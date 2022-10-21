"""Tests for the `botstrap.cli.utils` module."""
from __future__ import annotations

import re
import secrets
import string
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from botstrap.cli import utils
from botstrap.internal import Metadata
from tests.conftest import generate_random_text


@pytest.mark.parametrize(
    "installed_libs, expected",
    [
        ([], (None, r"\nERROR: You don't have any.+, then re-run this command\.\n\n$")),
        (["lib1", "lib2"], (None, r"\nERROR: You have multiple.+ this command\.\n\n$")),
        (["lib3"], ("lib3", r"^$")),
    ],
)
def test_get_discord_lib(
    capsys, monkeypatch, installed_libs: list[str], expected: tuple[str | None, str]
) -> None:
    monkeypatch.setattr(Metadata, "get_discord_libs", lambda: installed_libs)
    expected_result, expected_output_pattern = expected
    assert utils.get_discord_lib() == expected_result
    assert re.match(expected_output_pattern, capsys.readouterr().out, re.DOTALL)


@pytest.mark.parametrize(
    "discord_lib_id, expected",
    [
        ("", None),
        ("discord.py", None),
        ("discordpy", ("example_cog.py", "cogs/example.py")),
        ("disnake", ("example_cog.py", "cogs/example.py")),
        ("hikari", ("bot.py", "bot.py")),
        ("interactions", ("example_extension.py", "extensions/example.py")),
        ("naff", ("example_extension.py", "extensions/example.py")),
        ("nextcord", ("example_cog.py", "cogs/example.py")),
        ("pycord", ("example_cog.py", "cogs/example.py")),
        ("py-cord", None),
    ],
)
def test_get_lib_example(discord_lib_id: str, expected: tuple[str, str] | None) -> None:
    if expected:
        assert utils.get_lib_example(discord_lib_id) == expected
    else:
        with pytest.raises(RuntimeError):
            utils.get_lib_example(discord_lib_id)


@pytest.mark.slow
@pytest.mark.repeat(1)
def test_initialize_git(capsys, monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    (dir1 := tmp_path / "dir1").mkdir()
    (dir2 := tmp_path / "dir2").mkdir()

    def assert_init_success(input_path: Path, expected_output_prefix: str) -> None:
        assert utils.initialize_git(input_path) is True
        assert capsys.readouterr().out.startswith(expected_output_prefix)

    assert_init_success(dir1, "Initializing new Git repository.")
    assert_init_success(dir1, "Using existing Git repository.")
    assert_init_success(tmp_path, "Initializing new Git repository.")
    assert_init_success(dir2, "Using existing Git repository.")

    monkeypatch.setattr("shutil.which", lambda cmd: str(tmp_path / cmd))
    assert utils.initialize_git(tmp_path) is False
    assert re.match(
        r"^Initializing new Git repository\. \(.+\.git\)\n\nERROR: 'git init' failed\.",
        capsys.readouterr().out,
    )


@pytest.mark.parametrize(
    "file_contents, expected",
    [
        (string.printable, True),
        (secrets.token_bytes(128), False),
        (generate_random_text(1024), True),
        (secrets.token_bytes(1024), False),
        (generate_random_text(1024).encode() + secrets.token_bytes(1024), True),
        (secrets.token_bytes(1024) + generate_random_text(1024).encode(), False),
    ],
)
def test_is_text_file(
    monkeypatch, tmp_path, file_contents: str | bytes, expected: bool
) -> None:
    if isinstance(file_contents, str):
        file_contents = file_contents.encode()
    monkeypatch.chdir(tmp_path)
    (tmp_path / "file").write_bytes(file_contents)
    assert utils.is_text_file("file") == expected


@pytest.mark.parametrize(
    "args, stderr, expected",
    [
        (
            ("", "Git failed", "Is it installed / are you in a repo?"),
            "fatal: not a git repository (or any of the parent directories)",
            "ERROR: Git failed. Is it installed / are you in a repo?\n"
            "  └─ fatal: not a git repository (or any of the parent directories)\n",
        ),
        (
            ("\n", "Invalid path", "Must point to file(s) in the active repo."),
            "error: pathspec 'empty.txt' did not match any file(s) known to git\n"
            "Did you forget to 'git add'?",
            "\nERROR: Invalid path. Must point to file(s) in the active repo.\n  └─ "
            "error: pathspec 'empty.txt' did not match any file(s) known to git\n\n",
        ),
    ],
)
def test_print_error(capsys, args: tuple[str, ...], stderr: str, expected: str) -> None:
    line_spacing, summary, hint_text = args
    utils.print_error(line_spacing, summary, hint_text, stderr.encode())
    assert capsys.readouterr().out == expected


def test_git_unavailable(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("shutil.which", lambda cmd: str(tmp_path / cmd))
    git_process = utils.run_git()
    with pytest.raises(CalledProcessError):
        git_process.check_returncode()
    assert re.search(r": git \(executable\)$", git_process.stderr.decode())


@pytest.mark.slow
@pytest.mark.repeat(1)
def test_run_git(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "dir1" / "dir2").mkdir(parents=True)

    pre_init_process = utils.run_git("rev-parse", "--show-cdup", cwd="dir1/dir2")
    with pytest.raises(CalledProcessError):
        pre_init_process.check_returncode()

    init_process = utils.run_git("init")
    init_process.check_returncode()

    post_init_process = utils.run_git("rev-parse", "--show-cdup", cwd="dir1/dir2")
    post_init_process.check_returncode()
    assert post_init_process.stdout.decode().strip() == "../../"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Boring Example Name", "boring-example-name"),
        ("name_with_numbers123_456", "name-with-numbers123-456"),
        ("ALLCAPSName is confusing", "allcapsname-is-confusing"),
        ("---CamelCaseName-----AndDashes---", "camel-case-name-and-dashes"),
        ("a name with -more spaces- n -dashes-", "a-name-with-more-spaces-n-dashes"),
        ("-misc.punctuation,'chars:;and&stuff?!!", "misc-punctuation-chars-and-stuff"),
    ],
)
def test_slugify(text: str, expected: str) -> None:
    assert utils.slugify(text) == expected
