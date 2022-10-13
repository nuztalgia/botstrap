"""Tests for the `botstrap.cli.utils` module."""
from __future__ import annotations

import re
import secrets
import string
from subprocess import CalledProcessError

import pytest

from botstrap.cli import utils
from tests.conftest import generate_random_text


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
