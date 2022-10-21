"""Tests for the `botstrap.cli.menu` module."""
from __future__ import annotations

import re
from collections.abc import Sequence

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


def mock_initialize_bot(  # Properly tested in `test_init.py`.
    name: str, no_slugs: bool, no_install: bool, colors: CliColors
) -> None:
    assert isinstance(name, str)
    assert isinstance(no_slugs, bool)
    assert isinstance(no_install, bool)
    assert isinstance(colors, CliColors)
    print("initialize_bot succeeded!")


@pytest.fixture(autouse=True)
def setup(monkeypatch, tmp_path, sys_argv: list[str]) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["botstrap", *sys_argv])
    monkeypatch.setattr("webbrowser.open", lambda url: print(f"webbrowser: {url}"))
    monkeypatch.setattr("botstrap.cli.menu.detect_bot_tokens", mock_detect_bot_tokens)
    monkeypatch.setattr("botstrap.cli.menu.initialize_bot", mock_initialize_bot)


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
        (["init"], "initialize_bot succeeded!"),
        (["init", "-h"], r"e:.+botstrap.+init.+\[name\] \[-s\] \[-i\].+\[-h\] \[-n\]"),
        (["scan"], "detect_bot_tokens succeeded!"),
        (["scan", "-h"], r"e:.+botstrap.+scan.+\[paths\] \[-q\] \[-v\].+\[-h\] \[-n\]"),
    ],
)
def test_main(capsys, sys_argv: list[str], expected: str) -> None:
    with pytest.raises(SystemExit) as system_exit:
        cli.main()
    assert system_exit.value.code == 0
    assert re.search(expected, capsys.readouterr().out, re.DOTALL)
