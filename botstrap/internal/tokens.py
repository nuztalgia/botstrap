from __future__ import annotations

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
    def __init__(
        self,
        manager: CliManager,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
    ) -> None:
        super().__init__(
            uid=uid,
            requires_password=requires_password,
            display_name=display_name,
            storage_directory=storage_directory,
            valid_pattern=_PATTERN.fullmatch,
        )
        self.manager: Final[CliManager] = manager

    def resolve(self, create_if_missing: bool) -> str | None:
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

        if not create_if_missing:
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

    def format_bot_token_text(bot_token_text: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return _PLACEHOLDER if token.validate(bot_token_text) else ""

    print(strings.t_create_cue)
    token_input = cli.get_hidden_input(strings.t_prompt, format_bot_token_text)

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
