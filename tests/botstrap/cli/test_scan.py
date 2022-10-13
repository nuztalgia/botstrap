"""Tests for the `botstrap.cli.scan` module."""
from __future__ import annotations

import re
import secrets
import string
from subprocess import CalledProcessError
from typing import Any

import pytest

from botstrap import CliColors
from botstrap.cli import scan
from tests.conftest import generate_random_text, generate_random_token_value


@pytest.fixture(autouse=True)
def use_tmp_directory(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def init_repo_files(tmp_path) -> None:
    for i in range(3):
        (dir_path := tmp_path / f"dir{i + 1}").mkdir()
        for j in range(2 - i):
            (dir_path / f"file{j + 1}").touch()
    scan.run_git("init")


@pytest.mark.slow
@pytest.mark.repeat(1)
def test_detect_bot_tokens_fail(capsys) -> None:
    assert scan.detect_bot_tokens() == 1
    assert "Git command failed." in capsys.readouterr().out
    scan.run_git("init")
    assert scan.detect_bot_tokens("dir1") == 1
    assert "Invalid path." in capsys.readouterr().out


@pytest.mark.slow
@pytest.mark.repeat(1)
def test_detect_bot_tokens_success(capsys, tmp_path, init_repo_files) -> None:
    assert scan.detect_bot_tokens() == 0  # No tokens initially present.
    expected = "\nScanning 3 files...\n\nNo plaintext bot tokens detected.\n\n"
    assert capsys.readouterr().out == expected

    file1, file2 = (tmp_path / "dir3" / "file1"), (tmp_path / "file2")  # Tokens.
    file3 = tmp_path / "dir1" / "file3"  # Will not hold a token.

    file1.write_text(generate_random_token_value())
    file2.write_text(
        re.sub(r"^.+?\.", f"{string.printable[:24]}.", generate_random_token_value())
    )
    file3.write_text(
        re.sub(r"^.+?\.", f"{string.printable[:23]}.", generate_random_token_value())
    )

    assert scan.detect_bot_tokens(quiet=True) == 1
    expected = "Plaintext bot token(s) detected in:\n  - dir3/file1\n  - file2\n"
    assert capsys.readouterr().out == expected

    assert scan.detect_bot_tokens(["dir1", "dir3"], verbose=True) == 1
    assert capsys.readouterr().out == (
        "\nScanning 4 files...\n  1 dir1/file1\n  2 dir1/file2\n  3 dir1/file3"
        "\n  4 dir3/file1 [WARNING: Contains plaintext token.]\n\n"
        "Plaintext bot token(s) detected in:\n  - dir3/file1\n\n"
    )

    file1.write_text("No more token in this file!")

    assert scan.detect_bot_tokens(["dir1", "dir3"], quiet=True, verbose=True) == 0
    assert capsys.readouterr().out == ""  # `verbose` is ignored in favor of `quiet`.

    assert scan.detect_bot_tokens(quiet=True) == 1
    assert capsys.readouterr().out == "Plaintext bot token(s) detected in:\n  - file2\n"

    file2.unlink()  # Delete the other file that contained a token. No tokens left.

    assert scan.detect_bot_tokens(verbose=True) == 0
    assert capsys.readouterr().out == (
        "\nScanning 5 files...\n  1 dir1/file1\n  2 dir1/file2\n  3 dir1/file3\n"
        "  4 dir2/file1\n  5 dir3/file1\n\nNo plaintext bot tokens detected.\n\n"
    )


@pytest.mark.slow
@pytest.mark.repeat(1)
def test_list_files(init_repo_files) -> None:
    assert scan.list_files() == []
    assert scan.list_files("-o") == ["dir1/file1", "dir1/file2", "dir2/file1"]
    assert scan.list_files("-o", "*file1") == ["dir1/file1", "dir2/file1"]

    assert scan.list_files("-o", "*file2", cwd="dir2") == []
    with pytest.raises(CalledProcessError):
        assert scan.list_files("-o", "--error-unmatch", "*file2", cwd="dir2")


@pytest.mark.slow
@pytest.mark.repeat(1)
@pytest.mark.parametrize(
    "paths, cwd, expected",
    [
        ([], "", ["dir1/file1", "dir1/file2", "dir2/file1"]),
        ([], "dir3", []),
        ([], "dir1", ["file1", "file2"]),
        ([], "file2", (CalledProcessError, NotADirectoryError)),
        (["dir1"], "", ["dir1/file1", "dir1/file2"]),
        (["dir1/"], "", ["dir1/file1", "dir1/file2"]),
        (["dir1/*"], "", ["dir1/file1", "dir1/file2"]),
        (["file2"], "dir1", ["file2"]),
        (["file"], "dir1", CalledProcessError),
        (["file*"], "dir1", ["file1", "file2"]),
        (["dir2", "dir1"], "", ["dir1/file1", "dir1/file2", "dir2/file1"]),
        (["dir1"], "dir2", CalledProcessError),
    ],
)
def test_get_repo_files(
    init_repo_files, paths: list[str], cwd: str, expected: Any
) -> None:
    if isinstance(expected, list):
        assert scan.get_repo_files(paths, cwd) == expected
    else:
        with pytest.raises(expected):
            scan.get_repo_files(paths, cwd)


@pytest.mark.parametrize(
    "args, expected",
    [
        ((1, False), "\nScanning \x1b[36m\x1b[1m1 file\x1b[22m\x1b[39m...\n"),
        ((999, False), "\nScanning \x1b[36m\x1b[1m999 files\x1b[22m\x1b[39m...\n"),
        ((0, True), "\x1b[36m\x1b[1m\nScanning 0 files...\x1b[22m\x1b[39m\n"),
        ((1, True), "\x1b[36m\x1b[1m\nScanning 1 file...\x1b[22m\x1b[39m\n"),
    ],
)
def test_print_scan_header(capsys, args: tuple[int, bool], expected: str) -> None:
    file_count, verbose = args
    scan.print_scan_header(file_count, verbose, CliColors.default())
    assert capsys.readouterr().out == expected


@pytest.mark.parametrize(
    "args, file_contents, expected",
    [
        ((16, "empty.txt", CliColors.off(), 0), "", (False, "")),
        ((16, "empty.txt", CliColors.off(), 6), "", (False, "    16 empty.txt\n")),
        ((16, "empty.txt", CliColors.default(), 6), "", (False, "    16 empty.txt\n")),
        ((9, "f", CliColors.off(), 0), secrets.token_bytes(256), (False, "")),
        (
            (9, "f", CliColors.off(), 1),
            secrets.token_bytes(256),
            (False, "9 f [SKIPPED: Not a text file.]\n"),
        ),
        (
            (9, "f", CliColors.default(), 1),
            secrets.token_bytes(256),
            (False, "9 \x1b[30m\x1b[1mf [SKIPPED: Not a text file.]\x1b[22m\x1b[39m\n"),
        ),
        (
            (42, "empty.txt", CliColors.off(), 3),
            token_value := generate_random_token_value(),
            (True, warning := " 42 empty.txt [WARNING: Contains plaintext token.]\n"),
        ),
        ((42, "empty.txt", CliColors.off(), 0), token_value * 5, (True, "")),
        (
            (42, "empty.txt", CliColors.default(), 3),
            generate_random_text(1024) + token_value,
            (True, f" 42 \x1b[33m\x1b[1m{warning[4:-1]}\x1b[22m\x1b[39m\n"),
        ),
    ],
)
def test_scan_file_for_token(
    capsys,
    tmp_path,
    args: tuple[int, str, CliColors, int],
    file_contents: str | bytes,
    expected: tuple[bool, str],
) -> None:
    if isinstance(file_contents, str):
        file_contents = file_contents.encode()
    (tmp_path / args[1]).write_bytes(file_contents)

    expected_result, expected_output = expected
    assert scan.scan_file_for_token(*args) == expected_result
    assert capsys.readouterr().out == expected_output
