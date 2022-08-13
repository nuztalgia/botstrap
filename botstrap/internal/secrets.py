"""This module contains a class and helper functions for encrypting/decrypting data."""
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

_MINIMUM_PASSWORD_LENGTH: Final[int] = 8

_CONTENT_FILE: Final[str] = "content"
_FERNET_FILE: Final[str] = "fernet"

_KEY_FILES: Final[tuple[str, ...]] = (_CONTENT_FILE, _FERNET_FILE)


class Secret:
    """Manages read & write operations for files that contain sensitive encrypted data.

    A secret is represented in the file system by two `.key` files, both of which
    include the secret's `uid` in their file names. One of the files contains the
    encrypted `content` of the secret, and the other file contains the `fernet` key
    required to decrypt it. Each file is useless without the other.

    More about Fernet symmetric encryption: https://cryptography.io/en/latest/fernet/
    """

    def __init__(
        self,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
        valid_pattern: str | re.Pattern | Callable[[str], Any] | None = None,
    ) -> None:
        """Initializes a new `Secret` instance.

        Args:
            uid:
                A unique string identifying this secret. Will be used in the names of
                the files containing this secret's data.
            requires_password:
                Whether a user-provided password is required in order to read and/or
                write the data for this secret.
            display_name:
                A human-readable string describing this secret. Will be displayed in the
                CLI when referring to this secret. If omitted, the `uid` will be
                displayed instead.
            storage_directory:
                Where to store the encrypted `.key` files containing this secret's data.
                If omitted, the files will be saved in a folder named `.botstrap_keys`,
                which will be created in the same location as the file containing the
                `"__main__"` module for the executing script.
            valid_pattern:
                A string, regex pattern, or function for determining whether a provided
                input string fits the expected pattern for this secret. Will be used to
                validate the secret data before it's encrypted and after it's decrypted.
                If omitted, any string will be considered valid data for this secret.
        """
        if (not uid) or (not str(uid).isidentifier()):
            raise ValueError("Unique ID (uid) must be a valid non-empty identifier.")

        self.uid: Final[str] = str(uid)
        self.requires_password: Final[bool] = requires_password
        self.display_name: Final[str] = display_name or uid
        self.storage_directory: Final[Path] = _get_storage_directory(storage_directory)
        self.validate: Final[Callable[[str], bool]] = _get_validator(valid_pattern)

    def __str__(self) -> str:
        """Returns a nicely-printable string representation of this secret."""
        return self.display_name

    @property
    def file_path(self) -> Path:
        """The `Path` of the file containing this secret's encrypted data."""
        return self._get_key_file(_CONTENT_FILE)

    @property
    def minimum_password_length(self) -> int:
        """The minimum length for this secret's password, or `0` if not required."""
        return _MINIMUM_PASSWORD_LENGTH if self.requires_password else 0

    def write(self, data: str, password: Optional[str] = None) -> None:
        """Encrypts and writes the data to a file, optionally protected by a password.

        Args:
            data:
                A string containing sensitive information that should be encrypted
                before being stored in a file.
            password:
                An optional string that can improve the security of this secret. If
                provided, it must be at least `8` characters long, and must be inputted
                again every time this secret is decrypted. If omitted, a password will
                not be factored into this secret's encryption, and only the two `.key`
                files will be required to decrypt it (i.e. no human action needed).

        Raises:
            ValueError:
                If the `data` is not considered valid according to the `valid_pattern`
                parameter that was specified when instantiating this secret.
        """
        if not self.validate(data):
            raise ValueError(f'Attempted to write invalid data for "{self.uid}".')
        self.file_path.write_bytes(self._get_fernet(password).encrypt(data.encode()))

    def read(self, password: Optional[str] = None) -> Optional[str]:
        """Returns the decrypted data from this secret's file if it exists and is valid.

        Args:
            password:
                The password originally used to create this secret, if applicable. This
                must match the original password, or else the decrypted data will not be
                valid. If this secret was not created with a password, this argument
                should be omitted/ignored.

        Returns:
            The data for this secret if it exists & can be decrypted, otherwise `None`.
        """
        data = self._get_fernet(password).decrypt(self.file_path.read_bytes()).decode()
        return data if self.validate(data) else None

    def clear(self) -> None:
        """Deletes any files containing data related to this secret, if they exist."""
        for qualifier in _KEY_FILES:
            key_file = self._get_key_file(qualifier)
            key_file.unlink(missing_ok=True)

    def _get_key_file(self, qualifier: str) -> Path:
        if qualifier not in _KEY_FILES:
            raise ValueError(f'Invalid key file qualifier: "{qualifier}"')

        if (file := self.storage_directory / f".{self.uid}.{qualifier}.key").is_dir():
            dir_path = file.resolve()
            raise ValueError(f'Expected a file, but found a directory: "{dir_path}"')

        return file

    def _get_fernet(self, password: Optional[str]) -> Fernet:
        if self.requires_password:
            if not password:
                raise ValueError(f'Password is required to read/write "{self.uid}".')
            elif not isinstance(password, str):
                raise TypeError(f'Password type must be "str", not "{type(password)}".')
            elif len(password) < (length := self.minimum_password_length):
                raise ValueError(f"Password must be at least {length} characters long.")

        def get_extra_bytes(get_initial_bytes: Callable[[], bytes]) -> bytes:
            if not (fernet_file := self._get_key_file(_FERNET_FILE)).is_file():
                fernet_file.write_bytes(get_initial_bytes())
            return fernet_file.read_bytes()

        # Source: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
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
