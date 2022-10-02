"""Tests for the `botstrap.internal.metadata` module."""
from __future__ import annotations

import sys
from functools import partial
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from types import ModuleType
from typing import Any, Final

import pytest

from botstrap.internal import Metadata

_SCRIPT_EXEC_DIR: Final[Path] = Path(".")
_FILE_PARENT_DIR: Final[Path] = Path(__file__) / ".."

_FILE_NAME: Final[str] = Path(__file__).name
_PARENT_DIR_NAME: Final[str] = _FILE_PARENT_DIR.resolve().name

_EXISTING_PACKAGE_NAME: Final[str] = "existing_package"
_EXISTING_PACKAGE_INFO: Final[dict[str, str]] = {"name": _EXISTING_PACKAGE_NAME}


class MockEntryPoints:
    def __init__(self, console_scripts: list[str], *, group: str = "") -> None:
        if group == "console_scripts":
            self.names = console_scripts
        else:
            raise ValueError


class MockMetadata:
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def json(self) -> dict[str, str]:
        if self.name == _EXISTING_PACKAGE_NAME:
            return _EXISTING_PACKAGE_INFO
        else:
            raise PackageNotFoundError


@pytest.fixture
def mock_import_module(
    monkeypatch, module_name: str, class_name: str, attr_value: Any
) -> None:
    def mock_import(_: Any) -> ModuleType:
        mock_module = ModuleType(module_name)
        monkeypatch.setattr(mock_module, class_name, attr_value, raising=False)
        return mock_module

    monkeypatch.setattr("botstrap.internal.metadata.import_module", mock_import)


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
    monkeypatch.setattr(sys.modules["__main__"], "__file__", main_module_file)
    monkeypatch.setattr(sys, "argv", sys_argv)
    expected_keys_dir = (expected_parent_dir / ".botstrap_keys").resolve()
    assert Metadata.get_default_keys_dir() == expected_keys_dir


@pytest.mark.parametrize(
    "package_name, main_module_package, main_module_requires, expected",
    [
        ("", "", "", {}),
        (_EXISTING_PACKAGE_NAME, "any_pkg", "any_reqs", _EXISTING_PACKAGE_INFO),
        ("", _EXISTING_PACKAGE_NAME, "", _EXISTING_PACKAGE_INFO),
        ("", "", _EXISTING_PACKAGE_NAME, _EXISTING_PACKAGE_INFO),
        ("bad_package", _EXISTING_PACKAGE_NAME, _EXISTING_PACKAGE_NAME, {}),
        ("", "another_bad_package", _EXISTING_PACKAGE_NAME, {}),
    ],
)
def test_get_package_info(
    monkeypatch,
    package_name: str,
    main_module_package: str,
    main_module_requires: str,
    expected: dict[str, str | list[str]],
) -> None:
    monkeypatch.setattr("botstrap.internal.metadata.metadata", MockMetadata)
    monkeypatch.setattr(sys.modules["__main__"], "__package__", main_module_package)
    monkeypatch.setattr(
        sys.modules["__main__"], "__requires__", main_module_requires, raising=False
    )
    assert Metadata.get_package_info(package_name) == expected


@pytest.mark.parametrize(
    "program_name, sys_executable, sys_argv, console_scripts, expected",
    [
        ("", "", [], [], [""]),
        ("", "python4", [], [], ["python4"]),
        ("", "python", ["bot.py"], [], ["python", "bot.py"]),
        ("bot", "any-python", [], ["bot"], ["bot"]),
        ("bot1", "py", ["-m", "bot2"], ["bot", "bot1"], ["bot1"]),
        ("bot2", "py", ["-m", "bot2"], ["bot", "bot1"], ["py", "-m", "bot2"]),
        ("", "py", [__file__], [], ["py", _FILE_NAME]),
        ("", "py", [__file__, "-h", "--more-options"], [], ["py", _FILE_NAME]),
        ("", "py", ["-m", __file__, "-h"], ["bot", "bot1"], ["py", "-m", _FILE_NAME]),
        ("", "py", ["non-option", "-m", __file__, "-h"], [], ["py", "non-option"]),
    ],
)
def test_get_program_command(
    monkeypatch,
    program_name: str,
    sys_executable: str,
    sys_argv: list[str],
    console_scripts: list[str],
    expected: list[str],
) -> None:
    mock_entry_points = partial(MockEntryPoints, console_scripts)
    monkeypatch.setattr("botstrap.internal.metadata.entry_points", mock_entry_points)
    monkeypatch.setattr(sys, "executable", sys_executable)
    monkeypatch.setattr(sys, "orig_argv", [sys_executable, *sys_argv])
    assert Metadata.get_program_command(program_name) == expected


@pytest.mark.parametrize(
    "main_file_path, package_info, expected",
    [
        (None, _EXISTING_PACKAGE_INFO, _EXISTING_PACKAGE_NAME),
        (Path(__file__), _EXISTING_PACKAGE_INFO, _EXISTING_PACKAGE_NAME),
        (Path(__file__), {}, _FILE_NAME),
        (_FILE_PARENT_DIR, {}, _PARENT_DIR_NAME),
        (_FILE_PARENT_DIR / "src" / "main.py", {}, _PARENT_DIR_NAME),
        (_FILE_PARENT_DIR / "foo" / "src" / "main.py", {}, "foo"),
        (Path("foo/src/bar/main.py"), {}, "bar"),
        (Path("foo/bar/baz/SRC/mAiN.py"), {}, "baz"),
        (Path("foo/bar/baz/src/main/main.py"), {}, None),
    ],
)
def test_guess_program_name(
    monkeypatch,
    main_file_path: Path | None,
    package_info: dict[str, str | list[str]],
    expected: str | None,
) -> None:
    for target, mock in {
        "get_main_file_path": lambda: main_file_path,
        "get_package_info": lambda: package_info,
    }.items():
        monkeypatch.setattr(f"botstrap.internal.metadata.Metadata.{target}", mock)
    monkeypatch.setattr("pathlib.Path.exists", lambda _: True)
    assert Metadata.guess_program_name() == expected


@pytest.mark.parametrize(
    "module_name, class_name, attr_value",
    [("mdl", "cls", None), ("pkg.mdl", "cls", 0), ("a.b.c", "mdl.cls", MockMetadata)],
)
def test_import_class_fail(
    mock_import_module, module_name: str, class_name: str, attr_value: Any
) -> None:
    qualified_class_name = f"{module_name}.{class_name}"
    with pytest.raises(ImportError, match=qualified_class_name.replace(".", r"\.")):
        Metadata.import_class(qualified_class_name)


@pytest.mark.parametrize(
    "module_name, class_name, attr_value",
    [("mdl", "cls", str), ("pkg.mdl", "cls", int), ("a.b.c.mdl", "cls", MockMetadata)],
)
def test_import_class_success(
    mock_import_module, module_name: str, class_name: str, attr_value: type
) -> None:
    assert Metadata.import_class(f"{module_name}.{class_name}") == attr_value
