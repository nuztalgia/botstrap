"""Tests for the `botstrap.internal.metadata` module."""
from __future__ import annotations

from typing import Callable

import pytest

from botstrap.internal import Metadata


@pytest.fixture
def mock_packages(
    monkeypatch, packages: dict[str, list[str]]
) -> Callable[[], dict[str, list[str]]]:
    def get_packages() -> dict[str, list[str]]:
        return packages

    monkeypatch.setattr(
        "botstrap.internal.metadata.packages_distributions", get_packages
    )
    return get_packages


@pytest.mark.parametrize(
    "packages",
    [
        {},
        {"pkg_name": ["dist-name"]},
        {"a": ["a"], "b": ["b"], "c": ["c"], "d": ["d", "e", "f"]},
        {"discord": ["nextcord"], "pycord": ["py-cord"]},
    ],
)
def test_get_bot_class_info_fail(mock_packages, packages: dict[str, list[str]]) -> None:
    with pytest.raises(RuntimeError, match="Cannot.*determine.*class.*Discord bot"):
        Metadata.get_bot_class_info()


@pytest.mark.parametrize(
    "packages, expected",
    [
        ({"discord": ["discord.py"]}, ("discord.Client", "run", False)),
        ({"discord": ["py-cord"]}, ("discord.Bot", "run", False)),
        (
            {"disnake": ["disnake"]},
            ("disnake.ext.commands.InteractionBot", "run", False),
        ),
        ({"hikari": ["hikari"]}, ("hikari.GatewayBot", "run", True)),
        (
            {"interactions": ["discord-py-interactions"]},
            ("interactions.Client", "start", True),
        ),
        ({"naff": ["naff"]}, ("naff.Client", "start", False)),
        (
            {"discord": ["nextcord"], "nextcord": ["nextcord"]},
            ("nextcord.ext.commands.Bot", "run", False),
        ),
        (
            {"discord": ["nextcord", "py-cord"], "disnake": ["disnake"]},
            ("discord.Bot", "run", False),
        ),
    ],
)
def test_get_bot_class_info_success(
    mock_packages, packages: dict[str, list[str]], expected: tuple[str, str, bool]
) -> None:
    bot_class_info = Metadata.get_bot_class_info()
    assert bot_class_info.qualified_name == expected[0]
    assert bot_class_info.run_method_name == expected[1]
    assert bot_class_info.init_with_token == expected[2]
