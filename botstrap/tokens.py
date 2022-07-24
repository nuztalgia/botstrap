from __future__ import annotations

import re
from pathlib import Path
from string import Template
from typing import Final

from cryptography.fernet import InvalidToken

from botstrap.colors import Colors
from botstrap.secrets import Secret
from botstrap.strings import Strings
from botstrap.userflow import confirm_or_exit, exit_process, get_hidden_input

_LENGTHS: Final[tuple[int, ...]] = (24, 6, 27)
_PATTERN: Final[re.Pattern] = re.compile(r"\.".join(r"[\w-]{%i}" % i for i in _LENGTHS))
_PLACEHOLDER: Final[str] = ".".join("*" * i for i in _LENGTHS)


class Token(Secret):
    def __init__(
        self,
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

    @classmethod
    def default_dev(cls) -> Token:
        return cls(
            uid="dev",
            requires_password=False,
            display_name=Colors.yellow("development"),
        )

    @classmethod
    def default_prod(cls) -> Token:
        return cls(
            uid="prod",
            requires_password=True,
            display_name=Colors.green("production"),
        )

    def resolve(
        self,
        create_if_missing: bool = True,
        error_msg_prefix: str = "\n",
        strings: Strings = Strings.default(),
        colors: Colors = Colors.default(),
    ) -> str | None:
        if self.file_path.is_file():
            if self.requires_password:
                print(_sub_token(strings.password_cue, self))
                password = get_hidden_input(colors, strings.password_prompt)
            else:
                password = None

            try:
                return self.read(password=password)
            except (InvalidToken, ValueError):
                print(error_msg_prefix + _sub_token(strings.bot_token_mismatch, self))
                if self.requires_password:
                    print(strings.password_mismatch)
                return None

        if not create_if_missing:
            print(error_msg_prefix + _sub_token(strings.bot_token_missing, self))
            return None

        confirm_or_exit(
            strings, colors, _sub_token(strings.bot_token_missing_add, self)
        )

        self.write(
            data=(bot_token := _get_new_bot_token(strings, colors)),
            password=(
                _get_new_password(strings, colors, self)
                if self.requires_password
                else None
            ),
        )

        print(colors.success(strings.bot_token_creation_success))
        confirm_or_exit(strings, colors, strings.bot_token_creation_run)

        return bot_token


def _matches_token_pattern(text: str) -> bool:
    return bool(_PATTERN.fullmatch(text))


def _sub_token(template: Template, token: Token) -> str:
    return template.substitute(token_label=token.display_name)


def _get_new_bot_token(strings: Strings, colors: Colors) -> str:
    def format_token_text(bot_token_text: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return _PLACEHOLDER if _matches_token_pattern(bot_token_text) else ""

    print(strings.bot_token_creation_cue)
    bot_token = get_hidden_input(colors, strings.bot_token_prompt, format_token_text)

    if not _matches_token_pattern(bot_token):
        print(strings.bot_token_creation_hint)
        print(colors.lowlight(f"{strings.bot_token_prompt}: {_PLACEHOLDER}"))
        exit_process(strings, colors, strings.bot_token_creation_mismatch)

    return bot_token


def _get_new_password(strings: Strings, colors: Colors, token: Token) -> str:
    print(_sub_token(strings.password_creation_info, token))

    print(_sub_token(strings.password_creation_cue, token))
    length = type(token).MINIMUM_PASSWORD_LENGTH
    while len(password := get_hidden_input(colors, strings.password_prompt)) < length:
        hint_text = strings.password_creation_hint.substitute(min_length=length)
        print(colors.warning(hint_text))
        confirm_or_exit(strings, colors, strings.password_creation_retry)

    print(strings.password_confirmation_cue)
    while get_hidden_input(colors, strings.password_prompt) != password:
        print(colors.warning(strings.password_confirmation_hint))
        confirm_or_exit(strings, colors, strings.password_confirmation_retry)

    return password
