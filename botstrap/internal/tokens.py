"""This module contains the `Token` class, which represents a Discord bot token."""
import re
from pathlib import Path
from typing import Final

from cryptography.fernet import InvalidToken

from botstrap.internal.clisession import CliSession
from botstrap.internal.secrets import Secret

_LENGTHS: Final[tuple[int, ...]] = (24, 6, 27)
_PATTERN: Final[re.Pattern] = re.compile(r"\.".join(r"[\w-]{%i}" % i for i in _LENGTHS))


class Token(Secret):
    """Represents and handles operations for an individual Discord bot token.

    This class effectively combines the functionality provided by
    [`Secret`][botstrap.internal.secrets.Secret] (its parent class) and a
    [`CliSession`][botstrap.internal.clisession.CliSession] (passed in upon
    instantiation) to deliver a secure and user-friendly interface for managing a
    bot token. It only has one method -
    [`resolve()`][botstrap.internal.tokens.Token.resolve]
    - but currently, that's all it needs.
    """

    def __init__(
        self,
        cli: CliSession,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
    ) -> None:
        """Initializes a new `Token` instance.

        Args:
            cli:
                A `CliSession` providing the UX used by the CLI.
            uid:
                A unique string identifying this token. Will be used in the names of
                the files holding this token's data.
            requires_password:
                Whether a user-provided password is required to store and subsequently
                retrieve this token's value.
            display_name:
                A human-readable string describing this token. Will be displayed in
                the CLI when referring to this token. If omitted, the `uid` will be
                displayed instead.
            storage_directory:
                Where to store the encrypted files containing this token's data. If
                omitted, the files will be saved in a directory named `.botstrap_keys`,
                which will be created in the same location as the file containing the
                `#!py "__main__"` module for the executing script.
        """
        super().__init__(
            uid=uid,
            requires_password=requires_password,
            display_name=display_name,
            storage_directory=storage_directory,
            valid_pattern=_PATTERN.fullmatch,
        )
        self.cli: Final[CliSession] = cli

    def resolve(self, allow_token_creation: bool = True) -> str | None:
        """Returns the value of this token, interactively prompting for input if needed.

        The main advantage of this method over the superclass methods
        [`read()`][botstrap.internal.secrets.Secret.read] and
        [`write()`][botstrap.internal.secrets.Secret.write] is that it can interact with
        the user via the CLI and take different code paths according to their input.

        ??? info resolve-info "Info - Tasks performed by this method"
            Based on a combination of this token's state and the input provided by the
            user, this method can:

            - [x] Automatically decrypt and return the token's value, if no password
                  is required
            - [x] Prompt the user for a password if required by the token, then
                  return the decrypted value if successful
            - [x] Ask whether the user wants to create and encrypt a new file for
                  the token, if it doesn't already exist
            - [x] Walk the user through the process of creating a new token file
                  (and its password, if required)
            - [x] Notify the user about errors (in case of password mismatches,
                  missing files, etc.)
            - [x] Let the user choose whether to continue or exit the process at
                  various points throughout this flow

            This might sound like a lot, but the implementation is actually quite
            straightforward and (probably) more concise than this description might lead
            you to believe. Check out the source code <a href="#line-0-120">below</a>
            to see for yourself. :eyes:

        Args:
            allow_token_creation:
                Whether to interactively prompt the user to create (i.e. add and
                encrypt) the file for this token, if it hasn't already been created.
                If this is `False` and the file doesn't exist, this method will
                return `None`.

        Returns:
            The token value if it exists and can be decrypted, otherwise `None`.
        """
        if self.file_path.is_file():
            if self.requires_password:
                self.cli.print_prefixed(self.cli.strings.p_cue.substitute(token=self))
                password = self.cli.get_hidden_input(self.cli.strings.p_prompt)
            else:
                password = None

            try:
                return self.read(password=password)
            except (InvalidToken, ValueError):
                message = self.cli.strings.t_mismatch.substitute(token=self)
                self.cli.print_prefixed(message, is_error=True)
                if self.requires_password:
                    print(self.cli.strings.p_mismatch)
                return None

        if not allow_token_creation:
            message = self.cli.strings.t_missing.substitute(token=self)
            self.cli.print_prefixed(message, is_error=True)
            return None

        self.cli.print_prefixed()
        self.cli.confirm_or_exit(self.cli.strings.t_create.substitute(token=self))

        self.write(
            data=(token := _get_new_token(self)),
            password=_get_new_password(self) if self.requires_password else None,
        )

        print(self.cli.colors.success(self.cli.strings.t_create_success))
        self.cli.confirm_or_exit(self.cli.strings.t_create_use)

        return token


def _get_new_token(token: Token) -> str:
    """Prompts the user to provide a valid bot token string, and then returns it."""
    placeholder = ".".join("*" * i for i in _LENGTHS)

    def format_input(user_input: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return placeholder if token.validate(user_input) else ""

    print(token.cli.strings.t_create_cue)
    token_input = token.cli.get_hidden_input(token.cli.strings.t_prompt, format_input)

    if not token.validate(token_input):
        print(token.cli.strings.t_create_hint)
        print(token.cli.colors.lowlight(f"{token.cli.strings.t_prompt}: {placeholder}"))
        token.cli.exit_process(token.cli.strings.t_create_mismatch)

    return token_input


def _get_new_password(token: Token) -> str:
    """Prompts the user to provide a valid password string, and then returns it."""
    print(token.cli.strings.p_create_info.substitute(token=token))
    print(token.cli.strings.p_create_cue.substitute(token=token))

    prompt, min_length = token.cli.strings.p_prompt, token.min_pw_length

    while len(password_input := token.cli.get_hidden_input(prompt)) < min_length:
        hint = token.cli.strings.p_create_hint.substitute(min_length=min_length)
        print(token.cli.colors.warning(hint))
        token.cli.confirm_or_exit(token.cli.strings.p_create_retry)

    print(token.cli.strings.p_confirm_cue)
    while token.cli.get_hidden_input(token.cli.strings.p_prompt) != password_input:
        print(token.cli.colors.warning(token.cli.strings.p_confirm_hint))
        token.cli.confirm_or_exit(token.cli.strings.p_confirm_retry)

    return password_input
