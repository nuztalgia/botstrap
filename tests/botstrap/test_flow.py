"""Tests for the `botstrap.flow` module (`Botstrap` class)."""
from __future__ import annotations

import asyncio
import functools
import re
from argparse import ArgumentParser, Namespace
from string import ascii_uppercase
from typing import Any, Callable, Coroutine, Final, TypeVar, cast

import pytest

from botstrap import Botstrap, CliColors, Option
from botstrap.internal import Metadata, Token

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])

_DUMMY_TOKEN_VALUE: Final[str] = f"abcdefghijklmnopqrstuvwx.123456.{ascii_uppercase}-"


class MockBot:
    def __init__(self, **options: Any) -> None:
        for option_name, option_value in options.items():
            setattr(self, option_name, option_value)
        if self.__module__ == "discord.client":
            assert isinstance(getattr(self, "intents"), MockIntents)

    def event(self, coroutine: Coro) -> Coro:
        setattr(self, coroutine.__name__, coroutine)
        return coroutine


class MockIntents:
    @classmethod
    def default(cls) -> MockIntents:
        return cls()


@pytest.fixture
def retrieve_active_token(
    monkeypatch,
    created_token_uids: list[str],
    registered_token_uids: list[str],
    allow_token_creation: bool,
    allow_token_registration: bool,
) -> Callable[[], str | None]:
    botstrap = Botstrap()

    for token_uid in created_token_uids:
        Token(botstrap, token_uid).write(_DUMMY_TOKEN_VALUE)

    for token_uid in registered_token_uids:
        botstrap.register_token(token_uid)

    def _parse_args(_: Any) -> Namespace:
        args = {"token": registered_token_uids[0]} if registered_token_uids else {}
        return Namespace(**args)

    def _retrieve_active_token() -> str | None:
        return botstrap.retrieve_active_token(
            allow_token_creation=allow_token_creation,
            allow_token_registration=allow_token_registration,
        )

    monkeypatch.setattr(ArgumentParser, "parse_args", _parse_args)
    return _retrieve_active_token


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
    "created_token_uids, registered_token_uids, "
    "allow_token_creation, allow_token_registration, expected",
    [
        ([], [], False, False, RuntimeError),
        (["default"], [], False, False, RuntimeError),
        (["prod"], ["dev", "prod"], False, False, None),
        ([], [], False, True, None),
        (["dev", "prod"], ["default"], False, True, None),
        ([], [], True, True, 0),
    ],
)
def test_retrieve_active_token_fail(
    monkeypatch,
    retrieve_active_token,
    created_token_uids: list[str],
    registered_token_uids: list[str],
    allow_token_creation: bool,
    allow_token_registration: bool,
    expected: Any,
) -> None:
    def interrupt() -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)

    if isinstance(expected, int):
        with pytest.raises(SystemExit) as system_exit:
            retrieve_active_token()
        assert system_exit.value.code == expected
    elif not expected:
        assert retrieve_active_token() is None
    else:
        with pytest.raises(expected):
            retrieve_active_token()


@pytest.mark.parametrize(
    "created_token_uids, registered_token_uids, "
    "allow_token_creation, allow_token_registration",
    [
        ([], [], True, True),
        ([], ["dev"], True, False),
        (["prod"], ["dev"], True, False),
        (["dev"], ["dev", "prod"], False, False),
    ],
)
def test_retrieve_active_token_success(
    monkeypatch,
    retrieve_active_token,
    created_token_uids: list[str],
    registered_token_uids: list[str],
    allow_token_creation: bool,
    allow_token_registration: bool,
) -> None:
    def mock_resolve(token: Token, resolve_allow_token_creation: bool) -> str | None:
        assert resolve_allow_token_creation == allow_token_creation
        if allow_token_creation or (token.uid in created_token_uids):
            return _DUMMY_TOKEN_VALUE
        return None

    monkeypatch.setattr("botstrap.internal.tokens.Token.resolve", mock_resolve)
    assert retrieve_active_token() == _DUMMY_TOKEN_VALUE


@pytest.mark.parametrize(
    "bot_class, options, active_token_value, meta_bot_class_info, expected_error",
    [
        ("", {}, None, None, AssertionError),
        ("", {}, _DUMMY_TOKEN_VALUE, None, RuntimeError),
        ("", {}, _DUMMY_TOKEN_VALUE, ("an.imaginary.Class", "run", False), ImportError),
        (123, {}, _DUMMY_TOKEN_VALUE, None, TypeError),
    ],
)
def test_run_bot_fail(
    monkeypatch,
    bot_class: str | type,
    options: dict[str, Any],
    active_token_value: str | None,
    meta_bot_class_info: tuple[str, str, bool] | None,
    expected_error: Any,
) -> None:
    def mock_get_bot_class_info() -> tuple[str, str, bool]:
        if meta_bot_class_info:
            return meta_bot_class_info
        raise RuntimeError

    def mock_import_class(_: str) -> None:
        raise ImportError

    monkeypatch.setattr(Metadata, "get_bot_class_info", mock_get_bot_class_info)
    monkeypatch.setattr(Metadata, "import_class", mock_import_class)
    monkeypatch.setattr(Token, "resolve", lambda *_: active_token_value)
    monkeypatch.setattr(ArgumentParser, "parse_args", lambda _: Namespace())

    with pytest.raises(expected_error):
        assert Botstrap().run_bot(
            bot_class, **options
        )  # type: ignore[func-returns-value]


@pytest.mark.parametrize(
    "override_bot_class_name, options, expected_output",
    [
        (None, {}, r'^\nbot: default: Attempting to log in.*\n\n.*as "MockBot"\.\n\n$'),
        (("discord.client", "Client"), {}, r'Successfully logged in as "Client"\.\n+$'),
        (
            ("discord", "Bot"),
            {"run_method_name": "start", "init_with_token": True},
            normal_output := r"^\nbot: default: Attempting to log in to Discord\.\.\.\n"
            r'\nbot: default: Successfully logged in as "([A-Za-z]*Bot|Client)"\.\n\n+',
        ),
        (
            None,
            {"run_method_name": "walk", "exception_on_run": KeyboardInterrupt},
            normal_output + r"Received a keyboard interrupt\. Exiting process\.\n\n$",
        ),
        (
            ("hikari", "GatewayBot"),
            {"exception_on_run": type("UnauthorizedError", (Exception,), {})},
            normal_output + r"bot: error: Failed to log in\. .* Exiting process\.\n+$",
        ),
        (
            ("discord.client", "Client"),
            {"exception_on_run": type("LoginFailure", (Exception,), {})},
            normal_output + r".* sure your bot token is configured properly\..*\.\n\n$",
        ),
        (None, {"init_with_token": True, "exception_on_run": Exception}, normal_output),
    ],
)
def test_run_bot_success(
    capsys,
    monkeypatch,
    override_bot_class_name: tuple[str, str] | None,
    options: dict[str, Any],
    expected_output: str,
) -> None:
    if override_bot_class_name:
        module_name, class_name = override_bot_class_name
        MockBot.__module__ = module_name
        MockBot.__name__ = class_name

    run_method_name = options.get("run_method_name", "run")
    init_with_token = options.get("init_with_token", False)

    exception_on_run = options.get("exception_on_run")
    handled_exceptions = ("KeyboardInterrupt", "LoginFailure", "UnauthorizedError")

    def mock_run_bot(bot: MockBot, token: str | None = None) -> None:
        assert getattr(bot, "token") if init_with_token else token
        if on_connect := getattr(bot, "on_connect", None):
            asyncio.run(on_connect())
        if exception := getattr(bot, "exception_on_run", None):
            raise exception

    monkeypatch.setattr(MockBot, run_method_name, mock_run_bot, raising=False)
    monkeypatch.setattr(Metadata, "import_class", lambda *_: MockIntents)
    monkeypatch.setattr(Token, "resolve", lambda *_: _DUMMY_TOKEN_VALUE)
    monkeypatch.setattr(ArgumentParser, "parse_args", lambda _: Namespace())

    botstrap = Botstrap("bot", colors=CliColors.off())
    run_bot = functools.partial(botstrap.run_bot, MockBot, **options)

    if not exception_on_run:
        run_bot()
    elif exception_on_run.__name__ in handled_exceptions:
        with pytest.raises(SystemExit) as system_exit:
            run_bot()
        expected_exit_code = 0 if (exception_on_run == KeyboardInterrupt) else 1
        assert system_exit.value.code == expected_exit_code
    else:
        with pytest.raises(exception_on_run):
            run_bot()

    assert re.search(expected_output, capsys.readouterr().out, re.DOTALL)

    if override_bot_class_name:  # Restore original names.
        MockBot.__module__ = __name__
        MockBot.__name__ = "MockBot"
