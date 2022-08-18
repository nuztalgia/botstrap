"""This module contains a class that acts as a model for custom command-line options."""
from dataclasses import dataclass
from typing import Iterable


@dataclass(eq=False, frozen=True)
class CliOption:
    """A model for custom options to add to the Botstrap-provided CLI.

    TODO: Flesh out this class and add more documentation/examples.
    """

    help: str = ""
    default: str | bool | int | float = ""
    choices: Iterable[str | bool | int | float] = ()
