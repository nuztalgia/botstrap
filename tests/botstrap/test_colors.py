"""Tests for the `botstrap.colors` module (`Color` and `CliColors` classes)."""
from __future__ import annotations

from typing import Callable

import pytest

from botstrap import CliColors, Color


def get_color_func(name: str) -> Callable[[str], str]:
    return getattr(Color, name)


@pytest.mark.parametrize(
    "name, text, expected",
    [
        (color, f" {color} text ", f"\x1b[{code}m\x1b[1m {color} text \x1b[22m\x1b[39m")
        for code, color in enumerate(
            ["grey", "red", "green", "yellow", "blue", "pink", "cyan"], start=30
        )
    ],
)
def test_color_output(name: str, text: str, expected: str) -> None:
    assert get_color_func(name)(text) == expected


@pytest.mark.parametrize("name", ["black", "gray", "magenta"])
def test_color_nonexistent(name: str) -> None:
    with pytest.raises(AttributeError):
        get_color_func(name)


@pytest.mark.parametrize(
    "args, kwargs",
    [
        ([], {}),
        (["pink"], {}),
        (["cyan"], {"error": "pink"}),
        ([], {"highlight": "yellow", "lowlight": "cyan", "warning": "pink"}),
        (["green"], {"lowlight": "blue", "success": "yellow", "warning": "red"}),
    ],
)
def test_cli_colors_constructor(args: list[str], kwargs: dict[str, str]) -> None:
    cli_colors = CliColors(
        *[get_color_func(name) for name in args],
        **{name: get_color_func(value) for name, value in kwargs.items()},
    )
    assert cli_colors.primary == (get_color_func(args[0]) if args else str)
    for name, value in kwargs.items():
        assert getattr(cli_colors, name) == get_color_func(value)


@pytest.mark.parametrize(
    "preset, expected",
    [
        (
            "default",
            default_values := {
                "primary": "",
                "error": "red",
                "highlight": "cyan",
                "lowlight": "grey",
                "success": "green",
                "warning": "yellow",
            },
        ),
        ("off", {name: "" for name in default_values}),
    ],
)
def test_cli_colors_presets(preset: str, expected: dict[str, str]) -> None:
    cli_colors = getattr(CliColors, preset)()
    for name, value in expected.items():
        assert getattr(cli_colors, name) == (get_color_func(value) if value else str)
