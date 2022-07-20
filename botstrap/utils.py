from typing import Callable, Final, TypeAlias

from colorama import Fore, Style

_FormatText: TypeAlias = Callable[[str], str]


def _color(fore_color_code: str) -> _FormatText:
    def color_text(text: str) -> str:
        return f"{fore_color_code}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    return color_text


cyan: Final[_FormatText] = _color(Fore.CYAN)
green: Final[_FormatText] = _color(Fore.GREEN)
grey: Final[_FormatText] = _color(Fore.BLACK)  # "Bright black" is displayed as grey.
magenta: Final[_FormatText] = _color(Fore.MAGENTA)
red: Final[_FormatText] = _color(Fore.RED)
yellow: Final[_FormatText] = _color(Fore.YELLOW)
