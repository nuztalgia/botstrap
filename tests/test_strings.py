from string import Template
from typing import Any, Callable, Final

import pytest

from botstrap import CliStrings, Color

_DEFAULT_STRINGS: Final[CliStrings] = CliStrings.default()
_COMPACT_STRINGS: Final[CliStrings] = CliStrings.compact()


@pytest.mark.parametrize(
    "name, expected",
    [
        ("h_help", "Display this help message."),
        ("m_exit_by_choice", "Received a non-affirmative response."),
        ("m_exit_by_interrupt", "Received a keyboard interrupt."),
        ("m_exiting", "Exiting process."),
        ("m_login", "${token}: Attempting to log in to Discord..."),
        ("p_create_cue", "Please enter a password for your ${token} bot token."),
        (
            "p_create_info",
            "To keep your bot token extra safe, it must be encrypted with a password. "
            "This password won't be stored anywhere. It will only be used as a key to "
            "decrypt your token every time you run your bot in ${token} mode.",
        ),
        (
            "h_token_id",
            "The ID of the token to use to run the bot. "
            "Valid options are ${token_ids}.",
        ),
        ("m_login_success", '${token}: Successfully logged in as "${bot_id}".'),
        ("m_affirm_responses", ("yes", "y")),
    ],
)
def test_compact_strings(name: str, expected: str | tuple[str, ...]) -> None:
    match (value := getattr(_COMPACT_STRINGS, name)):
        case str() | tuple():
            assert value == expected
        case Template():
            assert value.template == expected
        case _:
            pytest.fail(f"Invalid attribute type for '{name}': {type(value)}")


@pytest.mark.parametrize(
    "choices, kwargs, expected",
    [
        ([], {}, ""),
        (["a"], {}, '"a"'),
        (["a"], {"quote_choices": False}, "a"),
        (["a", "b"], {}, '"a" or "b"'),
        (["a", "b"], {"conjunction": _DEFAULT_STRINGS.m_conj_and}, '"a" and "b"'),
        (["a", "b", "c"], {}, '"a", "b", or "c"'),
        (["a", "b", "c"], {"conjunction": "", "separator": "/"}, '"a"/"b"/"c"'),
        (["a", "b", "c", "d", "f"], {"quote_choices": False}, "a, b, c, d, or f"),
        (["g"] * 2, {"quote_choices": False, "conjunction": "", "separator": ""}, "gg"),
        (
            ["duck"] * 9 + ["GOOSE"],
            {"conjunction": "", "separator": " "},
            '"duck" "duck" "duck" "duck" "duck" "duck" "duck" "duck" "duck" "GOOSE"',
        ),
        (
            ["red", "blue", "yellow"],
            {"format_choice": lambda choice: getattr(Color, choice)(choice)},
            '"\x1b[31m\x1b[1mred\x1b[22m\x1b[39m", "\x1b[34m\x1b[1mblue\x1b[22m\x1b[39m'
            '", or "\x1b[33m\x1b[1myellow\x1b[22m\x1b[39m"',
        ),
    ],
)
def test_join_choices(
    choices: list[str], kwargs: dict[str, Any], expected: str
) -> None:
    for preset_strings in (_DEFAULT_STRINGS, _COMPACT_STRINGS):
        assert preset_strings.join_choices(choices, **kwargs) == expected


@pytest.mark.parametrize(
    "strings, format_response, expected",
    [
        (_COMPACT_STRINGS, None, 'If so, type "yes" or "y"'),
        (_DEFAULT_STRINGS, None, 'If so, type "yes" or "y"'),
        (
            _DEFAULT_STRINGS,
            Color.green,
            'If so, type "\x1b[32m\x1b[1myes\x1b[22m\x1b[39m"'
            ' or "\x1b[32m\x1b[1my\x1b[22m\x1b[39m"',
        ),
        (
            CliStrings(m_affirm_responses=("yes", "yeah", "yep")),
            None,
            'If so, type "yes", "yeah", or "yep"',
        ),
        (
            CliStrings(
                m_affirm_cue="If you're happy and you know it,",
                m_affirm_responses=("clap your hands",),
            ),
            Color.pink,
            f'If you\'re happy and you know it, "{Color.pink("clap your hands")}"',
        ),
    ],
)
def test_affirmation_prompt(
    strings: CliStrings, format_response: Callable[[str], str] | None, expected: str
) -> None:
    assert strings.get_affirmation_prompt(format_response) == expected
