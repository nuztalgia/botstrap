"""This module contains a class that acts as a model for custom command-line options."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Iterable


def option_to_arg_dict(option: Option) -> dict[str, Any]:
    """Returns the `Option` as a `dict` that can be understood by argstrap/argparse."""
    if option.is_flag:
        return {"action": "store_true", "help": option.help}
    else:
        return {
            "action": "store",
            "type": type(option.default),
            **{k: v for k, v in asdict(option).items() if k != "is_flag"},
        }


@dataclass(eq=False, frozen=True, kw_only=True)
class Option:
    """A model for a custom option to add to the Botstrap-provided CLI.

    TODO: Flesh out this class and add more documentation/examples.
    """

    def __post_init__(self) -> None:
        """Ensures all fields are valid in order to prevent problems down the line."""
        if self.is_flag and (self.default or self.choices):
            raise ValueError("`is_flag` cannot be used with `default` or `choices`.")

        if self.default == argparse.SUPPRESS:
            raise ValueError(f'"{self.default}" is not a valid value for `default`.')

        if (option_type := type(self.default)) not in (str, int, float):
            raise TypeError(f'"{option_type}" is not a valid type for `default`.')

        if any((type(choice) != option_type) for choice in self.choices):
            raise TypeError(f'All items in `choices` must be of type "{option_type}".')

    # region FIELDS

    is_flag: bool = False
    """Whether this option represents a boolean flag (i.e. an on/off switch).

    A **flag** is the most basic type of option. It doesn't require another command-line
    argument to tell it what its final "return value" should be - it'll simply be `True`
    if the option name was specified on the command line, or `False` if it wasn't.
    """

    default: str | int | float = ""
    """The value that should be used if this option is not specified.

    This field also determines the `#!py type` of the final "return value" of this
    option after command-line args have been parsed. If this field is omitted, this
    option's `#!py type` will be `#!py str` and its default value will be the empty
    string (`#!py ""`).
    """

    choices: Iterable[str | int | float] = ()
    """A group of values representing the valid choices for this option.

    When command-line arguments are parsed and this option is specified, the given value
    will be checked against the values in this field. If the given value is not one of
    these "acceptable" values, an error message will be displayed.

    If this field is omitted or otherwise empty, the given value for this option will
    not be checked. In other words, **any** value of the correct `#!py type`
    (see [`default`][botstrap.Option.default]) will be considered "acceptable".
    """

    help: str | None = None
    """A string containing a brief description of this option.

    This text will be displayed alongside the entry for this option when `--help` (or
    `-h`) is specified on the command line. If omitted, the entry for this option will
    appear without any help text. To prevent this option from being listed in the help
    menu, set this field to `Option.HIDE_HELP`.
    """

    # endregion FIELDS

    HIDE_HELP: ClassVar[str] = argparse.SUPPRESS
    """A constant used as the value for `help` to hide an option's `-h` menu entry."""
