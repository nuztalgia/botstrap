from __future__ import annotations

from pathlib import Path
from typing import Final, Iterable

from botstrap.internal import (
    Argstrap,
    CliManager,
    Metadata,
    Strings,
    ThemeColors,
    Token,
)

_DEFAULT_PROGRAM_NAME: Final[str] = "bot"
_DEFAULT_TOKEN_NAME: Final[str] = "default"


class Botstrap(CliManager):
    def __init__(
        self,
        colors: ThemeColors = ThemeColors.default(),
        strings: Strings = Strings.default(),
        program_name: str | None = None,
    ) -> None:
        name = program_name or Metadata.guess_program_name() or _DEFAULT_PROGRAM_NAME
        super().__init__(name, colors, strings)
        self._tokens_by_uid: Final[dict[str, Token]] = {}
        self._active_token: Token | None = None

    def register_token(
        self,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
        silent: bool = False,
    ) -> Botstrap:
        token = Token(self, uid, requires_password, display_name, storage_directory)
        if (not silent) and (token.uid in self._tokens_by_uid):
            raise ValueError(f'A token with unique ID "{token.uid}" already exists.')
        self._tokens_by_uid[token.uid] = token
        return self

    def parse_args(
        self,
        description: str | None = None,
        version: str | None = None,
    ) -> Botstrap:
        args = Argstrap(
            manager=self,
            description=description,
            version=version,
            registered_tokens=(tokens := list(self._tokens_by_uid.values())),
        ).parse_args()

        if version and args.version:
            print(version)
        elif tokens and args.manage_tokens:
            self._manage_tokens(tokens)
        else:
            self._active_token = (
                tokens[0] if (len(tokens) == 1) else self._tokens_by_uid[args.token]
            )
            return self  # This is the only path that will continue program execution.

        raise SystemExit(0)  # Exit successfully if another path was taken & completed.

    def retrieve_active_token(
        self,
        *,
        allow_auto_register_token: bool = True,
        allow_auto_parse_args: bool = True,
        allow_token_creation: bool = True,
    ) -> str | None:
        if not self._tokens_by_uid:
            if allow_auto_register_token:
                uid = _DEFAULT_TOKEN_NAME
                self.register_token(uid=uid, display_name=self.colors.highlight(uid))
            else:
                raise RuntimeError(
                    "There are no registered tokens to retrieve.\nTo fix this, you can "
                    "allow auto-register and/or explicitly call `register_token()`."
                )

        if not self._active_token:
            if allow_auto_parse_args:
                self.parse_args()
            else:
                raise RuntimeError(
                    "Cannot confirm active token (args were not parsed).\nTo fix this, "
                    "you can allow auto-parse and/or explicitly call `parse_args()`."
                )

        if token := self._active_token:
            try:
                return token.resolve(create_if_missing=allow_token_creation)
            except KeyboardInterrupt:
                self._handle_keyboard_interrupt()

        return None

    def run_bot(self, bot_class: str | type = "discord.Bot", **options) -> None:
        token_value = self.retrieve_active_token(
            allow_auto_register_token=options.pop("allow_auto_register_token", True),
            allow_auto_parse_args=options.pop("allow_auto_parse_args", True),
            allow_token_creation=options.pop("allow_token_creation", True),
        )
        original_bot_class = bot_class

        if isinstance(bot_class, str):
            bot_class = Metadata.import_class(bot_class) or ""

        if not isinstance(bot_class, type):
            raise TypeError(f'Unable to instantiate bot class: "{original_bot_class}"')

        if token_value:
            self._init_bot(token_value, bot_class, **options)

    def _handle_keyboard_interrupt(self) -> None:
        self.cli.exit_process(self.strings.exit_keyboard_interrupt, is_error=False)

    def _init_bot(self, token_value: str, bot_class: type, **options) -> None:
        bot = bot_class(**options)
        token_label = (
            token.display_name if (token := self._active_token) else _DEFAULT_TOKEN_NAME
        )

        @bot.event
        async def on_connect():
            bot_name = getattr(bot, "user", type(bot).__name__)
            self.cli.print_prefixed_message(
                self.strings.discord_login_success.substitute(
                    token_label=token_label,
                    bot_identifier=self.colors.highlight(bot_name),
                )
            )

        self.cli.print_prefixed_message(
            self.strings.discord_login_attempt.substitute(token_label=token_label),
            suppress_newline=True,
        )

        try:
            bot.run(token_value)
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()
        except Metadata.import_class("discord.LoginFailure"):  # type: ignore[misc]
            self.cli.print_prefixed_message(is_error=True)  # Print error prefix only.
            self.cli.exit_process(self.strings.discord_login_failure)

    def _manage_tokens(self, tokens: Iterable[Token]) -> None:
        while saved_tokens := [token for token in tokens if token.file_path.is_file()]:
            self.cli.print_prefixed_message(self.strings.bot_token_mgmt_list)

            for count, token in enumerate(saved_tokens, start=1):
                index = str(token.file_path).rindex(token.uid) + len(token.uid)
                path = self.colors.lowlight(f"{str(token.file_path)[:index]}.*")
                print(f"  {count}) {self.colors.highlight(token.uid)} -> {path}")

            self.cli.confirm_or_exit(self.strings.bot_token_mgmt_delete)

            uids = [token.uid for token in saved_tokens]
            prompt = self.strings.bot_token_deletion_cue

            while (uid := self.cli.get_input(prompt)) not in uids:
                print(self.colors.warning(self.strings.bot_token_deletion_mismatch))
                print(self.strings.bot_token_deletion_hint.substitute(examples=uids))
                self.cli.confirm_or_exit(self.strings.bot_token_deletion_retry)

            next(token for token in tokens if token.uid == uid).clear()
            print(self.colors.success(self.strings.bot_token_deletion_success))

        self.cli.print_prefixed_message(self.strings.bot_token_mgmt_none)
