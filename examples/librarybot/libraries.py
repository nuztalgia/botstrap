from botstrap.internal import Metadata
from importlib.metadata import packages_distributions
from typing import Any, Final, Literal


SUPPORTED_DISCORD_PACKAGES: Final[tuple[str, ...]] = (
    "discord",
    "disnake",
    "hikari",
    "interactions",
    "naff",
    "nextcord",
)  # Pycord is supported too - it's included under the "discord" namespace.


def get_discord_packages() -> list[str]:
    """Returns a list of the names of all installed and supported Discord packages."""
    package_dists = packages_distributions()
    installed_packages = [p for p in package_dists if p in SUPPORTED_DISCORD_PACKAGES]

    # Nextcord doesn't actually use the "discord" namespace, which means the default
    # "discord.Bot" import won't work. Remove "discord" if it only contains Nextcord.
    if package_dists.get("discord") == ["nextcord"]:
        installed_packages.remove("discord")

    return sorted(installed_packages)


def get_library_names(package_name: str) -> list[str]:
    """Returns a list of possible names for the library providing the given package."""
    return packages_distributions()[package_name]


def create_bot(
    bot_class_name: Literal["hikari.GatewayBot", "interactions.Client", "naff.Client"],
    **constructor_kwargs: Any,
) -> Any:
    """Creates and returns an instance of the bot class (only for libs that need it)."""
    return Metadata.import_class(bot_class_name)(**constructor_kwargs)
