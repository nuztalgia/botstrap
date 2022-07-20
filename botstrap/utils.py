from base64 import urlsafe_b64encode
from functools import partial
from os import urandom
from pathlib import Path
from typing import Callable, Final, Optional, TypeAlias

from colorama import Fore, Style
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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


def read_decrypted(file_path: Path, password: Optional[str] = None) -> str:
    try:
        return _fernet(password).decrypt(file_path.read_bytes()).decode()
    except InvalidToken:
        return ""


def write_encrypted(file_path: Path, data: str, password: Optional[str] = None) -> None:
    file_path.write_bytes(_fernet(password).encrypt(data.encode()))


def _fernet(password: Optional[str]) -> Fernet:
    def get_extra_bytes(get_initial_bytes: Callable[[], bytes]) -> bytes:
        # TODO: Store these in a file. Generating them every time doesn't work (obv).
        return get_initial_bytes()

    if password:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=get_extra_bytes(partial(urandom, 16)),
            iterations=480000,
        )
        key = urlsafe_b64encode(kdf.derive(password.encode()))
    else:
        key = get_extra_bytes(Fernet.generate_key)

    return Fernet(key)
