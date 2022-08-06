from __future__ import annotations

from dataclasses import KW_ONLY, asdict, dataclass
from typing import Callable

from colorama import Fore, Style, init

# Initialize colorama the first time this module is imported anywhere.
init(autoreset=True)


class Color:
    """A collection of functions that add color to strings printed to the console.

    These functions work by adding pre-defined ANSI escape codes from `colorama.Fore`
    and `colorama.Style` to the beginning and end of a given string. These characters
    are interpreted by the terminal as instructions to display the enclosed text in a
    specific color/style.

    Example:
        >>> from botstrap import Color
        >>>
        >>> print(
        >>>     f"{Color.pink('P')}{Color.red('R')}{Color.yellow('I')}"
        >>>     f"{Color.green('D')}{Color.cyan('E')}{Color.blue('!')}"
        >>> )
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
class ThemeColors:
    """A `dataclass` specifying the colors to be used for certain types of console text.

    The attributes of this class are all functions that accept and return a string, just
    like the class methods of `Color`. In fact, many of those class methods are used as
    the default values for this class's attributes, such that (for example) `Color.red`
    is synonymous with `ThemeColors.default().error`.

    Basic color presets are provided by this class's `default()` and `off()` methods. If
    you desire further customization, you can create a new instance of this class and
    specify any colors you'd like to change. All constructor arguments are keyword-only
    except `primary`, which is the only one NOT assigned a color by default.

    Example:
        >>> from botstrap import Botstrap, Color, ThemeColors
        >>>
        >>> bot_colors = ThemeColors(Color.cyan, highlight=Color.pink)
        >>> Botstrap(colors=bot_colors).run_bot()
    """

    primary: Callable[[str], str] = str
    _: KW_ONLY = None  # type: ignore[assignment]
    error: Callable[[str], str] = Color.red
    highlight: Callable[[str], str] = Color.cyan
    lowlight: Callable[[str], str] = Color.grey
    success: Callable[[str], str] = Color.green
    warning: Callable[[str], str] = Color.yellow

    @classmethod
    def default(cls) -> ThemeColors:
        """Returns an instance of this class with default values for all attributes."""
        return cls()

    @classmethod
    def off(cls) -> ThemeColors:
        """Returns an instance of this class with all colors disabled.

        In other words, all attributes are effectively no-ops (functions that simply
        call `str()` on their inputs without adding any formatting characters), causing
        any strings printed to the console to be displayed in their original color.
        """
        return cls(**{key: str for key in asdict(cls.default())})
