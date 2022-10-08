"""Tests for the `botstrap.internal.tokens` module."""
from __future__ import annotations

import re
import string
from secrets import choice
from typing import Callable, Final

import pytest

from botstrap import CliColors
from botstrap.internal import CliSession, Token
from tests.conftest import CliAction

_CLI_SESSION: Final[CliSession] = CliSession("CLI", CliColors.off())
_VALID_TOKEN_CHARS: Final[str] = string.ascii_letters + string.digits + "_-"


def generate_random_token_value() -> str:
    token = []
    for length in (24, 6, 27):
        token.append("".join(choice(_VALID_TOKEN_CHARS) for _ in range(length)))
    return ".".join(token)


def setup_resolve_token(
    *, requires_password: bool, allow_token_creation: bool
) -> Callable[[], str | None]:
    def resolve_token() -> str | None:
        token = Token(cli=_CLI_SESSION, uid="TEST", requires_password=requires_password)
        return token.resolve(allow_token_creation)

    return resolve_token


def test_default_token(tmp_path) -> None:
    token = Token.get_default(_CLI_SESSION)
    assert token.uid == "default"
    assert not token.requires_password
    assert token.display_name == "default"
    assert token.storage_directory == (tmp_path / ".botstrap_keys")
    assert token.cli == _CLI_SESSION


@pytest.mark.parametrize(
    "text_to_validate, expected",
    [
        ("", False),
        ("definitely.a.token", False),
        (f"abcdefghijklmnopqrstuvwx.123456.{string.ascii_uppercase}-", True),
        *[(generate_random_token_value(), True) for _ in range(5)],  # Fuzz testing.
    ],
)
def test_validate(text_to_validate: str, expected: bool) -> None:
    assert Token.get_default(_CLI_SESSION).validate(text_to_validate) == expected


@pytest.mark.slow
@pytest.mark.repeat(1)
@pytest.mark.parametrize(
    "resolve_token, cli_actions, expected",
    [
        (
            setup_resolve_token(requires_password=False, allow_token_creation=False),
            [],
            (None, r"^\nCLI: error: Keyfile for TEST bot token doesn't exist\.\n\n$"),
        ),
        (
            setup_resolve_token(requires_password=False, allow_token_creation=True),
            CliAction.list(
                (r"^\nCLI: .*don't have a saved TEST bot token\..*add one now\?", "n"),
            ),
            (0, r"\n\nReceived a non-affirmative response. Exiting process.\n\n$"),
        ),
        (
            setup_resolve_token(requires_password=False, allow_token_creation=True),
            CliAction.list(
                (r"^\nCLI: .*Would you like to add one now\?", "yes"),
                (r"enter your bot token.*\nBOT TOKEN: $", "invalid_bot_token", False),
            ),
            (1, r"That doesn't seem like a valid bot token\..*Exiting process.\n$"),
        ),
        (
            setup_resolve_token(requires_password=False, allow_token_creation=True),
            CliAction.list(
                (r"^\nCLI: .*Would you like to add one now\?", "yes"),
                (r"\nBOT TOKEN: $", new_token := generate_random_token_value(), False),
                (r"successfully encrypted and saved.*run your bot now\?", "YES"),
            ),
            (new_token, r" YES\n$"),
        ),
        (
            setup_resolve_token(requires_password=True, allow_token_creation=True),
            CliAction.list(
                (r"^\nCLI: .*Would you like to add one now\?", "Y"),
                (r"\nBOT TOKEN: $", generate_random_token_value(), False),
                (r"enter a password for your TEST bot token\.\nPASSWORD: $", "", False),
                (r"PASSWORD: \n+Your password must be at least 8 characters long", "n"),
            ),
            (0, r"\n\nReceived a non-affirmative response. Exiting process.\n\n$"),
        ),
        (
            setup_resolve_token(requires_password=True, allow_token_creation=True),
            CliAction.list(
                (r"^\nCLI: .*Would you like to add one now\?", "Y"),
                (r"\nBOT TOKEN: $", new_token := generate_random_token_value(), False),
                (r"enter a password.*\.\nPASSWORD: $", "12345678", False),
                (r"re-enter the same password again.*\nPASSWORD: $", "12345679", False),
                (r"password doesn't match your original password.*try again\?", "yes"),
                (r" yes\nPASSWORD: $", "12345678", False),
                (r" \*{8}\n\n.*encrypted and saved.*run your bot now\?", "y"),
            ),
            (new_token, r" y\n$"),
        ),
    ],
)
def test_resolve_new_token(
    capsys,
    mock_get_input,
    resolve_token: Callable[[], str | None],
    cli_actions: list[CliAction],
    expected: tuple[int | str | None, str],
) -> None:
    expected_result, expected_output_pattern = expected

    if isinstance(expected_result, int):
        with pytest.raises(SystemExit) as system_exit:
            resolve_token()
        assert system_exit.value.code == expected_result
    else:
        assert resolve_token() == expected_result

    assert re.search(expected_output_pattern, capsys.readouterr().out, re.DOTALL)


@pytest.mark.slow
@pytest.mark.repeat(1)
@pytest.mark.parametrize(
    "resolve_token, cli_actions, expected",
    [
        (
            setup_resolve_token(requires_password=False, allow_token_creation=True),
            CliAction.list(
                (r"add one now\?", "y"),
                (r"\nBOT TOKEN: $", new_token := generate_random_token_value(), False),
                (r"run your bot now\?", "y"),
            ),
            new_token,
        ),
        (
            setup_resolve_token(requires_password=True, allow_token_creation=True),
            (
                setup_password := CliAction.list(
                    (r"add one now\?", "y"),
                    (r"\nBOT TOKEN: $", new_token, False),
                    CliAction(r"\nPASSWORD: $", string.punctuation, False),
                    CliAction(r"\nPASSWORD: $", string.punctuation, False),
                    (r"run your bot now\?", "y"),
                )
            )
            + [CliAction(r"the password .* TEST bot token\.\nPASSWORD: $", "", False)],
            None,
        ),
        (
            setup_resolve_token(requires_password=True, allow_token_creation=True),
            setup_password + [CliAction(r"\nPASSWORD: $", "12345678", False)],
            None,
        ),
        (
            setup_resolve_token(requires_password=True, allow_token_creation=True),
            setup_password + [CliAction(r"\nPASSWORD: $", string.punctuation, False)],
            new_token,
        ),
    ],
)
def test_resolve_existing_token(
    mock_get_input,
    resolve_token: Callable[[], str | None],
    cli_actions: list[CliAction],
    expected: str | None,
) -> None:
    resolve_token()  # Create the token.
    assert resolve_token() == expected
