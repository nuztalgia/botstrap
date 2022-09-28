"""This module contains the `Option` class, which is a model for custom CLI options."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, ClassVar, Iterable


@dataclass(eq=False, frozen=True, kw_only=True)
class Option:
    """A model for a custom option to add to the Botstrap-provided CLI.

    This is a simple [dataclass][1] whose **attributes** (also referred to as
    **fields**) define the type and behavior of a command-line option, thus allowing
    for extensive customization of a bot's CLI.

    To add a custom option, create an instance of this class and pass it into the
    [`parse_args()`][botstrap.Botstrap.parse_args] method of your `Botstrap`
    integration. You may add as many options as you want, as long as their names
    are unique. Their values will be returned as an instance of `Option.Results`.

    [1]: https://docs.python.org/3/library/dataclasses.html
    """

    def __post_init__(self) -> None:
        """Ensures all fields are valid in order to prevent problems down the line."""
        if self.flag and (self.default or self.choices):
            raise ValueError("'flag' cannot be used alongside 'default' or 'choices'.")

        if self.default == argparse.SUPPRESS:
            raise ValueError(f"\"{self.default}\" is not a valid value for 'default'.")

        if (option_type := type(self.default)) not in (str, int, float):
            raise TypeError(
                f"{option_type} is not a valid type for 'default'. Expected one of "
                f"'{str.__name__}', '{int.__name__}', or '{float.__name__}'."
            )

        if any((not isinstance(choice, option_type)) for choice in self.choices):
            raise TypeError(
                f"All elements in 'choices' must be {option_type} to match 'default'."
            )

    # region FIELDS

    flag: bool = False
    """Whether this option represents a boolean flag (i.e. an on/off switch).

    A **flag** is the most basic type of option. It doesn't require another command-line
    argument to tell it what its value should be - it'll simply be `True` if its name
    (or abbreviation) was specified on the command line, or `False` if not.

    ??? question "FAQ - How does this field affect the others?"
        - If this field is set to `True`, you should **ignore** the
          [`default`][botstrap.Option.default] and [`choices`][botstrap.Option.choices]
          fields when instantiating this class. Effectively,
          [`default`][botstrap.Option.default] will behave as if it were set to `False`,
          and [`choices`][botstrap.Option.choices] will be unused because this option
          does not parse a *separate* command-line argument to determine its value.

        - If this field is set to `False` (or omitted, because that's the default
          setting), you should **set** the [`default`][botstrap.Option.default] and
          [`choices`][botstrap.Option.choices] fields when instantiating this class -
          unless you intend to use their default values, of course.

        - This field has no effect on [`help`][botstrap.Option.help], which should
          always be provided for a user-friendly experience! :sparkles:

    ??? note "Note - The default value of a flag"
        It's important to avoid confusing the value of this **field** with the value of
        the resulting command-line **option**:

        - To create an option with a `bool` value type, this field should always be set
          to `True`.
        - The default value of the resulting command-line option will always be `False`.

        Consequently, if you'd like to create a custom option corresponding to a `bool`
        value that normally defaults to `True` (such as [`auto_sync_commands`][1]),
        it must be semantically negated. For example:

        ```{.py title="" .annotate .line-numbers-off}
        from botstrap import Botstrap, Option

        botstrap = Botstrap()
        args = botstrap.parse_args(
            disable_auto_sync=Option(
                flag=True, # (1)
                help="Disable automatic syncing of the bot's slash commands.",
            )
        )
        botstrap.run_bot(auto_sync_commands=(not args.disable_auto_sync))
        ```

        1.  This creates a flag named `--disable-auto-sync` (or `-d` for short) with
            a default value of `False`.

        [1]: https://docs.pycord.dev/en/master/api.html#discord.Bot.auto_sync_commands
    """

    default: str | int | float = ""
    """The value that should be used if this option is not specified.

    In addition to providing a standard value, this field determines the `type` of the
    parsed value for this option. If omitted, this option's type will be `str` and its
    default value will be the empty string.

    Note that the value of this field **must** be a `str`, an `int`, or a `float`.
    To create an option with a `bool` value type, use the [`flag`][botstrap.Option.flag]
    field instead.

    ??? example "Example - Creating options of different types"
        ```py title="example.py"
        from botstrap import Botstrap, Option

        Botstrap().parse_args(
            a=Option(help="An option with type 'str'."),
            b=Option(default=0, help="An option with type 'int'."),
            c=Option(default=0.0, help="An option with type 'float'."),
            d=Option(flag=True, help="A boolean flag."),
        )
        ```

        ```console title="Console Session"
        $ python example.py -h
        usage: example.py [-a <str>] [-b <int>] [-c <float>] [-d] [-t] [--help]

          Run "python example.py" with no parameters to start the bot.

        options:
          -a <>         An option with type 'str'.
          -b <>         An option with type 'int'.
          -c <>         An option with type 'float'.
          -d            A boolean flag.
          -t, --tokens  View/manage your saved Discord bot tokens.
          -h, --help    Display this help message.
        ```
    """

    choices: Iterable[str | int | float] = ()
    """A group of values representing the acceptable choices for this option.

    When command-line arguments are parsed and this option is specified, the given
    value will be checked against the values in this field. If the given value is
    not one of these "acceptable" values, an error message will be displayed.

    If this field is omitted or otherwise empty, the given value for this option
    will not be checked. This means that **any** value with the same `type` as the
    [`default`][botstrap.Option.default] value will be considered acceptable.

    ??? example "Example - Defining valid values for an option"
        ```{.py title="example.py" .annotate}
        from botstrap import Botstrap, Option

        Botstrap().parse_args(
            pizza_topping=Option(
                default="cheese", # (1)
                choices=("mushrooms", "olives", "pepperoni", "sausage"),
            ),
        )
        ```

        1.  If the specified `default` value is not included in `choices`, Botstrap will
            automatically prepend it to ensure consistent and predictable behavior.

        ```console title="Console Session"
        $ python example.py -p pineapple
        usage: example.py [-p <str>] [-t] [--help]
        example.py: error: argument -p/--pizza-topping: invalid choice: 'pineapple'
        (choose from 'cheese', 'mushrooms', 'olives', 'pepperoni', 'sausage')
        ```
    """

    help: str | None = None
    """A string containing a brief description of this option.

    This text will be displayed alongside the entry for this option when `--help` (or
    `-h`) is specified on the command line. If omitted, the entry for this option will
    appear without any help text. To prevent this option from being listed in the help
    menu, set this field to [`Option.HIDE_HELP`][botstrap.Option.HIDE_HELP].

    ??? example "Example - Configuring visibility in the help menu"
        ```py title="example.py"
        from botstrap import Botstrap, Option

        args = Botstrap().parse_args(
            x=Option(help="A user-friendly option with help text!"),
            y=Option(),
            z=Option(help=Option.HIDE_HELP),
        )
        print(args)
        ```

        ```console title="Console Session"
        $ python example.py -h
        usage: example.py [-x <str>] [-y <str>] [-t] [--help]

          Run "python example.py" with no parameters to start the bot.

        options:
          -x <>         A user-friendly option with help text!
          -y <>
          -t, --tokens  View/manage your saved Discord bot tokens.
          -h, --help    Display this help message.

        $ python example.py -y "a mysterious option" -z "a super secret option"
        Results(z='', y='a mysterious option', z='a super secret option')
        ```

        Notice that `-y` appears without a description because it didn't specify a value
        for its `help` field, while `-z` does not appear in the help menu at all because
        it specified `Option.HIDE_HELP`. However, both options are equally usable.
    """

    # endregion FIELDS

    HIDE_HELP: ClassVar[str] = argparse.SUPPRESS
    """Hides an option's `-h` menu entry when used as the value for the `help` field."""

    class Results(argparse.Namespace):
        """A basic class to hold the final parsed values of custom command-line options.

        This class (like its superclass, [`Namespace`][1]) is essentially just an
        `object` with a readable string representation. The names of its attributes
        will match the names you specify for your `Option` objects when passing them
        as keyword arguments to [`parse_args()`][botstrap.Botstrap.parse_args].

        If you prefer to work with a `dict` representation of your parsed option values,
        simply pass your instance of this class to the built-in Python function
        [`vars()`][2].

        [1]: https://docs.python.org/3/library/argparse.html#the-namespace-object
        [2]: https://docs.python.org/3/library/functions.html#vars
        """

        def __init__(self, *allowed_keys: str, **kwargs: Any) -> None:
            """Initializes a new `Option.Results` instance.

            Args:
                *allowed_keys:
                    The names of the attributes that are assignable to this object.
                **kwargs:
                    The attribute names and corresponding values to assign to this
                    object. Only attributes whose names are present in `*allowed_keys`
                    will be assigned.
            """
            super().__init__(**{k: kwargs[k] for k in kwargs if k in allowed_keys})
