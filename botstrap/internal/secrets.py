"""This module contains the `Secret` class, which encrypts and decrypts data files."""
from __future__ import annotations

import os
import re
from base64 import urlsafe_b64encode
from functools import partial
from pathlib import Path
from typing import Any, Callable, Final, Literal, TypeAlias, cast, get_args

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from botstrap.internal.metadata import Metadata

_KeyQualifier: TypeAlias = Literal["content", "fernet"]


class Secret:
    """Manages read & write operations for files that contain sensitive encrypted data.

    Each instance of this class represents a unique string containing secret information
    that must be encrypted before saving it to a file, and subsequently decrypted before
    it can be accessed again.

    ??? question "FAQ - How does the encryption work?"
        <div id="key-files"/>
        This class uses [Fernet][1] symmetric encryption from the [`cryptography`][2]
        package to encrypt and decrypt data, optionally with extra protection in the
        form of a [password](./#passwords). The encrypted data is guaranteed to be
        unreadable without the original **key** that was used to encrypt it.
        Fernet keys are uniquely and randomly generated for each individual secret
        at encryption time.

        A secret is therefore represented in the file system by two separate `.key`
        files, both of which are named using the secret's `uid` (unique ID).
        One of the files contains the encrypted `content` of the secret, and the other
        file contains the `fernet` key required to decrypt it. Each of these files is
        useless without the other. :closed_lock_with_key:

    ??? info "Info - Fernet encryption with passwords"
        <div id="passwords"/>
        Factoring a password into the encryption of a secret can add an extra layer of
        protection because the password will not be stored anywhere on the file system.
        This means that even if a malicious actor were to gain access to both the
        `content.key` and `fernet.key` files of a secret, they still would not be able
        to decipher the original data.

        If a password is provided when a secret's
        [`write()`][botstrap.internal.Secret.write] method is invoked, the data will be
        encrypted using an algorithm based on [this][3] reference implementation. The
        password will be run through the [`PBKDF2HMAC`][4] key derivation function to
        obtain the Fernet key for the secret. As a result, the original password will
        have to be accurately entered in order to "complete" the key **every time** the
        secret is decrypted.

    [1]:https://cryptography.io/en/latest/fernet/
    [2]:https://pypi.org/project/cryptography/
    [3]:https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
    [4]:https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#pbkdf2
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
                A unique string to identify this secret.
                Will be used in the names of the files containing this secret's data.
            requires_password:
                Whether a user-provided password is required in order to read and/or
                write the data for this secret.
            display_name:
                A human-readable string describing this secret. Will be displayed in the
                CLI when referring to this secret. If omitted, the `uid` will be
                displayed instead.
            storage_directory:
                Where to store the files containing this secret's data.
                If omitted, they will be saved in a default
                [`.botstrap_keys`][botstrap.internal.Metadata.get_default_keys_dir]
                directory.
            valid_pattern:
                A string, regex `Pattern`, or function for determining whether a
                given input `str` fits the expected pattern for this secret.
                Will be used to validate the secret's data before encryption and after
                decryption. If omitted, **any string** will be considered "valid data".
        """
        if (not uid) or (not str(uid).isidentifier()):
            raise ValueError("Unique ID (uid) must be a valid non-empty identifier.")

        def get_storage_directory() -> Path:
            """Turns storage_directory into a valid Path, creating the dir if needed."""
            nonlocal storage_directory

            if not storage_directory:
                storage_directory = Metadata.get_default_keys_dir()
            elif isinstance(storage_directory, str):
                storage_directory = Path(storage_directory)

            if (storage_directory := storage_directory.resolve()).is_file():
                raise ValueError(
                    f'Expected a directory, but found a file: "{storage_directory}"'
                )

            storage_directory.mkdir(exist_ok=True, parents=True)
            return storage_directory

        def get_validator() -> Callable[[str], bool]:
            """Turns valid_pattern into a function that takes a str & returns a bool."""
            nonlocal valid_pattern

            if not valid_pattern:
                valid_pattern = re.compile(".*", re.DOTALL)
            elif isinstance(valid_pattern, str):
                valid_pattern = re.compile(valid_pattern)

            def validate_pattern(text: str) -> bool:
                """Returns `True` if the given text fits the pattern for this secret."""
                if isinstance(valid_pattern, re.Pattern):
                    return valid_pattern.fullmatch(text) is not None
                else:
                    return bool(cast(Callable, valid_pattern)(text))

            return validate_pattern

        self.uid: Final[str] = str(uid)
        self.requires_password: Final[bool] = requires_password
        self.display_name: Final[str] = display_name or uid
        self.storage_directory: Final[Path] = get_storage_directory()
        self.validate: Final[Callable[[str], bool]] = get_validator()

    def __str__(self) -> str:
        """Returns a nicely-printable string representation of this secret."""
        return self.display_name

    @property
    def file_path(self) -> Path:
        """The path of the file that may contain this secret's encrypted data.

        This property will only return the `content` file path, as the `fernet` file is
        irrelevant outside of this class. The return value will be an instance of
        `pathlib.Path`, but it is **not** guaranteed to point to an existing file
        (e.g. if this secret hasn't been created/saved yet, or has been deleted).
        """
        return self._get_key_file("content")

    @property
    def min_pw_length(self) -> int:
        """The minimum length for this secret's password, if one is required.

        For secrets that require a password, this property will return `8`
        (chosen arbitrarily to try and balance security vs. convenience).
        For secrets that don't require a password, this will return `0`.
        """
        return 8 if self.requires_password else 0

    def clear(self) -> None:
        """Deletes all files containing data related to this secret, if any exist.

        This method **does not** scan the entire system to locate the files for a secret
        - it only checks the [`storage_directory`][botstrap.internal.Secret.__init__]
        that was specified upon instantiation.

        ??? tip "Tip - Don't scramble your secrets!"
            If a secret's [`.key`](./#key-files) files are renamed or moved out of their
            original directory without a corresponding change to the `uid` and/or
            `storage_directory` constructor parameters (or vice versa), then the secret
            will behave as if there are no existing files associated with it.
            Fortunately, this can easily be resolved by either moving the files back
            into place or updating the constructor parameters in your code.
        """
        for qualifier in get_args(_KeyQualifier):
            key_file = self._get_key_file(qualifier)
            key_file.unlink(missing_ok=True)

    def read(self, password: str | None = None) -> str | None:
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

    def write(self, data: str, password: str | None = None) -> None:
        """Encrypts and writes the data to a file, optionally protected by a password.

        If the `password` param is provided, it must be at least `8` characters long
        (see [`min_pw_length`][botstrap.internal.Secret.min_pw_length]) and will have to
        be provided again whenever [`read()`][botstrap.internal.Secret.read] is invoked
        to decrypt this secret.

        Omitting the `password` parameter means that only the secret's two
        [`.key`](./#key-files) files will be required in order to decrypt it.
        This is both more convenient *and* more dangerous, so choose wisely. :genie:

        Args:
            data:
                A string containing sensitive information to be encrypted before being
                stored in a file.
            password:
                An optional string that can improve the [security](./#passwords)
                of this secret. If omitted, a password will not be factored into
                the encryption algorithm for this secret.

        Raises:
            ValueError: If the `data` is not considered valid according to the
                [`valid_pattern`][botstrap.internal.Secret.__init__]
                that was specified when this secret was instantiated.
        """
        if not self.validate(data):
            raise ValueError(f'Attempted to write invalid data for "{self.uid}".')
        self.file_path.write_bytes(self._get_fernet(password).encrypt(data.encode()))

    def _get_key_file(self, qualifier: _KeyQualifier) -> Path:
        """Returns the `Path` to the qualified (content/fernet) file for this secret."""
        if (file := self.storage_directory / f".{self.uid}.{qualifier}.key").is_dir():
            dir_path = file.resolve()
            raise ValueError(f'Expected a file, but found a directory: "{dir_path}"')
        return file

    def _get_fernet(self, password: str | None) -> Fernet:
        """Returns a `Fernet` instance for encrypting and decrypting `bytes` data."""
        if self.requires_password:
            if not password:
                raise ValueError(f'Password is required to read/write "{self.uid}".')
            elif not isinstance(password, str):
                raise TypeError(f"Password type must be {str}, not {type(password)}.")
            elif len(password) < (length := self.min_pw_length):
                raise ValueError(f"Password must be at least {length} characters long.")
        elif password:
            raise ValueError(f'Unexpectedly received a password for "{self.uid}".')

        def get_extra_bytes(get_initial_bytes: Callable[[], bytes]) -> bytes:
            if not (fernet_file := self._get_key_file("fernet")).is_file():
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
