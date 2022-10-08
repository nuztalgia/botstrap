"""Tests for the `botstrap.internal.secrets` module."""
from __future__ import annotations

import re
import string
from base64 import urlsafe_b64encode
from pathlib import Path
from typing import Any

import pytest

from botstrap import Color
from botstrap.internal import Secret


@pytest.fixture(autouse=True)
def mock_storage_directory(
    monkeypatch,
    tmp_path,
    storage_directory: str | Path | None,
    setup_path_method: str | None,
) -> str | Path | None:
    storage_path = tmp_path / (storage_directory or ".botstrap_keys")

    if isinstance(storage_directory, str):
        monkeypatch.setattr(Path, "__new__", lambda _, name: tmp_path / name)

    if setup_path_method and (setup := getattr(storage_path, setup_path_method)):
        setup_kwargs = {"exist_ok": False}
        if setup_path_method == "mkdir":
            setup_kwargs["parents"] = True
        setup(**setup_kwargs)

    return storage_path if isinstance(storage_directory, Path) else storage_directory


@pytest.fixture(autouse=True)
def storage_directory() -> None:
    return None


@pytest.fixture(autouse=True)
def setup_path_method() -> None:
    return None


@pytest.mark.parametrize(
    "uid, storage_directory, setup_path_method",
    [
        ("", None, None),
        ("1_bot", None, None),
        ("non-identifier-uid", None, None),
        ("bot", None, "touch"),
        ("bot_1", "keys n stuff", "touch"),
        ("_xX_b0t_Xx_", Path("KEY_STORAGE"), "touch"),
    ],
)
def test_init_fail(
    mock_storage_directory,
    uid: str,
    storage_directory: str | Path | None,
    setup_path_method: str | None,
) -> None:
    with pytest.raises(ValueError):
        Secret(uid, storage_directory=mock_storage_directory)


@pytest.mark.parametrize(
    (
        "uid, requires_password, display_name, storage_directory, setup_path_method, "
        "expected_display_name, expected_min_pw_length"
    ),
    [
        ("bot", False, None, None, None, "bot", 0),
        ("bot_1", False, None, "keys n stuff", "mkdir", "bot_1", 0),
        ("bot", False, Color.pink("bot"), Path(""), None, Color.pink("bot"), 0),
        ("_xX_b0t_Xx_", True, "botX", None, "mkdir", "botX", 8),
        ("a1b2c3", True, "", "secrets", None, "a1b2c3", 8),
        ("_", True, "___", Path("definitely/nothing/here"), "mkdir", "___", 8),
    ],
)
def test_init_success(
    mock_storage_directory,
    tmp_path,
    uid: str,
    requires_password: bool,
    display_name: str | None,
    storage_directory: str | Path | None,
    setup_path_method: str | None,
    expected_display_name: str,
    expected_min_pw_length: int,
) -> None:
    secret = Secret(uid, requires_password, display_name, mock_storage_directory)
    assert secret.uid == uid
    assert secret.requires_password == requires_password
    assert secret.display_name == expected_display_name
    assert str(secret) == expected_display_name
    assert str(
        (storage_directory or ".botstrap_keys")
        if (storage_directory != Path("."))
        else tmp_path
    ) in str(secret.storage_directory)
    assert secret.storage_directory.is_relative_to(tmp_path)
    assert secret.storage_directory.is_dir()
    assert secret.file_path == secret.storage_directory / f".{uid}.content.key"
    assert secret.min_pw_length == expected_min_pw_length


@pytest.mark.parametrize(
    "valid_pattern, text_to_validate, expected",
    [
        (None, "", True),
        (".*", "", True),
        (r".*\..*", string.punctuation, True),
        (None, "lorem ipsum", True),
        ("", "lorem ipsum", True),
        ("l", "lorem ipsum", False),
        ("l.*", "lorem ipsum", True),
        ("l.*", ".lorem ipsum", False),
        (re.compile("a.*"), string.ascii_lowercase, True),
        (re.compile("a"), string.ascii_lowercase, False),
        (re.compile("a").match, string.ascii_lowercase, True),
        (re.compile("bc").match, string.ascii_lowercase, False),
        (re.compile("bc").search, string.ascii_lowercase, True),
        (lambda s: len(s) == 10, "123456789", False),
        (lambda s: len(s) == 10, "0123456789", True),
    ],
)
def test_validate(valid_pattern: Any, text_to_validate: str, expected: bool) -> None:
    secret = Secret(uid="_", valid_pattern=valid_pattern)
    assert secret.validate(text_to_validate) == expected


@pytest.mark.parametrize(
    "create_dir_for_key, error_on_file_path", [("content", True), ("fernet", False)]
)
def test_invalid_key_files(create_dir_for_key: str, error_on_file_path: bool) -> None:
    secret = Secret("unused_uid")
    (secret.storage_directory / f".{secret.uid}.{create_dir_for_key}.key").mkdir()
    if error_on_file_path:
        with pytest.raises(ValueError):
            assert secret.file_path
    with pytest.raises(ValueError):
        secret.clear()


@pytest.mark.parametrize(
    "requires_password, valid_pattern, data, password, expected_error, error_pattern",
    [
        (False, None, "abc", 123, ValueError, "Unexpectedly received a password"),
        (False, None, "abc", "xyz", ValueError, "Unexpectedly received a password"),
        (True, None, "abc", None, ValueError, "Password is required to read/write"),
        (True, None, "abc", "", ValueError, "Password is required to read/write"),
        (True, None, "abc", 123, TypeError, "Password type .* 'str'>, not .* 'int'>"),
        (True, None, "abc", True, TypeError, "Password type .* 'str'>, not .* 'bool'>"),
        (True, None, "", "a", ValueError, "Password must be at least 8 characters"),
        (True, None, "", "abcdefg", ValueError, "Password .* at least 8 characters"),
        (False, ".+", "", "", (ValueError, FileNotFoundError), r"(invalid data|\.key)"),
    ],
)
def test_file_ops_fail(
    requires_password: bool,
    valid_pattern: Any,
    data: str,
    password: Any,
    expected_error: Any,
    error_pattern: str,
) -> None:
    secret = Secret("unused_uid", requires_password, valid_pattern=valid_pattern)
    with pytest.raises(expected_error, match=error_pattern):
        secret.write(data, password)
    with pytest.raises(expected_error, match=error_pattern):
        secret.read(password)


@pytest.mark.slow
@pytest.mark.repeat(1)
@pytest.mark.parametrize(
    "uid, requires_password, valid_pattern, data, password",
    [
        ("_", False, None, "", None),
        ("abc", True, "\\w+", "abc123", "hunter22"),
        ("x1", True, re.compile(".*", re.DOTALL), string.printable, string.punctuation),
    ],
)
def test_file_ops_success(
    uid: str, requires_password: bool, valid_pattern: Any, data: str, password: Any
) -> None:
    secret = Secret(uid, requires_password, valid_pattern=valid_pattern)
    encoded_data = data.encode(), data.encode("ascii"), urlsafe_b64encode(data.encode())

    def count_stored_files() -> int:
        return len(list(secret.storage_directory.iterdir()))

    assert count_stored_files() == 0
    secret.clear()  # No effect; no error.
    assert count_stored_files() == 0

    secret.write(data, password)  # Encrypt.
    assert count_stored_files() == 2

    for qualifier in ("content", "fernet"):
        file_path = secret.storage_directory / f".{uid}.{qualifier}.key"
        assert file_path.is_file()
        file_data = file_path.read_bytes()
        for unencrypted_data in encoded_data:
            assert (not unencrypted_data) or (unencrypted_data not in file_data)
            assert file_data and (file_data not in unencrypted_data)

    assert secret.read(password) == data  # Decrypt & check.

    secret.write(data * 2, password)  # Overwrite.
    assert count_stored_files() == 2
    assert secret.read(password) == data * 2

    secret.clear()  # Delete.
    assert count_stored_files() == 0
    with pytest.raises(FileNotFoundError):
        secret.read(password)
