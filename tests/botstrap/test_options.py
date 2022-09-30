"""Tests for the `botstrap.options` module (`Option` and `Option.Results` classes)."""
from __future__ import annotations

from typing import Any

import pytest

from botstrap import Option


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"flag": True},
        {"default": 1},
        {"default": 1.5},
        {"choices": ["bing", "bang", "bong"]},
        {"choices": "abcdefghijklmnopqrstuvwxyz"},  # Each letter is a separate choice.
        {"default": 1, "choices": (1, 2, 3)},
        {"default": 1, "choices": {2, 3, 4}},
        {"default": 1, "choices": [1, 1]},
        {"default": 0.0, "choices": (1.0, 2.5, 3.14)},
        {"help": ""},
        {"flag": True, "help": Option.HIDE_HELP},
        {"choices": ["bing", "bang", "bong"], "help": "Sing, sang, song."},
    ],
)
def test_valid_options(kwargs: dict[str, Any]) -> None:
    option = Option(**kwargs)
    assert option.flag == kwargs.get("flag", False)
    assert option.default == kwargs.get("default", "")
    assert option.choices == kwargs.get("choices", ())
    assert option.help == kwargs.get("help", None)


@pytest.mark.parametrize(
    "kwargs, expected_error",
    [
        ({"flag": True, "default": 1}, ValueError),
        ({"flag": True, "choices": (1, 2, 3)}, ValueError),
        ({"default": Option.HIDE_HELP}, ValueError),
        ({"default": None}, TypeError),
        ({"default": False}, TypeError),
        ({"default": (1, 2, 3)}, TypeError),
        ({"choices": (1, 2, 3)}, TypeError),
        ({"default": 1, "choices": "abc"}, TypeError),
        ({"default": 1, "choices": (1.5, 2.5, 3.5)}, TypeError),
        ({"default": 1.5, "choices": (1, 2, 3)}, TypeError),
    ],
)
def test_invalid_options(kwargs: dict[str, Any], expected_error: Any) -> None:
    with pytest.raises(expected_error):
        Option(**kwargs)


@pytest.mark.parametrize(
    "allowed_keys, kwargs",
    [
        ([], {}),
        ([], {"a": 1, "b": 2, "c": 3}),
        (["a", "b"], {}),
        (["a", "b"], {"a": 1, "b": 2, "c": 3}),
        (["a", "b", "c"], {"a": 1, "b": 2, "c": 3}),
        (["a", "b", "c"], {"d": True, "e": None, "f": 3.14}),
    ],
)
def test_option_results(allowed_keys: list[str], kwargs: dict[str, Any]) -> None:
    results = Option.Results(*allowed_keys, **kwargs)
    for key, value in vars(results).items():
        assert key in allowed_keys
        assert value == kwargs[key]
        assert getattr(results, key) == value
