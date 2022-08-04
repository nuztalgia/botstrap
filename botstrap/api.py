from __future__ import annotations

from pathlib import Path
from typing import Final

from botstrap.internal import CliManager, Metadata, Strings, ThemeColors, Token

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

    def retrieve_active_token(
        self,
        create_if_missing: bool = True,
        silent: bool = False,
    ) -> str | None:
        _, token_value = self._process_tokens(create_if_missing, silent)
        return token_value

    def run_bot(
        self,
        bot_class: str | type = "discord.Bot",
        create_token_if_missing: bool = True,
        **bot_options,
    ) -> None:
        original_bot_class = bot_class
        if isinstance(bot_class, str):
            bot_class = Metadata.import_class(bot_class) or ""

        if not isinstance(bot_class, type):
            raise TypeError(f'Unable to instantiate bot class: "{original_bot_class}"')

        token, token_value = self._process_tokens(create_token_if_missing)
        if token and token_value:
            self._init_bot(token.display_name, token_value, bot_class, **bot_options)

    def _process_tokens(
        self,
        create_if_missing: bool = True,
        silent: bool = False,
    ) -> tuple[Token | None, str | None]:
        if not self._tokens_by_uid:
            if create_if_missing:
                uid = _DEFAULT_TOKEN_NAME
                self.register_token(uid=uid, display_name=self.colors.highlight(uid))
            elif silent:
                return None, None
            else:
                raise RuntimeError("There are no registered tokens to read data from.")

        # TODO: Properly select the token to use (i.e. from command-line args).
        token, token_value = next(iter(self._tokens_by_uid.values())), None

        try:
            token_value = token.resolve(create_if_missing)
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()

        return token, token_value

    def _init_bot(
        self, token_label: str, token_value: str, bot_class: type, **bot_options
    ) -> None:
        bot = bot_class(**bot_options)

        @bot.event
        async def on_connect():
            bot_name = getattr(bot, "user", type(bot).__name__)
            self._print_prefixed_message(
                self.strings.discord_login_success.substitute(
                    token_label=token_label,
                    bot_identifier=self.colors.highlight(bot_name),
                )
            )

        self._print_prefixed_message(
            self.strings.discord_login_attempt.substitute(token_label=token_label),
            suppress_newline=True,
        )

        try:
            bot.run(token_value)
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt()
        except Metadata.import_class("discord.LoginFailure"):  # type: ignore[misc]
            self._print_prefixed_message(is_error=True)  # Print error prefix only.
            self.cli.exit_process(self.strings.discord_login_failure)

    def _handle_keyboard_interrupt(self) -> None:
        self.cli.exit_process(self.strings.exit_keyboard_interrupt, is_error=False)
