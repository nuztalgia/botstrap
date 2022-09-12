"""This module contains `Color` & `CliColors`, both of which add color to CLI output."""
from __future__ import annotations

from dataclasses import KW_ONLY, asdict, dataclass
from typing import Callable

from colorama import Fore, Style, init

# Initialize colorama the first time this module is imported anywhere.
init(autoreset=True)


class Color:
    """A collection of functions that add color to console-printed strings.

    These functions work by adding pre-defined [ANSI escape codes][1] from the
    [`colorama`][2] library to the beginning and end of the given string.
    The escape code characters are interpreted by the console as instructions
    to display the enclosed text in a specific color/style.

    [1]: http://en.wikipedia.org/wiki/ANSI_escape_code
    [2]: https://pypi.org/project/colorama/

    !!! example "Example - Printing rainbow-colored text :rainbow_flag:"
        ```pycon
        >>> from botstrap import Color
        >>> print(
        ...     f"{Color.pink('P')}{Color.red('R')}{Color.yellow('I')}"
        ...     f"{Color.green('D')}{Color.cyan('E')}{Color.blue('!')}"
        ... )
        ```
    """

    @classmethod
    def _color_text(cls, fore_color_code: str, text: str) -> str:
        return f"{fore_color_code}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    @classmethod
    def blue(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it blue."""
        return cls._color_text(Fore.BLUE, text)

    @classmethod
    def cyan(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it cyan."""
        return cls._color_text(Fore.CYAN, text)

    @classmethod
    def green(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it green."""
        return cls._color_text(Fore.GREEN, text)

    @classmethod
    def grey(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it grey."""
        return cls._color_text(Fore.BLACK, text)  # "Bright black" is displayed as grey.

    @classmethod
    def pink(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it pink."""
        return cls._color_text(Fore.MAGENTA, text)

    @classmethod
    def red(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it red."""
        return cls._color_text(Fore.RED, text)

    @classmethod
    def yellow(cls, text: str) -> str:
        """Returns a copy of the string with extra characters to color it yellow."""
        return cls._color_text(Fore.YELLOW, text)


@dataclass(eq=False, frozen=True)
class CliColors:
    """A model for the colors used by the Botstrap-provided CLI.

    The fields of this class are `Callable[[str], str]` functions that can add color to
    particular types of text shown in the console, such as success and error messages.
    Simple color presets are provided by the [`default()`][botstrap.CliColors.default]
    and [`off()`][botstrap.CliColors.off] class methods.

    To personalize these colors, you can create a new instance of this class and
    specify any values you'd like to change. All constructor arguments correspond to
    field names, and all of them are keyword-only except for [`primary`](./#primary).

    ??? tip "Tip - Set your bot's primary color!"
        <div id="primary"/>
        The `primary` field is not assigned a color by default. This is deliberate, as
        it will be used to color your bot's name and is essentially a personal brand.
        :rainbow:

        To customize this field, simply instantiate this class with your desired color -
        such as `CliColors(Color.blue)` - and pass it in as the `colors` parameter to
        the `Botstrap` constructor. See the example below for more details.

    ??? info "Info - Field names and descriptions"
        The following table lists the names of all the fields in this class,
        demonstrates the colors that they use by default, and describes the types of
        text to which they are applied.

        | Field            | Description                                               |
        | ---------------- | --------------------------------------------------------- |
        |`primary`         | Your bot's name. See the [tip](./#primary) for more info. |
        |`error`{.red}     | Message shown when the script terminates due to an error. |
        |`highlight`{.cyan}| Important text that isn't a success/warning/error message.|
        |`lowlight`{.grey} | Less important text that may safely be de-emphasized.     |
        |`success`{.green} | Text shown when processes or tasks complete successfully. |
        |`warning`{.yellow}| Text shown when something goes wrong, but is recoverable. |

    ??? example "Example - Customizing specific colors"
        Let's say you want to use cyan as your bot's primary color... but cyan is the
        default highlight color, so that might be confusing. Fortunately, it's easy to
        change the highlight color too! This example demonstrates how to change the
        primary color to `cyan`{.cyan} and the highlight color to `pink`{.pink}.

        ```py title="bot.py"
        from botstrap import Botstrap, CliColors, Color

        bot_colors = CliColors(Color.cyan, highlight=Color.pink)
        Botstrap(name="cyan-bot", colors=bot_colors).run_bot()
        ```

        ```{.console title="Console Session" .custom-colors .ends-with-input}
        $ python bot.py

        cyan-bot: You currently don't have a saved default bot token.
        Would you like to add one now? If so, type "yes" or "y":
        ```
    """

    primary: Callable[[str], str] = str
    _: KW_ONLY = None  # type: ignore[assignment]  # (1)
    error: Callable[[str], str] = Color.red
    highlight: Callable[[str], str] = Color.cyan
    lowlight: Callable[[str], str] = Color.grey
    success: Callable[[str], str] = Color.green
    warning: Callable[[str], str] = Color.yellow

    @classmethod
    def default(cls) -> CliColors:
        """Returns an instance of this class with default values for all colors.

        Functions from `Color` are used as the defaults for all fields except for
        [`primary`](./#primary), which defaults to `str()` and is essentially a no-op
        unless overridden.
        """
        return cls()

    @classmethod
    def off(cls) -> CliColors:
        """Returns an instance of this class with all colors disabled.

        In other words, the values of all fields will effectively be no-ops -
        functions that simply call `str()` on their inputs without adding any
        formatting characters. This means that any text printed to the console
        will be displayed in its original (un-styled) color.
        """
        return cls(**{key: str for key in asdict(cls.default())})
