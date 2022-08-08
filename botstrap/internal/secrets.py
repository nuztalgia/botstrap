import os
import re
from base64 import urlsafe_b64encode
from functools import partial
from pathlib import Path
from typing import Any, Callable, Final, Optional, cast

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from botstrap.internal.metadata import Metadata

_CONTENT_FILE: Final[str] = "content"
_FERNET_FILE: Final[str] = "fernet"
_KEY_FILES: Final[tuple[str, ...]] = (_CONTENT_FILE, _FERNET_FILE)


class Secret:
    MINIMUM_PASSWORD_LENGTH: Final[int] = 8

    def __init__(
        self,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
        valid_pattern: str | re.Pattern | Callable[[str], Any] | None = None,
    ) -> None:
        if (not uid) or (not str(uid).isidentifier()):
            raise ValueError("Unique ID (uid) must be a valid non-empty identifier.")

        self.uid: Final[str] = str(uid)
        self.requires_password: Final[bool] = requires_password
        self.display_name: Final[str] = display_name or uid
        self.storage_directory: Final[Path] = _get_storage_directory(storage_directory)
        self.validate: Final[Callable[[str], bool]] = _get_validator(valid_pattern)

    def __str__(self) -> str:
        return self.display_name

    @property
    def file_path(self) -> Path:
        return _get_key_file(self.uid, self.storage_directory, _CONTENT_FILE)

    def read(self, password: Optional[str] = None) -> Optional[str]:
        fernet = _get_fernet(
            self.uid, self.storage_directory, self.requires_password, password
        )
        data = fernet.decrypt(self.file_path.read_bytes()).decode()
        return data if self.validate(data) else None

    def write(self, data: str, password: Optional[str] = None) -> None:
        if not self.validate(data):
            raise ValueError(f'Attempted to write invalid data for "{self.uid}".')
        fernet = _get_fernet(
            self.uid, self.storage_directory, self.requires_password, password
        )
        self.file_path.write_bytes(fernet.encrypt(data.encode()))

    def clear(self) -> None:
        for qualifier in _KEY_FILES:
            key_file = _get_key_file(self.uid, self.storage_directory, qualifier)
            key_file.unlink(missing_ok=True)


def _get_validator(
    pattern: str | re.Pattern | Callable[[str], Any] | None
) -> Callable[[str], bool]:
    if not pattern:
        pattern = re.compile(".*", re.DOTALL)
    elif isinstance(pattern, str):
        pattern = re.compile(pattern)

    def validate_pattern(text: str) -> bool:
        if isinstance(pattern, re.Pattern):
            return pattern.match(text) is not None
        else:
            return bool(cast(Callable, pattern)(text))

    return validate_pattern


def _get_storage_directory(directory_path: str | Path | None) -> Path:
    if not directory_path:
        try:
            directory_path = Metadata.get_main_file_path() / ".." / ".botstrap_keys"
        except OSError as e:
            raise ValueError("Could not resolve default key storage directory.") from e
    elif isinstance(directory_path, str):
        directory_path = Path(directory_path)

    if (directory_path := directory_path.resolve()).is_file():
        raise ValueError(f'Expected a directory, but found a file: "{directory_path}"')

    directory_path.mkdir(exist_ok=True)
    return directory_path


def _get_key_file(uid: str, storage_dir: Path, qualifier: str) -> Path:
    if qualifier not in _KEY_FILES:
        raise ValueError(f'Invalid key file qualifier: "{qualifier}"')

    if (key_file := storage_dir / f".{uid}.{qualifier}.key").is_dir():
        dir_path = key_file.resolve()
        raise ValueError(f'Expected a file, but found a directory: "{dir_path}"')

    return key_file


def _get_fernet(
    uid: str, storage_dir: Path, requires_password: bool, password: Optional[str]
) -> Fernet:
    if requires_password:
        if not password:
            raise ValueError(f'Password is required in order to read/write "{uid}".')
        elif not isinstance(password, str):
            raise TypeError(f'Password type must be "str", not "{type(password)}".')
        elif len(password) < (min_length := Secret.MINIMUM_PASSWORD_LENGTH):
            raise ValueError(f"Password must be at least {min_length} characters long.")

    def get_extra_bytes(get_initial_bytes: Callable[[], bytes]) -> bytes:
        fernet_file = _get_key_file(uid, storage_dir, _FERNET_FILE)
        if not fernet_file.is_file():
            fernet_file.write_bytes(get_initial_bytes())
        return fernet_file.read_bytes()

    if password:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=get_extra_bytes(partial(os.urandom, 16)),
            iterations=480000,
        )
        key = urlsafe_b64encode(kdf.derive(password.encode()))
    else:
        key = get_extra_bytes(Fernet.generate_key)

    return Fernet(key)