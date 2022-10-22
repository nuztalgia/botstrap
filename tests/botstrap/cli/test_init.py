"""Tests for the `botstrap.cli.init` module."""
from __future__ import annotations

import functools
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Final

import pytest

from botstrap import CliColors
from botstrap.cli import init, utils
from botstrap.internal import Metadata
from tests.conftest import CliAction, generate_random_text

_REPO_ROOT: Final[Path] = (Path(__file__) / "../../../..").resolve()
_TEMPLATE_REGEX: Final[re.Pattern] = re.compile(r"\${\w+}")


class MockHTTPResponse:
    def __init__(self, url: str, timeout: int) -> None:
        relative_file = re.sub(r"https://.*/main/", "", url)
        self.read = (_REPO_ROOT / relative_file).read_bytes
        assert timeout in range(5, 20)


class MockPopen:
    def __init__(
        self, mock_stdout: list[str], args: str | list[str], **options: Any
    ) -> None:
        self.stdout = [f"{line}\n" for line in mock_stdout]
        self.returncode = 1  # Must call communicate() to set to 0 (indicating success).

        assert " ".join(args) == "pip install -e ."
        assert isinstance(options["cwd"], Path)
        assert options["stderr"] == subprocess.DEVNULL
        assert options["stdout"] == subprocess.PIPE
        assert options["universal_newlines"]

    def communicate(self) -> None:
        self.returncode = 0


@pytest.fixture
def initializer(monkeypatch, tmp_path, discord_lib: str) -> init.BotstrapInitializer:
    monkeypatch.chdir(tmp_path)
    return init.BotstrapInitializer(CliColors.off(), discord_lib)


@pytest.fixture(autouse=True)
def discord_lib() -> str:
    return "DISCORD_LIB"


@pytest.mark.parametrize(
    "discord_lib, args, expected_output",
    [
        (None, [], r"^$"),
        ("discord.py", [], r"^\nPreparing to initialize a new discord\.py bot\.\n"),
        ("disnake", [], r"disnake bot\.\nget_bot_info\n self\.discord_lib='disnake'\n"),
        ("hikari", ["MyBot"], r"='hikari'\n bot_name='MyBot'\n slugify_bot_name=True"),
        ("discord-py-interactions", ["bot", True], r"='bot'\n slugify_bot_name=False"),
        ("naff", ["bot2", True], r"='naff'\n bot_name='bot2'\n slugify_bot_name=False"),
        ("nextcord", ["bot_3", True, False], r"name='bot_3'\n slug.+=False\n+Received"),
        ("py-cord", [], r"Received a keyboard interrupt. Exiting initialization.\n\n$"),
    ],
)
def test_initialize_bot_args(
    capsys, monkeypatch, discord_lib: str | None, args: list[Any], expected_output: str
) -> None:
    def mock_get_bot_info(
        self: init.BotstrapInitializer, bot_name: str, slugify_bot_name: bool
    ) -> None:
        print(f"get_bot_info\n {self.discord_lib=}\n {bot_name=}\n {slugify_bot_name=}")
        raise KeyboardInterrupt

    monkeypatch.setattr(init.BotstrapInitializer, "_get_bot_info", mock_get_bot_info)
    monkeypatch.setattr(init, "get_discord_lib", lambda _: discord_lib)

    assert init.initialize_bot(*args) == 1
    assert re.search(expected_output, capsys.readouterr().out, re.DOTALL)


@pytest.mark.parametrize(
    "args, relative_bot_dir, can_init_git, can_init_files, can_install_bot, expected",
    [
        (("bot", True, True), ".", False, True, True, (1, "^Using existing directory")),
        (("b-t", True, True), "dir", False, True, True, (1, "^Creating new directory")),
        (("abc", True, True), ".", True, False, True, (1, r"^No files were created\.")),
        (("x_y_", True, True), ".", True, True, False, (0, r" from this directory\.$")),
        (("z", True, True), "bot-dir", True, True, False, (0, " from the bot-dir dir")),
        (("z", True, True), "", True, True, True, (0, r"command from any directory\.")),
        (("aaa", True, True), "bb", True, True, True, (0, r"the aaa command.+any dir")),
        (("bot-123", True, True), ".", True, True, True, (0, "the bot-123 command")),
        (("Bot__123", True, True), ".", True, True, True, (0, "the bot-123 command")),
        (("Bot__123", False, True), ".", True, True, True, (0, "the Bot__123 command")),
        (("BOT_4", True, False), "", True, True, True, (0, "the python -m bot4 comm")),
        (("BOT_4", False, False), "", True, True, True, (0, "the python -m bot4 comm")),
    ],
)
def test_initializer_run(
    capsys,
    monkeypatch,
    tmp_path,
    initializer,
    args: tuple[str, bool, bool],
    relative_bot_dir: str,
    can_init_git: bool,
    can_init_files: bool,
    can_install_bot: bool,
    expected: tuple[int, str],
) -> None:
    bot_name, slugify_bot_name, install_bot = args
    expected_result, expected_final_output_pattern = expected

    bot_name = utils.slugify(bot_name) if slugify_bot_name else bot_name
    bot_dir = (tmp_path / relative_bot_dir).resolve()

    def mock_init_all_files(_bot_dir: Path, _bot_name: str, _bot_package: str) -> bool:
        assert _bot_dir == bot_dir
        assert _bot_name == bot_name
        assert re.fullmatch(r"[a-z0-9]+", _bot_package)
        return can_init_files

    def mock_install_bot(_bot_dir: Path, _bot_name: str) -> bool:
        assert install_bot
        assert _bot_dir == bot_dir
        assert _bot_name == bot_name
        return can_install_bot

    monkeypatch.setattr(initializer, "_get_bot_info", lambda *_: (bot_name, bot_dir))
    monkeypatch.setattr(init, "initialize_git", lambda *_: can_init_git)
    monkeypatch.setattr(initializer, "_initialize_all_files", mock_init_all_files)
    monkeypatch.setattr(initializer, "_install_bot", mock_install_bot)

    assert initializer.run(*args) == expected_result

    final_output = next(s for s in reversed(capsys.readouterr().out.split("\n")) if s)
    assert re.search(expected_final_output_pattern, final_output)


@pytest.mark.parametrize(
    "args, cli_actions, expected",
    [
        (
            ("bot-1", False),
            CliAction.list((r"^  - Provided.+: 'bot-1'\.\n  - Using name as-is", "y")),
            ("bot-1", "bot-1"),
        ),
        (
            ("bot-2", True),
            CliAction.list((r"^  -.+bot name: 'bot-2'\.\n  - Using name as-is", "yes")),
            ("bot-2", "bot-2"),
        ),
        (
            ("Test__Bot", False),
            CliAction.list(
                (r"^  - Provided bot name: 'Test__Bot'\.\n  - Using name as-is", "nah"),
                (r"h\n\nWill create bot files in: .+Is this correct\? If .+: $", "YES"),
            ),
            ("Test__Bot", "."),
        ),
        (
            ("Test__Bot", True),
            CliAction.list(
                (r": 'Test__Bot'\.\n.+: 'Test__Bot' -> 'test-bot'.+disable.+'-s'", "Y"),
            ),
            ("test-bot", "test-bot"),
        ),
        (
            ("", True),
            CliAction.list(
                (r"^  - Bot name not provided.+\n  - Using slugified bot name: ", "y"),
            ),
            ("", "."),
        ),
        (
            ("", True),
            CliAction.list(
                (r"not provided\. Using directory name: .+Is this correct\?.+: $", "N"),
                (r"N\n\nWill create bot files in: .+Is this correct\?.+: $", "nopers"),
                (r"enter the name of the directory.+to create your bot: $", "tmp_file"),
                (r"e\nERROR: tmp_file .+existing file.+ different name\? .+: $", "yes"),
                (r"enter the name of the directory.+to create your bot: $", "test_bot"),
                (r"Will create bot files in: .+test_bot\nIs this correct\?.+: $", "y"),
            ),
            ("", "test_bot"),
        ),
    ],
)
def test_initializer_get_bot_info(
    mock_get_input,
    tmp_path,
    initializer: init.BotstrapInitializer,
    args: tuple[str, bool],
    cli_actions: list[CliAction],
    expected: tuple[str, str],
) -> None:
    (tmp_path / "tmp_file").touch()
    expected_name, expected_relative_dir = expected
    bot_name, bot_dir = initializer._get_bot_info(*args)
    assert bot_name == (expected_name or utils.slugify(tmp_path.name))
    assert bot_dir == (tmp_path / expected_relative_dir).resolve()


def test_initializer_initialize_all_files_fail(
    monkeypatch, tmp_path, initializer
) -> None:
    monkeypatch.setattr(Metadata, "get_package_info", lambda _: {"version": "1.0.0"})
    monkeypatch.setattr(init, "_RAW_REPO_URL", "http://raw.githubusercontent.com/")
    with pytest.raises(ValueError):
        initializer._initialize_all_files(tmp_path, "test-bot", "testbot")


@pytest.mark.parametrize(
    "discord_lib, package_version, bot_name, bot_package, extra_file, existing_files",
    [
        ("discord.py", "", "testbot", "testbot", "cogs/example.py", []),
        ("disnake", "", "test-bot-2", "testbot2", "cogs/example.py", [".gitignore"]),
        ("hikari", "", "bot3", "bot3", "bot.py", [".gitignore", "bot3/__init__.py"]),
        ("discord-py-interactions", "", "bot-4", "bot4", "extensions/example.py", []),
        ("naff", "", "TestBot", "testbot", "extensions/example.py", [".gitattributes"]),
        ("nextcord", "1.0", "Test_Bot_6", "testbot6", "cogs/example.py", ["README.md"]),
        ("py-cord", "2022.10.20", "test-bot-7", "testbot7", "cogs/example.py", []),
    ],
)
def test_initializer_initialize_all_files_success(
    capsys,
    monkeypatch,
    tmp_path,
    initializer: init.BotstrapInitializer,
    discord_lib: str,
    package_version: str,
    bot_name: str,
    bot_package: str,
    extra_file: str,
    existing_files: list[str],
) -> None:
    mock_package_info = {"version": package_version}
    monkeypatch.setattr(Metadata, "get_package_info", lambda _: mock_package_info)
    monkeypatch.setattr(init, "urlopen", MockHTTPResponse)

    for existing_file in existing_files:
        (tmp_path / existing_file).parent.mkdir(exist_ok=True)
        (tmp_path / existing_file).touch()

    expected_file_names = (
        ".gitattributes",
        ".gitignore",
        "README.md",
        "pyproject.toml",
        f"{bot_package}/__init__.py",
        f"{bot_package}/__main__.py",
        f"{bot_package}/{extra_file}",
    )
    expected_pyproject_lines = (
        f'name = "{bot_name}"',
        'readme = "README.md"',
        'requires-python = ">=3.10"',
        f'{bot_name} = "{bot_package}.__main__:main"',
        f'version = {{ attr = "{bot_package}.VERSION" }}',
        *(
            [
                f'  "botstrap == {package_version}",',
                f'  "{discord_lib} == {package_version}",',
            ]
            if package_version
            else ['  "botstrap",', f'  "{discord_lib}",']
        ),
    )

    initializer._initialize_all_files(tmp_path, bot_name, bot_package)
    output_text = capsys.readouterr().out.replace("\\", "/")
    output_files = {p.relative_to(tmp_path) for p in tmp_path.rglob("*") if p.is_file()}
    assert output_files == {Path(file_name) for file_name in expected_file_names}

    for file_name in expected_file_names:
        file_contents = Path(file_name).read_text()

        if file_name == "pyproject.toml":
            for expected_line in expected_pyproject_lines:
                assert f"{expected_line}\n" in file_contents

        if file_name in existing_files:
            expected_text = f"Skipping file {file_name} because it already exists.\n"
            expected_empty_contents = True
        else:
            expected_text = f"Creating file: {file_name}\n"
            expected_empty_contents = False

        assert expected_text in output_text
        assert (not file_contents) == expected_empty_contents
        assert not _TEMPLATE_REGEX.search(file_contents)  # All placeholders filled in.


def test_initializer_install_bot(capsys, monkeypatch, tmp_path, initializer) -> None:
    mock_sha = generate_random_text(length=49, chars="0123456789abcdef")
    mock_stdout = [
        "Obtaining file:///C:/Windows/Paths/Are/Fun/test-bot",
        "  Installing build dependencies: started",
        "  Installing build dependencies: finished with status 'done'",
        "  Preparing editable metadata (pyproject.toml): started",
        "  Preparing editable metadata (pyproject.toml): finished with status 'donezo'",
        "Requirement already satisfied: botstrap==0.3.0 in /irrelevant/path",
        "Building wheels for collected packages: test-bot",
        f"  Created wheel for test-bot: sha256={mock_sha}0",
        f"  Stored in directory: /path/to/wheel/{mock_sha}",
        "Successfully built test-bot",
        "Installing collected packages: test-bot",
        "Successfully installed test-bot-1.0.0",
    ]

    monkeypatch.setattr(subprocess, "Popen", functools.partial(MockPopen, mock_stdout))
    monkeypatch.setattr(sys, "prefix", sys.base_prefix)
    monkeypatch.setattr(shutil, "which", lambda cmd: cmd)

    assert initializer._install_bot(tmp_path, "test-bot")
    assert capsys.readouterr().out == (
        "Setting up a global editable installation of test-bot...\n\n"
        "Obtaining file: C:/Windows/Paths/Are/Fun/test-bot\n"
        "  Installing build dependencies... done.\n"
        "  Preparing editable metadata (pyproject.toml)... donezo.\n"
        "Building wheels for collected packages: test-bot\n"
        f"  Stored in directory: /path/to/wheel/{mock_sha}\n"
        "Successfully built test-bot!\n\n"
        "Installing collected packages: test-bot\n"
        "Successfully installed test-bot-1.0.0!\n\n"
    )
