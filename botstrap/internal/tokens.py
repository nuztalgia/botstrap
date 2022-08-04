from __future__ import annotations

import re
from pathlib import Path
from string import Template
from typing import Final, Iterable

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
        cli, colors, s = self.manager.cli, self.manager.colors, self.manager.strings

        # noinspection PyProtectedMember
        print_prefixed = self.manager._print_prefixed_message

        if self.file_path.is_file():
            if self.requires_password:
                print_prefixed(_sub_token(s.password_cue, self))
                password = cli.get_hidden_input(s.password_prompt)
            else:
                password = None

            try:
                return self.read(password=password)
            except (InvalidToken, ValueError):
                print_prefixed(_sub_token(s.bot_token_mismatch, self), is_error=True)
                if self.requires_password:
                    print(colors.lowlight(s.password_mismatch))
                return None

        if not create_if_missing:
            print_prefixed(_sub_token(s.bot_token_missing, self), is_error=True)
            return None

        print_prefixed()  # Print prefix and stay on the same line for the next message.
        cli.confirm_or_exit(_sub_token(s.bot_token_missing_add, self))

        self.write(
            data=(bot_token := _get_new_bot_token(self)),
            password=_get_new_password(self) if self.requires_password else None,
        )

        print(colors.success(s.bot_token_creation_success))
        cli.confirm_or_exit(s.bot_token_creation_run)

        return bot_token


def manage_tokens(manager: CliManager, tokens: Iterable[Token]) -> None:
    cli, colors, s = manager.cli, manager.colors, manager.strings

    while saved_tokens := [token for token in tokens if token.file_path.is_file()]:
        print(s.bot_token_mgmt_list)
        for token in saved_tokens:
            print(f"  * {colors.highlight(token.uid)} -> {token.file_path}")

        cli.confirm_or_exit(s.bot_token_mgmt_delete)
        uids = [token.uid for token in saved_tokens]

        while (uid := cli.get_input(s.bot_token_deletion_cue)) not in uids:
            print(colors.warning(s.bot_token_deletion_mismatch))
            print(s.bot_token_deletion_hint.substitute(examples=uids))
            cli.confirm_or_exit(s.bot_token_deletion_retry)

        next(token for token in tokens if token.uid == uid).clear()
        print(colors.success(s.bot_token_deletion_success))

    print(s.bot_token_mgmt_none)


def _matches_token_pattern(text: str) -> bool:
    return bool(_PATTERN.fullmatch(text))


def _sub_token(template: Template, token: Token) -> str:
    return template.substitute(token_label=token.display_name)


def _get_new_bot_token(token: Token) -> str:
    cli, colors, s = token.manager.cli, token.manager.colors, token.manager.strings

    def format_bot_token_text(bot_token_text: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return _PLACEHOLDER if _matches_token_pattern(bot_token_text) else ""

    print(s.bot_token_creation_cue)
    bot_token = cli.get_hidden_input(s.bot_token_prompt, format_bot_token_text)

    if not _matches_token_pattern(bot_token):
        print(s.bot_token_creation_hint)
        print(colors.lowlight(f"{s.bot_token_prompt}: {_PLACEHOLDER}"))
        cli.exit_process(s.bot_token_creation_mismatch)

    return bot_token


def _get_new_password(token: Token) -> str:
    cli, colors, s = token.manager.cli, token.manager.colors, token.manager.strings
    min_length = type(token).MINIMUM_PASSWORD_LENGTH

    print(_sub_token(s.password_creation_info, token))
    print(_sub_token(s.password_creation_cue, token))

    while len(password := cli.get_hidden_input(s.password_prompt)) < min_length:
        hint = s.password_creation_hint.substitute(min_length=min_length)
        cli.confirm_or_exit(f"{colors.warning(hint)}\n{s.password_creation_retry}")

    print(s.password_confirmation_cue)  # lgtm[py/clear-text-logging-sensitive-data]
    while cli.get_hidden_input(s.password_prompt) != password:
        print(colors.warning(s.password_confirmation_hint))
        cli.confirm_or_exit(s.password_confirmation_retry)

    return password
