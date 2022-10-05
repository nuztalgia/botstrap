"""Tests for the `botstrap.internal.argstrap` module."""
from __future__ import annotations

from typing import Any, Final

import pytest

from botstrap import CliColors, Option
from botstrap.internal import Argstrap, CliSession, Metadata, Token

_CLI_SESSION: Final[CliSession] = CliSession("CLI", CliColors.off())


@pytest.fixture(autouse=True)
def mock_metadata(monkeypatch, meta_prog: list[str], meta_desc: str | None) -> None:
    monkeypatch.setattr(Metadata, "get_program_command", lambda _: meta_prog)
    monkeypatch.setattr(Metadata, "get_package_info", lambda _: {"summary": meta_desc})


@pytest.mark.parametrize(
    "token_args, description, version, custom_options, meta_prog, meta_desc, "
    "expected_prog, expected_usage, expected_desc",
    [
        (
            [],
            None,
            None,
            {},
            ["python", "bot0.py"],
            None,
            "bot0.py",
            "bot0.py [-t] [--help]",
            '  Run "python bot0.py" with no parameters to start the bot.',
        ),
        (
            [("default",)],
            None,
            "v1.0.0",
            {"beta": Option(flag=True)},
            ["python", "-m", "bot1.py"],
            "A bot.",
            "bot1.py",
            "bot1.py [-b] [-t] [-v] [--help]",
            '  A bot.\n  Run "python -m bot1.py" with no parameters to start the bot.',
        ),
        (
            [("dev",), ("prod", True)],
            "A bot.",
            "",
            {"a": Option(flag=True, help=Option.HIDE_HELP), "b": Option(flag=True)},
            ["bot2"],
            None,
            "bot2",
            "bot2 [-b] [-t] [--help] [<token id>]",
            '  A bot.\n  Run "bot2" with no parameters to start the bot in dev mode.',
        ),
        (
            [("bot",)],
            None,
            None,
            {
                "hoo": Option(default=2, help="An option that can't be abbreviated."),
                "bar": Option(default="bar", help="An option that can be abbreviated."),
                "baz": Option(default=3.14, help="Option 'bar' stole my abbreviation!"),
            },
            ["python3", "-m", "bot3"],
            None,
            "bot3",
            "bot3 [--hoo <int>] [-b <str>] [--baz <float>] [-t] [--help]",
            '  Run "python3 -m bot3" with no parameters to start the bot.',
        ),
        (
            [("default",), ("admin", True), ("super_duper_secret_admin", True)],
            None,
            "4.0",
            {
                "status": Option(),
                "mentions": Option(flag=True),
                "loglevel": Option(default=3, choices=range(1, 5)),
                "alpha": Option(flag=True, help=Option.HIDE_HELP),
            },
            ["py4", "-m", "bot4"],
            None,
            "bot4",
            "bot4 [-s <str>] [-m] [-l <int>] [-t] [-v] [--help] [<token id>]",
            '  Run "py4 -m bot4" with no parameters to start the bot in default mode.',
        ),
    ],
)
def test_init_success(
    token_args: list[tuple[Any, ...]],
    description: str | None,
    version: str | None,
    custom_options: dict[str, Option],
    meta_prog: list[str],
    meta_desc: str | None,
    expected_prog: str,
    expected_usage: str,
    expected_desc: str,
) -> None:
    tokens = [Token(_CLI_SESSION, *args) for args in token_args]
    argstrap = Argstrap(_CLI_SESSION, tokens, description, version, **custom_options)
    assert argstrap.cli == _CLI_SESSION
    assert argstrap.prog == expected_prog
    assert argstrap.usage == expected_usage
    assert argstrap.description == expected_desc
