from __future__ import annotations

import re
from pathlib import Path
from string import Template
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
            valid_pattern=_matches_token_pattern,
        )
        self.manager: Final[CliManager] = manager

    def resolve(self, create_if_missing: bool) -> str | None:
        cli, colors, strings = (mgr := self.manager).cli, mgr.colors, mgr.strings

        if self.file_path.is_file():
            if self.requires_password:
                cli.print_prefixed_message(self._substitute_into(strings.password_cue))
                password = cli.get_hidden_input(strings.password_prompt)
            else:
                password = None

            try:
                return self.read(password=password)
            except (InvalidToken, ValueError):
                message = self._substitute_into(strings.bot_token_mismatch)
                cli.print_prefixed_message(message, is_error=True)
                if self.requires_password:
                    print(colors.lowlight(strings.password_mismatch))
                return None

        if not create_if_missing:
            message = self._substitute_into(strings.bot_token_missing)
            cli.print_prefixed_message(message, is_error=True)
            return None

        cli.print_prefixed_message()  # Print prefix only; continue on the same line.
        cli.confirm_or_exit(self._substitute_into(strings.bot_token_missing_add))

        self.write(
            data=(bot_token := _get_new_bot_token(self)),
            password=_get_new_password(self) if self.requires_password else None,
        )

        print(colors.success(strings.bot_token_creation_success))
        cli.confirm_or_exit(strings.bot_token_creation_run)

        return bot_token

    def _substitute_into(self, template: Template) -> str:
        return template.substitute(token_label=self.display_name)


def _matches_token_pattern(text: str) -> bool:
    return bool(_PATTERN.fullmatch(text))


def _get_new_bot_token(token: Token) -> str:
    cli, colors, strings = (mgr := token.manager).cli, mgr.colors, mgr.strings

    def format_bot_token_text(bot_token_text: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return _PLACEHOLDER if _matches_token_pattern(bot_token_text) else ""

    print(strings.bot_token_creation_cue)
    bot_token = cli.get_hidden_input(strings.bot_token_prompt, format_bot_token_text)

    if not _matches_token_pattern(bot_token):
        print(strings.bot_token_creation_hint)
        print(colors.lowlight(f"{strings.bot_token_prompt}: {_PLACEHOLDER}"))
        cli.exit_process(strings.bot_token_creation_mismatch)

    return bot_token


def _get_new_password(token: Token) -> str:
    cli, colors, strings = (mgr := token.manager).cli, mgr.colors, mgr.strings
    min_length = type(token).MINIMUM_PASSWORD_LENGTH

    # noinspection PyProtectedMember
    def print_password_creation_strings() -> None:
        print(token._substitute_into(strings.password_creation_info))
        print(token._substitute_into(strings.password_creation_cue))

    print_password_creation_strings()
    while len(password := cli.get_hidden_input(strings.password_prompt)) < min_length:
        msg = strings.password_creation_hint.substitute(min_length=min_length)
        cli.confirm_or_exit(f"{colors.warning(msg)}\n{strings.password_creation_retry}")

    print(strings.password_confirmation_cue)  # lgtm
    while cli.get_hidden_input(strings.password_prompt) != password:
        print(colors.warning(strings.password_confirmation_hint))
        cli.confirm_or_exit(strings.password_confirmation_retry)

    return password
