from __future__ import annotations

from dataclasses import KW_ONLY, asdict, dataclass
from typing import Callable

from colorama import Fore, Style, init

# Initialize colorama the first time this module is imported anywhere.
init(autoreset=True)


class Color:
    @classmethod
    def _color_text(cls, fore_color_code: str, text: str) -> str:
        return f"{fore_color_code}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    @classmethod
    def blue(cls, text: str) -> str:
        return cls._color_text(Fore.BLUE, text)

    @classmethod
    def cyan(cls, text: str) -> str:
        return cls._color_text(Fore.CYAN, text)

    @classmethod
    def green(cls, text: str) -> str:
        return cls._color_text(Fore.GREEN, text)

    @classmethod
    def grey(cls, text: str) -> str:
        return cls._color_text(Fore.BLACK, text)  # "Bright black" is displayed as grey.

    @classmethod
    def magenta(cls, text: str) -> str:
        return cls._color_text(Fore.MAGENTA, text)

    @classmethod
    def red(cls, text: str) -> str:
        return cls._color_text(Fore.RED, text)

    @classmethod
    def yellow(cls, text: str) -> str:
        return cls._color_text(Fore.YELLOW, text)


@dataclass(eq=False, frozen=True)
class ThemeColors:
    primary: Callable[[str], str] = str
    _: KW_ONLY = None  # type: ignore[assignment]
    error: Callable[[str], str] = Color.red
    highlight: Callable[[str], str] = Color.cyan
    lowlight: Callable[[str], str] = Color.grey
    success: Callable[[str], str] = Color.green
    warning: Callable[[str], str] = Color.yellow

    @classmethod
    def default(cls) -> ThemeColors:
        return cls()

    @classmethod
    def off(cls) -> ThemeColors:
        return cls(**{key: str for key in asdict(cls.default())})
