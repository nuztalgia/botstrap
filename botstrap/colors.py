from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, TypeAlias

from colorama import Fore, Style

_FormatText: TypeAlias = Callable[[str], str]


def _color(fore_color_code: str) -> _FormatText:
    def color_text(text: str) -> str:
        return f"{fore_color_code}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    return color_text


@dataclass(eq=False, frozen=True, kw_only=True)
class Colors:
    cyan: _FormatText = _color(Fore.CYAN)
    green: _FormatText = _color(Fore.GREEN)
    grey: _FormatText = _color(Fore.BLACK)  # "Bright black" is displayed as grey.
    magenta: _FormatText = _color(Fore.MAGENTA)
    red: _FormatText = _color(Fore.RED)
    yellow: _FormatText = _color(Fore.YELLOW)

    alert: _FormatText = magenta
    error: _FormatText = red
    highlight: _FormatText = cyan
    lowlight: _FormatText = grey
    success: _FormatText = green
    warning: _FormatText = yellow

    @classmethod
    def default(cls) -> Colors:
        return cls()

    @classmethod
    def off(cls) -> Colors:
        return cls(**{key: _no_op for key in asdict(cls.default())})


def _no_op(text: str) -> str:
    return text
