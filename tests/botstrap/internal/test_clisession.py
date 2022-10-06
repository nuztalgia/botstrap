"""Tests for the `botstrap.internal.clisession` module."""
from __future__ import annotations

from dataclasses import asdict
from typing import Callable, Final, cast

import pytest

from botstrap import CliColors, CliStrings, Color
from botstrap.internal import CliSession

_CLI_DEFAULT: Final[CliSession] = CliSession("default")
_CLI_NO_COLOR: Final[CliSession] = CliSession("no-color", CliColors.off())

_CLI_PRESETS: Final[tuple[CliSession, CliSession]] = (_CLI_DEFAULT, _CLI_NO_COLOR)


@pytest.fixture
def mock_input(monkeypatch, response: str) -> None:
    def print_and_return_response() -> str:
        print(response)
        return response

    monkeypatch.setattr("builtins.input", print_and_return_response)


@pytest.mark.parametrize(
    "name, kwargs",
    [
        ("", {}),
        ("abc", {"colors": CliColors.off()}),
        ("cli", {"strings": CliStrings.compact()}),
        ("xyz", {"colors": CliColors(Color.cyan), "strings": CliStrings.default()}),
    ],
)
def test_properties(name: str, kwargs: dict[str, CliColors | CliStrings]) -> None:
    cli = CliSession(name, **kwargs)  # type: ignore[arg-type]
    assert cli.name == name
    assert asdict(cli.colors) == asdict(kwargs.get("colors", CliColors.default()))
    assert cli.strings == kwargs.get("strings", CliStrings.default())


@pytest.mark.parametrize("response", ["y", "Y", "yes", "YES", "yEs  ", " \t  YeS   \n"])
def test_confirm_or_exit_confirmed(capsys, mock_input, response: str) -> None:
    for cli in _CLI_PRESETS:
        cli.confirm_or_exit("Confirm?")
        assert capsys.readouterr().out == (
            f'Confirm? If so, type "{cli.colors.highlight("yes")}"'
            f' or "{cli.colors.highlight("y")}": {response}\n'
        )


@pytest.mark.parametrize("response", ["", "ye", "\n", "no", "N", "yeah", "k", "blargh"])
def test_confirm_or_exit_exited(capsys, mock_input, response: str) -> None:
    with pytest.raises(SystemExit) as system_exit:
        _CLI_NO_COLOR.confirm_or_exit("Confirm?")
    assert capsys.readouterr().out.endswith(
        "\n\nReceived a non-affirmative response. Exiting process.\n\n"
    )
    assert system_exit.value.code == 0


@pytest.mark.parametrize(
    "reason, is_error, expected_color",
    [
        ("", True, "N/A"),
        ("", False, "N/A"),
        ("Everything is on fire.", True, "error"),
        ("Received a keyboard interrupt.", False, "lowlight"),
    ],
)
def test_exit_process(capsys, reason: str, is_error: bool, expected_color: str) -> None:
    for cli in _CLI_PRESETS:
        with pytest.raises(SystemExit) as system_exit:
            if is_error:
                cli.exit_process(reason)  # Default value of `is_error` should be True.
            else:
                cli.exit_process(reason, is_error)
        if reason:
            colored_reason = getattr(cli.colors, expected_color)(reason)
            exiting_message = cli.colors.lowlight(cli.strings.m_exiting)
            assert capsys.readouterr().out == f"{colored_reason} {exiting_message}\n"
        else:
            assert capsys.readouterr().out == ""
        assert system_exit.value.code == (1 if is_error else 0)


@pytest.mark.parametrize(
    "prompt, response, format_input, expected",
    [
        ("Enter password", "01234567890123456789", None, "********************"),
        ("if you type in your pw, it will show as stars", "hunter2", str, "hunter2"),
        ("Enter a long password", "abcdefghijklmnopqrstuvwxyz0123456789", len, "36"),
        ("On Wednesdays, we wear", "pink", Color.pink, Color.pink("pink")),
    ],
)
def test_get_hidden_input(
    capsys,
    monkeypatch,
    prompt: str,
    response: str,
    format_input: Callable[[str], str] | None,
    expected: str,
) -> None:
    monkeypatch.setattr("getpass.getpass", lambda: response)
    monkeypatch.setattr("getpass.fallback_getpass", lambda *_: response)
    for cli in _CLI_PRESETS:
        cli.get_hidden_input(prompt, format_input)
        prompt = cli.colors.highlight(f"{prompt}:")
        hidden = cast(Callable, str if format_input else cli.colors.lowlight)(expected)
        assert capsys.readouterr().out == f"{prompt} \033[F\033[1A{prompt} {hidden}\n"


@pytest.mark.parametrize(
    "message, is_error, suppress_newline, expected",
    [
        ("", False, False, "$NAME: "),
        ("A regular message.", False, False, "$NAME: A regular message.\n"),
        ("An error!!!", True, False, "$NAME: error: An error!!!\n"),
        ("Logging in...", False, True, "$NAME: Logging in... "),
        ("LoginFailure:", True, True, "$NAME: error: LoginFailure: "),
    ],
)
def test_print_prefixed(
    capsys, message: str, is_error: bool, suppress_newline: bool, expected: str
) -> None:
    for cli in _CLI_PRESETS:
        cli.print_prefixed(message, is_error, suppress_newline)
        assert capsys.readouterr().out == expected.replace("$NAME", f"\n{cli.name}")
