"""Tests for the `botstrap.internal.argstrap` module."""
from __future__ import annotations

import re
from string import ascii_uppercase
from typing import Any, Final, cast

import pytest

from botstrap import CliColors, Option
from botstrap.internal import Argstrap, CliSession, Token
from tests.conftest import CliAction

_CLI_SESSION: Final[CliSession] = CliSession("CLI", CliColors.off())
_DUMMY_TOKEN_VALUE: Final[str] = f"abcdefghijklmnopqrstuvwx.123456.{ascii_uppercase}-"


@pytest.mark.parametrize(
    "custom_options, expected_error, error_pattern",
    [
        ({1: None}, TypeError, "keywords must be strings"),
        ({"_": None}, ValueError, "^Invalid command-line argument name: ''.$"),
        ({"h": None}, ValueError, "^Invalid command-line argument name: 'h'.$"),
        ({"help": None}, ValueError, "^'help' is not a unique command-line arg name.$"),
        ({"halp": None}, TypeError, "^Invalid type for custom option 'halp'. Expected"),
        ({"halp": Option(), "_halp": Option()}, ValueError, "not a unique .* arg name"),
    ],
)
def test_init_fail(
    custom_options: dict[str, Option], expected_error: Any, error_pattern: str
) -> None:
    with pytest.raises(expected_error, match=error_pattern):
        Argstrap(_CLI_SESSION, [], "", "", **custom_options)


@pytest.mark.parametrize(
    "token_uids, description, version, custom_options, meta_prog, meta_desc, "
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
            ["default"],
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
            ["dev", "prod"],
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
            ["bot"],
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
            ["default", "admin", "super_duper_secret_admin"],
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
    mock_get_metadata,
    token_uids: list[str],
    description: str | None,
    version: str | None,
    custom_options: dict[str, Option],
    meta_prog: list[str],
    meta_desc: str | None,
    expected_prog: str,
    expected_usage: str,
    expected_desc: str,
) -> None:
    tokens = [Token(_CLI_SESSION, token_uid) for token_uid in token_uids]
    argstrap = Argstrap(_CLI_SESSION, tokens, description, version, **custom_options)
    assert argstrap.cli == _CLI_SESSION
    assert argstrap.prog == expected_prog
    assert argstrap.usage == expected_usage
    assert argstrap.description == expected_desc


@pytest.mark.slow
@pytest.mark.parametrize(
    "token_uids, version, custom_options, sys_argv, expected, expected_output",
    [
        ([], None, {}, [], "default", {}),
        ([], None, {}, ["--help"], 0, r"\n  -h, --help +Display this help message\.\n"),
        ([], None, {}, ["-t"], 0, "manage_tokens"),
        ([], None, {}, ["-v"], 2, "error: unrecognized arguments: -v"),
        ([], "", {}, ["-v"], 2, "error: unrecognized arguments: -v"),
        ([], "v1.0.0", {}, ["-v"], 0, r"^v1\.0\.0\n$"),
        ([], "v1.0.1", {"v": Option()}, [], "default", {"v": ""}),
        ([], "v1.0.1", {"v": Option()}, ["-v"], 2, "-v: expected one argument"),
        ([], "v1.0.1", {"v": Option()}, ["-v", "foobar"], "default", {"v": "foobar"}),
        ([], "v1.0.1", {"v": Option()}, ["--version"], 0, r"^v1\.0\.1\n$"),
        ([], None, {"hoo": Option(flag=True)}, [], "default", {"hoo": False}),
        ([], None, {"hoo": Option(flag=True)}, ["--hoo"], "default", {"hoo": True}),
        ([], None, {"hoo": Option(flag=True)}, ["-h"], 0, "Display this help message"),
        ([], "version 2.0", {}, ["-t", "-h", "-v"], 0, "Display this help message"),
        ([], "version 2.0", {}, ["-t", "-v"], 0, r"^version 2\.0$"),
        ([], None, {"too": Option(default=1)}, ["-t", "2"], "default", {"too": 2}),
        ([], None, {"too": Option(default=1)}, ["-t", "2", "--tokens"], 0, "manage_t"),
        (["dev"], None, {}, [], "dev", {}),
        (["dev", "prod"], None, {}, [], "dev", {}),
        (["dev", "prod"], None, {}, ["prod"], "prod", {}),
        (["dev", "prod"], None, {}, ["-t", "prod", "-h"], 0, "Display this help mess"),
        (["dev", "prod"], None, {}, ["-t", "prod"], 0, "manage_tokens"),
        (["dev", "prod"], None, {}, ["pro"], 2, " <token id>: invalid choice: 'pro' "),
        (["dev", "prod"], "v3", {"foo": Option(flag=True)}, [], "dev", {"foo": False}),
        (
            ["dev", "prod"],
            "v3",
            {"foo": Option(flag=True)},
            ["prod", "-f"],
            "prod",
            {"foo": True},
        ),
        (
            ["dev", "prod", "admin", "super_secret"],
            "v3",
            {
                "float": Option(default=3.14),
                "foo": Option(flag=True),
                "fun_level": Option(default=0, choices=range(100)),
            },
            ["--fun-level", "99", "super_secret", "-f", "6.28"],
            "super_secret",
            {"float": 6.28, "foo": False, "fun_level": 99},
        ),
    ],
)
def test_parse_bot_args(
    capsys,
    monkeypatch,
    token_uids: list[str],
    version: str | None,
    custom_options: dict[str, Option],
    sys_argv: list[str],
    expected: int | str,
    expected_output: str | dict[str, str | int | float],
) -> None:
    tokens = [Token(_CLI_SESSION, token_uid) for token_uid in token_uids]
    argstrap = Argstrap(_CLI_SESSION, tokens, "", version, **custom_options)

    def mock_manage_tokens() -> None:
        print("manage_tokens")
        raise KeyboardInterrupt

    monkeypatch.setattr(argstrap, "manage_tokens", mock_manage_tokens)
    monkeypatch.setattr("sys.argv", ["bot.py", *sys_argv])

    if isinstance(expected, int):
        with pytest.raises(SystemExit) as system_exit:
            argstrap.parse_bot_args()
        output = capsys.readouterr()
        assert re.search(cast(str, expected_output), output.out + output.err, re.DOTALL)
        assert system_exit.value.code == expected
    else:
        token, results = argstrap.parse_bot_args()
        assert token.uid == expected
        assert vars(results) == expected_output


@pytest.mark.slow
@pytest.mark.parametrize(
    "saved_token_names, cli_actions, expected",
    [
        ([], [], r"^\nCLI: You currently don't have any saved bot tokens\.\n\n$"),
        (
            ["dev"],
            CliAction.list((r"^\nCLI: .* tokens saved:\n  1\. dev ->.*\.dev\.\*", "N")),
            r": N\n\nReceived a non-affirmative response. Exiting process.\n\n$",
        ),
        (
            [("dev", "development")],
            CliAction.list(
                (r"^\nCLI: .* tokens saved:\n  1\. development ->.*\.dev\.\*", "y"),
                ("Please enter the number next to the token you want to delete: ", "1"),
            ),
            r"delete: 1\n\nToken successfully deleted\.\n\n"
            r"CLI: You currently don't have any saved bot tokens\.\n\n$",
        ),
        (
            [("dev", "development"), ("prod", "production"), "staging"],
            CliAction.list(
                (
                    r"^\nCLI: You currently have the following bot tokens saved:\n"
                    r"  1\. development ->  .*\.botstrap_keys.\.dev\.\*\n"
                    r"  2\. production  ->  .*\.botstrap_keys.\.prod\.\*\n"
                    r"  3\. staging     ->  .*\.botstrap_keys.\.staging\.\*\n",
                    "Y",
                ),
                ("Please enter the number next to the token you want to delete: ", "4"),
                (
                    r": 4\n\nThat number doesn't match any of the above tokens\. "
                    r'\(Expected "1", "2", or "3"\.\)\n\nWould you like to try again\?',
                    "yes",
                ),
                ("Please enter the number next to the token you want to delete: ", "2"),
                (
                    r"delete: 2\n\nToken successfully deleted\.\n\n"
                    r"CLI: You currently have the following bot tokens saved:\n"
                    r"  1\. development ->  .*\.botstrap_keys.\.dev\.\*\n"
                    r"  2\. staging     ->  .*\.botstrap_keys.\.staging\.\*\n",
                    "nah",
                ),
            ),
            r": nah\n\nReceived a non-affirmative response. Exiting process.\n\n$",
        ),
    ],
)
def test_manage_tokens(
    capsys,
    mock_get_input,
    saved_token_names: list[str | tuple[str, str]],
    cli_actions: list[CliAction],
    expected: str,
) -> None:
    tokens = []

    for token_name in saved_token_names:
        if isinstance(token_name, str):
            token = Token(_CLI_SESSION, token_name)
        else:
            token = Token(_CLI_SESSION, token_name[0], False, token_name[1])
        token.write(_DUMMY_TOKEN_VALUE)
        tokens.append(token)

    with pytest.raises(SystemExit) as system_exit:
        Argstrap(_CLI_SESSION, tokens).manage_tokens()

    assert re.search(expected, capsys.readouterr().out, re.DOTALL)
    assert system_exit.value.code == 0
