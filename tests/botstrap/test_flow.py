"""Tests for the `botstrap.flow` module (`Botstrap` class)."""
from __future__ import annotations

import re
from argparse import Namespace
from typing import Any, cast

import pytest

from botstrap import Botstrap, CliColors, Option


def test_register_token() -> None:
    botstrap = Botstrap()
    botstrap.register_token("dev")
    with pytest.raises(ValueError, match='A token with unique ID "dev" already exists'):
        botstrap.register_token("dev")
    botstrap.register_token("dev", allow_overwrites=True)  # No error.


@pytest.mark.parametrize(
    "desc, version, custom_options, meta_desc, sys_argv, expected",
    [
        (None, None, {}, None, [], {}),
        ("", "", {}, None, ["-t"], r"You currently don't have any saved bot tokens\."),
        ("", "", {}, None, ["-h"], r"usage: .* \[-t\] \[--help\]\n\n  Run.*bot.\n\n"),
        ("A bot!", None, {}, "zz", ["-h"], r"usage: .*\]\n\n  A bot!\n  Run.*bot.\n\n"),
        (None, None, {}, "A bot!", ["-h"], r"usage: .*\]\n\n  A bot!\n  Run.*bot.\n\n"),
        (None, "version 0.0.0.0.1", {}, None, ["-v"], r"^version (0\.){4}1\n$"),
        ("", "", {"foo": Option()}, None, ["-h"], r"usage:.*\[-f <str>\] \[-t\] \[--h"),
        ("", "", {"foo": Option()}, None, [], {"foo": ""}),
        ("", "", {"foo": Option()}, None, ["-f", "abcdef"], {"foo": "abcdef"}),
        (
            "A bot with lots of options.",
            "v2.0.0",
            test_options := {
                "loglevel": Option(default=2, choices=range(1, 5)),
                "status": Option(help="Text to show in the bot's Discord status."),
                "activity": Option(
                    default="playing",
                    choices=("streaming", "listening", "watching"),
                    help="The text preceding '--status'. Defaults to '%(default)s'.",
                ),
                "mentions": Option(flag=True, help="Allow the bot to @mention people."),
                "alpha": Option(flag=True, help=Option.HIDE_HELP),
            },
            "Just a bot.",
            ["-t", "-h", "-v"],
            r"^usage: .* \[-l <int>\] \[-s <str>\] \[-a <str>\] \[-m\] \[-t\] \[-v\] \["
            r"--help\]\n\n  A bot with lots of options\.\n  Run.*to start the bot\.\n",
        ),
        (
            "A bot with lots of options.",
            "v2.0.0",
            test_options,
            "Just a bot.",
            ["--alpha", "-a", "watching", "-s", "you."],
            {
                "loglevel": 2,
                "status": "you.",
                "activity": "watching",
                "mentions": False,
                "alpha": True,
            },
        ),
    ],
)
def test_parse_args(
    capsys,
    monkeypatch,
    mock_get_metadata,
    desc: str | None,
    version: str | None,
    custom_options: dict[str, Option],
    meta_desc: str | None,
    sys_argv: list[str],
    expected: str | dict[str, str | int | float],
) -> None:
    botstrap = Botstrap(desc=desc, version=version, colors=CliColors.off())
    monkeypatch.setattr("sys.argv", ["bot.py", *sys_argv])

    if isinstance(expected, str):
        with pytest.raises(SystemExit) as system_exit:
            botstrap.parse_args(**custom_options)
        assert re.search(cast(str, expected), capsys.readouterr().out, re.DOTALL)
        assert system_exit.value.code == 0
    else:
        assert vars(botstrap.parse_args(**custom_options)) == expected


@pytest.mark.parametrize(
    "allow_token_creation, allow_token_registration, expected",
    [(False, False, RuntimeError), (False, True, None), (True, True, 0)],
)
def test_retrieve_active_token_fail(
    monkeypatch,
    allow_token_creation: bool,
    allow_token_registration: bool,
    expected: Any,
) -> None:
    def interrupt() -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)
    monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda _: Namespace())

    def retrieve_active_token() -> str | None:
        return Botstrap().retrieve_active_token(
            allow_token_creation=allow_token_creation,
            allow_token_registration=allow_token_registration,
        )

    if isinstance(expected, int):
        with pytest.raises(SystemExit) as system_exit:
            retrieve_active_token()
        assert system_exit.value.code == expected
    elif not expected:
        assert retrieve_active_token() is None
    else:
        with pytest.raises(expected):
            retrieve_active_token()
