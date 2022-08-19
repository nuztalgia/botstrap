"""This module contains a class that acts as a model for custom command-line options."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any, Callable, ClassVar, Iterable

from botstrap import Color


def option_to_arg_dict(option: Option) -> dict[str, Any]:
    """Returns the `Option` as a `dict` that can be understood by argstrap/argparse."""
    if (option_dict := asdict(option)).pop("is_flag"):
        return {
            "action": "store_true",
            **{k: v for k, v in option_dict.items() if k not in ("default", "choices")},
        }
    else:
        return {
            "action": "store",
            "type": type(option.default),
            "choices": option.choices or None,
            **{k: v for k, v in option_dict.items() if k != "choices"},
        }


def show_unused_value(value: Any) -> None:
    """Prints the unused `value` to the console in red text, to flag the problem."""
    print(Color.red(f"UNUSED OPTION VALUE: '{value}' ({type(value)})"))


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

    ??? question "FAQ - How does this field affect the others?"
        - If this field is set to `True`, you may **ignore** the
          [`default`][botstrap.Option.default] and [`choices`][botstrap.Option.choices]
          fields when instantiating this class. Effectively, `default` will behave as
          if it were set to `False`, and `choices` will be unused because this option
          does not parse a **separate** command-line argument to determine its value.

        - If this field is set to `False` (or omitted, because that's the default
          setting), you **must** set the [`default`][botstrap.Option.default] and
          [`choices`][botstrap.Option.choices] fields when instantiating this class -
          unless you intend to use their default values.

        - This field has no effect on [`help`][botstrap.Option.help], which should
          **always** be provided for a user-friendly experience! :sparkles:
    """

    default: str | int | float = ""
    """The value that should be used if this option is not specified.

    This field also determines the `#!py type` of the final "return value" of this
    option after command-line args have been parsed. If this field is omitted, this
    option's `#!py type` will be `#!py str` and its default value will be the empty
    string (`#!py ""`).

    Note that the value of this field **must** be a `#!py str`, an `#!py int`,
    or a `#!py float`. To create an option with a `#!py bool` value type, use the
    [`is_flag`][botstrap.Option.is_flag] field.
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

    callback: Callable[[Any], None] = show_unused_value
    """A function that will be invoked with the value of this option after it's parsed.

    The function should accept a single parameter whose type matches that of the
    [`default`][botstrap.Option.default] value, or a `#!py bool` if
    [`is_flag`][botstrap.Option.is_flag] was set to `True`. For brevity and ease of use,
    the parameter is type-hinted as `Any`, but you may assume it will be called with a
    value of the appropriate type.

    ??? note "Note - Omitting this field"
        If this field is omitted, then this whole `Option` will essentially **do
        nothing**. To flag this problem when it occurs (and to maybe also provide a
        useful debugging tool), the default value of this field is a function that will
        `#!py print` the value of the unused option to the console in highly visible
        `red`{.red} text.
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
