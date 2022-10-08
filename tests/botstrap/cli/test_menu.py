"""Tests for the `botstrap.cli.menu` module."""
from __future__ import annotations

import re
from typing import Sequence

import pytest

from botstrap import CliColors, cli


def mock_detect_bot_tokens(  # Properly tested in `test_scan.py`.
    paths: Sequence[str] | None, quiet: bool, verbose: bool, colors: CliColors
) -> None:
    assert (paths is None) or isinstance(paths, Sequence)
    assert isinstance(quiet, bool)
    assert isinstance(verbose, bool)
    assert isinstance(colors, CliColors)
    print("detect_bot_tokens succeeded!")


@pytest.fixture(autouse=True)
def setup(monkeypatch, tmp_path, sys_argv: list[str]) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["botstrap", *sys_argv])
    monkeypatch.setattr("webbrowser.open", lambda url: print(f"webbrowser: {url}"))
    monkeypatch.setattr("botstrap.cli.menu.detect_bot_tokens", mock_detect_bot_tokens)


@pytest.mark.parametrize(
    "sys_argv, expected",
    [
        ([], r"Usage:.+\n  botstrap .+<command>.+\[options\].+\n.+Commands"),  # Colors.
        (
            ["-n"],
            help_text := r"^[ _]+\n[ _|]+\n.+version .+Usage:\n  botstrap <command> \["
            r"options\]\n\nCommands:\n.+General Options:\n  -h.+\n  -n.+ output.\n\n$",
        ),
        (["-h", "-n"], help_text),
        (["help", "-h", "-n"], help_text),
        (["docs"], r"^webbrowser: https://botstrap.readthedocs.io/en/latest/api/?\n$"),
        (["docs", "-h", "-n"], help_text),
        (["repo"], r"^webbrowser: https://github.com/nuztalgia/botstrap/?\n$"),
        (["repo", "-h", "-n"], help_text),
        (["site"], r"^webbrowser: https://botstrap.readthedocs.io(/en/latest)?/?\n$"),
        (["site", "-h", "-n"], help_text),
        (["scan"], "detect_bot_tokens succeeded!"),
    ],
)
def test_main(capsys, sys_argv: list[str], expected: str) -> None:
    with pytest.raises(SystemExit) as system_exit:
        cli.main()
    assert system_exit.value.code == 0
    assert re.search(expected, capsys.readouterr().out, re.DOTALL)
