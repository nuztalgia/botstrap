"""Tests for the `botstrap.internal.metadata` module."""
from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any, Final

import pytest

from botstrap.internal import Metadata

_SCRIPT_EXEC_DIR: Final[Path] = Path(".")
_FILE_PARENT_DIR: Final[Path] = Path(__file__) / ".."

_EXISTING_PACKAGE_NAME: Final[str] = "existing_package"


class MockMetadata:
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def json(self) -> dict[str, str]:
        if self.name == _EXISTING_PACKAGE_NAME:
            return {"name": self.name}
        else:
            raise PackageNotFoundError


def mock_main_module(monkeypatch, **kwargs: Any) -> None:
    for name, value in kwargs.items():
        monkeypatch.setattr(
            sys.modules["__main__"], f"__{name}__", value, raising=(name != "requires")
        )


@pytest.fixture
def mock_packages(monkeypatch, packages: dict[str, list[str]]) -> None:
    monkeypatch.setattr(
        "botstrap.internal.metadata.packages_distributions", lambda: packages
    )


@pytest.mark.parametrize(
    "packages",
    [
        {},
        {"pkg_name": ["dist-name"]},
        {"a": ["a"], "b": ["b"], "c": ["c"], "d": ["d", "e", "f"]},
        {"discord": ["nextcord"], "pycord": ["py-cord"]},
    ],
)
def test_get_bot_class_info_fail(mock_packages, packages: dict[str, list[str]]) -> None:
    expected = r"^Cannot automatically determine the class to use for the Discord bot.$"
    with pytest.raises(RuntimeError, match=expected):
        Metadata.get_bot_class_info()


@pytest.mark.parametrize(
    "packages, expected",
    [
        ({"discord": ["discord.py"]}, ("discord.Client", "run", False)),
        ({"discord": ["py-cord"]}, ("discord.Bot", "run", False)),
        (
            {"disnake": ["disnake"]},
            ("disnake.ext.commands.InteractionBot", "run", False),
        ),
        ({"hikari": ["hikari"]}, ("hikari.GatewayBot", "run", True)),
        (
            {"interactions": ["discord-py-interactions"]},
            ("interactions.Client", "start", True),
        ),
        ({"naff": ["naff"]}, ("naff.Client", "start", False)),
        (
            {"discord": ["nextcord"], "nextcord": ["nextcord"]},
            ("nextcord.ext.commands.Bot", "run", False),
        ),
        (
            {"discord": ["nextcord", "py-cord"], "disnake": ["disnake"]},
            ("discord.Bot", "run", False),
        ),
    ],
)
def test_get_bot_class_info_success(
    mock_packages, packages: dict[str, list[str]], expected: tuple[str, str, bool]
) -> None:
    bot_class_info = Metadata.get_bot_class_info()
    assert bot_class_info.qualified_name == expected[0]
    assert bot_class_info.run_method_name == expected[1]
    assert bot_class_info.init_with_token == expected[2]


@pytest.mark.parametrize(
    "main_module_file, sys_argv, expected_parent_dir",
    [
        ("", [], _SCRIPT_EXEC_DIR),
        (False, [__file__], _FILE_PARENT_DIR),
        (None, ["a confounding arg", __file__], _SCRIPT_EXEC_DIR),
        (0, [__file__, "an irrelevant arg", "and another one"], _FILE_PARENT_DIR),
        ([], [f"a {__file__} that does not exist! \\o/"], _SCRIPT_EXEC_DIR),
        (__file__, [], _FILE_PARENT_DIR),
        (Path(__file__).parent, ["arbitrary arg"], _FILE_PARENT_DIR / ".."),
    ],
)
def test_get_default_keys_dir(
    monkeypatch, main_module_file: Any, sys_argv: list[str], expected_parent_dir: Path
) -> None:
    mock_main_module(monkeypatch, file=main_module_file)
    monkeypatch.setattr(sys, "argv", sys_argv)
    expected_keys_dir = (expected_parent_dir / ".botstrap_keys").resolve()
    assert Metadata.get_default_keys_dir() == expected_keys_dir


@pytest.mark.parametrize(
    "package_name, main_module_package, main_module_requires, expect_result",
    [
        ("", "", "", False),
        (_EXISTING_PACKAGE_NAME, "irrelevant_package", "irrelevant_requires", True),
        ("", _EXISTING_PACKAGE_NAME, "", True),
        ("", "", _EXISTING_PACKAGE_NAME, True),
        ("bad_package", _EXISTING_PACKAGE_NAME, _EXISTING_PACKAGE_NAME, False),
        ("", "another_bad_package", _EXISTING_PACKAGE_NAME, False),
    ],
)
def test_get_package_info(
    monkeypatch,
    package_name: str,
    main_module_package: str,
    main_module_requires: str,
    expect_result: bool,
) -> None:
    mock_main_module(
        monkeypatch, package=main_module_package, requires=main_module_requires
    )
    monkeypatch.setattr("botstrap.internal.metadata.metadata", MockMetadata)
    package_info = Metadata.get_package_info(package_name)
    assert package_info == ({"name": _EXISTING_PACKAGE_NAME} if expect_result else {})
