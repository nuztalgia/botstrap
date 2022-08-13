"""This module contains two classes for facilitating colorful command-line output."""
from __future__ import annotations

from dataclasses import KW_ONLY, asdict, dataclass
from typing import Callable

from colorama import Fore, Style, init

# Initialize colorama the first time this module is imported anywhere.
init(autoreset=True)


class Color:
    """A collection of functions that add color to console-printed strings.

    These functions work by adding pre-defined ANSI escape codes from
    [`colorama`](https://pypi.org/project/colorama/) to the beginning and end of the
    given string. These characters are interpreted by the console as instructions to
    display the enclosed text in a specific color/style.

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

    The following table summarizes this class's attributes, their default colors, and
    the types of text to which they are applied.

    | `primary`   | n/a    | Your bot's brand. See the "Note" below for more info.     |
    | ----------- | ------ | --------------------------------------------------------- |
    | `error`     | red    | Message shown when the script terminates due to an error. |
    | `highlight` | cyan   | Important text that isn't a success/warning/error message.|
    | `lowlight`  | grey   | Less important text that may safely be de-emphasized.     |
    | `success`   | green  | Text shown when processes or tasks complete successfully. |
    | `warning`   | yellow | Text shown when something goes wrong, but is recoverable. |

    Simple color presets are provided by the `default()` and `off()` class methods. If
    you desire further customization, you can create a new instance of this class and
    specify any colors you'd like to change. All constructor args are keyword-only
    except for `primary`.

    Note:
        The `primary` attribute is not assigned a color by default. This is deliberate,
        as it will be used to color your bot's name and is essentially a personal brand.

        To customize `primary`, simply instantiate this class with your desired color as
        the first constructor arg - such as `CliColors(Color.pink)` - and pass it in as
        the `colors` argument when creating your `BotstrapFlow` instance.

    Example:
        ```py title="bot.py" hl_lines="5"
        from botstrap import BotstrapFlow, CliColors, Color

        # We want cyan as our primary color, but it's the default highlight color...
        # Let's change the highlight color to pink so our bot can be primarily cyan!
        bot_colors = CliColors(Color.cyan, highlight=Color.pink)

        BotstrapFlow(colors=bot_colors).run_bot()  # Living our cyan bot dreams.
        ```
    """

    primary: Callable[[str], str] = str
    _: KW_ONLY = None  # type: ignore[assignment]
    error: Callable[[str], str] = Color.red
    highlight: Callable[[str], str] = Color.cyan
    lowlight: Callable[[str], str] = Color.grey
    success: Callable[[str], str] = Color.green
    warning: Callable[[str], str] = Color.yellow

    @classmethod
    def default(cls) -> CliColors:
        """Returns an instance of this class with default values for all attributes.

        Note:
            Class methods from `Color` are used as the default values for all of this
            class's attributes, except for `primary`.

            ```pycon
            >>> from botstrap import Color, CliColors
            >>> CliColors.default().error == Color.red
            True
            ```
        """
        return cls()

    @classmethod
    def off(cls) -> CliColors:
        """Returns an instance of this class with all colors disabled.

        In other words, all attributes are effectively no-ops (functions that simply
        call `str()` on their inputs without adding any formatting characters), causing
        any strings printed to the console to be displayed in their original color.
        """
        return cls(**{key: str for key in asdict(cls.default())})
