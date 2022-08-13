"""This module contains a class and helper functions for handling Discord bot tokens."""
import re
from pathlib import Path
from typing import Final

from cryptography.fernet import InvalidToken

from botstrap.internal.cmdline import CliManager
from botstrap.internal.secrets import Secret

_LENGTHS: Final[tuple[int, ...]] = (24, 6, 27)
_PATTERN: Final[re.Pattern] = re.compile(r"\.".join(r"[\w-]{%i}" % i for i in _LENGTHS))
_PLACEHOLDER: Final[str] = ".".join("*" * i for i in _LENGTHS)


class Token(Secret):
    """A subclass of `Secret` that represents an individual Discord bot token."""

    def __init__(
        self,
        manager: CliManager,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
    ) -> None:
        """Initializes a new `Token` instance.

        Args:
            manager:
                A `CliManager` specifying the UX to be used by the CLI.
            uid:
                A unique string identifying this token. Will be used in the names of
                the files containing this token's data.
            requires_password:
                Whether a password is required in order to create and subsequently
                retrieve this token.
            display_name:
                A human-readable string describing this token. Will be displayed in the
                CLI when referring to this token. If omitted, the `uid` will be
                displayed instead.
            storage_directory:
                Where to store the encrypted `.key` files containing this token's data.
                If omitted, the files will be saved in a folder named `.botstrap_keys`,
                which will be created in the same location as the file containing the
                `"__main__"` module for the executing script.
        """
        super().__init__(
            uid=uid,
            requires_password=requires_password,
            display_name=display_name,
            storage_directory=storage_directory,
            valid_pattern=_PATTERN.fullmatch,
        )
        self.manager: Final[CliManager] = manager

    def resolve(self, allow_token_creation: bool) -> str | None:
        """Returns this token's data, interactively requesting user input if needed.

        The primary advantage of this method over the superclass methods `read()` and
        `write()` is that it can interact with the user via the CLI and take different
        code paths according to the input it may receive. This allows it to:

          * Automatically retrieve the decrypted token if no password is required
          * Prompt the user for a password to decrypt the token, if one is required
          * Notify the user about errors such as password mismatches / nonexistent files
          * Ask whether the user wants to create a new token file, if one doesn't exist
          * Walk the user through the process of adding a new token (and password)
          * Let the user choose whether to exit / continue the process at various points

        Args:
            allow_token_creation:
                Whether to prompt the user to create a file for this token, if one
                doesn't already exist. If `True` and the user responds affirmatively,
                they will be asked to input the token data, and then create a password
                for it (if `requires_password` was set to `True` when this token was
                instantiated).

        Returns:
            The token value if it exists and can be decrypted, otherwise `None`.
        """
        cli, strings = self.manager.cli, self.manager.strings

        if self.file_path.is_file():
            if self.requires_password:
                cli.print_prefixed_message(strings.p_cue.substitute(token=self))
                password = cli.get_hidden_input(strings.p_prompt)
            else:
                password = None

            try:
                return self.read(password=password)
            except (InvalidToken, ValueError):
                message = strings.t_mismatch.substitute(token=self)
                cli.print_prefixed_message(message, is_error=True)
                if self.requires_password:
                    print(strings.p_mismatch)
                return None

        if not allow_token_creation:
            message = strings.t_missing.substitute(token=self)
            cli.print_prefixed_message(message, is_error=True)
            return None

        cli.print_prefixed_message()
        cli.confirm_or_exit(strings.t_create.substitute(token=self))

        self.write(
            data=(bot_token := _get_new_bot_token(self)),
            password=_get_new_password(self) if self.requires_password else None,
        )

        print(self.manager.colors.success(strings.t_create_success))
        cli.confirm_or_exit(strings.t_create_use)

        return bot_token


def _get_new_bot_token(token: Token) -> str:
    cli, strings = token.manager.cli, token.manager.strings

    def format_input(user_input: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return _PLACEHOLDER if token.validate(user_input) else ""

    print(strings.t_create_cue)
    token_input = cli.get_hidden_input(strings.t_prompt, format_input)

    if not token.validate(token_input):
        print(strings.t_create_hint)
        print(token.manager.colors.lowlight(f"{strings.t_prompt}: {_PLACEHOLDER}"))
        cli.exit_process(strings.t_create_mismatch)

    return token_input


def _get_new_password(token: Token) -> str:
    cli, strings = token.manager.cli, token.manager.strings
    min_length = token.minimum_password_length

    print(strings.p_create_info.substitute(token=token))
    print(strings.p_create_cue.substitute(token=token))

    while len(password_input := cli.get_hidden_input(strings.p_prompt)) < min_length:
        hint = strings.p_create_hint.substitute(min_length=min_length)
        print(token.manager.colors.warning(hint))
        cli.confirm_or_exit(strings.p_create_retry)

    print(strings.p_confirm_cue)
    while cli.get_hidden_input(strings.p_prompt) != password_input:
        print(token.manager.colors.warning(strings.p_confirm_hint))
        cli.confirm_or_exit(strings.p_confirm_retry)

    return password_input
