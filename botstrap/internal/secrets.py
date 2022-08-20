"""This module contains the `Secret` class, which encrypts and decrypts data files."""
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

    Each instance of this class represents a unique string containing secret information
    that must be encrypted before saving it to a file, and subsequently decrypted before
    it can be accessed again.

    ??? question "FAQ - How does the encryption work?"
        This class uses [Fernet](https://cryptography.io/en/latest/fernet/) symmetric
        encryption from the [`cryptography`](https://pypi.org/project/cryptography/)
        package to encrypt and decrypt data, optionally with extra protection in the
        form of a password. The encrypted data is guaranteed to be unreadable without
        the **key** that was used to encrypt it. Fernet keys are uniquely generated
        for each secret at encryption time.

        Each secret is therefore represented in the file system by two separate `.key`
        files, both of which include the secret's `uid` in their file names. One of
        the files contains the encrypted `content` of the secret, and the other file
        contains the `fernet` key required to decrypt it. Each of these files is
        useless without the other. :closed_lock_with_key:

    ??? info "Info - Fernet encryption with passwords"
        Factoring a password into the encryption of a secret can add an extra layer of
        protection because the password will not be stored anywhere on the file system.
        This means that even if a malicious actor were to gain access to both the
        `content.key` and `fernet.key` files of a secret, they still would not be able
        to decipher the original data.

        If a password is provided when a secret's
        [`write()`][botstrap.internal.secrets.Secret.write] method is invoked,
        the specified data will be encrypted using an algorithm based on [this
        example](https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet)
        from the Fernet documentation. The password will be run through the
        [`PBKDF2HMAC`](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC)
        key derivation function to factor it into the `fernet` key for the secret.
        It will therefore be required again in order to "complete" the key
        **every time** the secret is decrypted.
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
                Where to store the encrypted files holding this secret's data. If
                omitted, the files will be saved in a folder named `.botstrap_keys`,
                which will be created in the same location as the file containing the
                `#!py "__main__"` module for the executing script.
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
        """The `Path` of the file that may contain this secret's encrypted data.

        This property will only return the `content` file path, as the `fernet` file is
        irrelevant outside of this class. The return value will be an instance of
        [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#concrete-paths),
        but it is **not** guaranteed to point to an existing file (e.g. if this secret's
        data hasn't been created/saved yet, or has been deleted).
        """
        return self._get_key_file(_CONTENT_FILE)

    @property
    def min_pw_length(self) -> int:
        """The minimum length for this secret's password, if one is required.

        For secrets that require a password, this property will return `#!py 8` (chosen
        arbitrarily to try and balance security vs. convenience). For secrets that don't
        require a password, this will return `#!py 0`.
        """
        return _MINIMUM_PASSWORD_LENGTH if self.requires_password else 0

    def read(self, password: Optional[str] = None) -> Optional[str]:
        """Returns the decrypted data from this secret's file if it exists and is valid.

        The `password` param **must** be provided if this secret was originally
        encrypted with a password, and **must not** be provided if the opposite is true.
        If provided, it must match the original password or else the decrypted data
        will not be valid and this method will return `None`.

        Args:
            password:
                The password originally used to create this secret, if applicable.
                Otherwise, this should be `None`.

        Returns:
            The data for this secret if it exists & can be decrypted, otherwise `None`.
        """
        data = self._get_fernet(password).decrypt(self.file_path.read_bytes()).decode()
        return data if self.validate(data) else None

    def write(self, data: str, password: Optional[str] = None) -> None:
        """Encrypts and writes the data to a file, optionally protected by a password.

        If the `password` param is provided, it must be at least `#!py 8` characters
        long (see [`min_pw_length`][botstrap.internal.secrets.Secret.min_pw_length])
        and will have to be provided again whenever
        [`read()`][botstrap.internal.secrets.Secret.read]
        is invoked to decrypt this secret.

        Omitting the `password` parameter means that only the secret's two `.key` files
        will be required in order to decrypt it. This is both more convenient *and* more
        dangerous, so choose wisely. :genie:

        Args:
            data:
                A string containing sensitive information to be encrypted before being
                stored in a file.
            password:
                An optional string that can improve the security of this secret. If
                omitted, a password will not be factored into the encryption algorithm
                for this secret.

        Raises:
            ValueError: If the `data` is not considered valid according to the
                [`valid_pattern`][botstrap.internal.secrets.Secret.__init__]
                that was specified when this secret was instantiated.
        """
        if not self.validate(data):
            raise ValueError(f'Attempted to write invalid data for "{self.uid}".')
        self.file_path.write_bytes(self._get_fernet(password).encrypt(data.encode()))

    def clear(self) -> None:
        """Deletes all files containing data related to this secret, if any exist.

        This method **does not** scan the entire system to
        locate the files for a secret - it only checks the
        [`storage_directory`][botstrap.internal.secrets.Secret.__init__]
        that was specified upon instantiation.

        !!! tip "Tip - Don't scramble your secrets!"
            If a secret's `.key` files are renamed or moved out of their original
            directory without a corresponding change to the `uid` and/or
            `storage_directory` constructor parameters (or vice versa), then the secret
            will behave as if there are no existing files associated with it.
            Fortunately, this can easily be resolved by either moving the files back
            into place or updating the constructor parameters in your code.
        """
        for qualifier in _KEY_FILES:
            key_file = self._get_key_file(qualifier)
            key_file.unlink(missing_ok=True)

    def _get_key_file(self, qualifier: str) -> Path:
        """Returns the `Path` to the qualified (content/fernet) file for this secret."""
        if qualifier not in _KEY_FILES:
            raise ValueError(f'Invalid key file qualifier: "{qualifier}"')

        if (file := self.storage_directory / f".{self.uid}.{qualifier}.key").is_dir():
            dir_path = file.resolve()
            raise ValueError(f'Expected a file, but found a directory: "{dir_path}"')

        return file

    def _get_fernet(self, password: Optional[str]) -> Fernet:
        """Returns a `Fernet` instance for encrypting and decrypting `bytes` data."""
        if self.requires_password:
            if not password:
                raise ValueError(f'Password is required to read/write "{self.uid}".')
            elif not isinstance(password, str):
                raise TypeError(f'Password type must be "str", not "{type(password)}".')
            elif len(password) < (length := self.min_pw_length):
                raise ValueError(f"Password must be at least {length} characters long.")

        def get_extra_bytes(get_initial_bytes: Callable[[], bytes]) -> bytes:
            if not (fernet_file := self._get_key_file(_FERNET_FILE)).is_file():
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


def _get_validator(
    pattern: str | re.Pattern | Callable[[str], Any] | None
) -> Callable[[str], bool]:
    """Turns the `pattern` into a function that accepts a string and returns a bool."""
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
    """Turns the `directory_path` into a usable `Path`, creating the dir if needed."""
    if not directory_path:
        directory_path = Metadata.get_default_keys_dir()
    elif isinstance(directory_path, str):
        directory_path = Path(directory_path)

    if (directory_path := directory_path.resolve()).is_file():
        raise ValueError(f'Expected a directory, but found a file: "{directory_path}"')

    directory_path.mkdir(exist_ok=True)
    return directory_path
