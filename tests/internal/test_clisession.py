"""Tests for the `botstrap.internal.clisession` module."""
from __future__ import annotations

from dataclasses import asdict

import pytest

from botstrap import CliColors, CliStrings, Color
from botstrap.internal import CliSession


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
    cli = CliSession(name, **kwargs)  # type:ignore[arg-type]
    assert cli.name == name
    assert asdict(cli.colors) == asdict(kwargs.get("colors", CliColors.default()))
    assert cli.strings == kwargs.get("strings", CliStrings.default())
