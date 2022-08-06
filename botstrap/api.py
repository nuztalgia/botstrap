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
    """The primary API for bot token storage, retrieval, and management.

    This class contains methods that facilitate the simple and secure handling of
    Discord bot tokens. It maintains a token registry to enable programmatic declaration
    of expected/allowed tokens, and provides a CLI for interactive addition and deletion
    of encrypted token data. This class also maintains some state corresponding to its
    constructor arguments, which collectively ensure a consistent look and feel for the
    aforementioned CLI.

    Args:
        name:
            An optional string containing the name of your bot. If omitted or empty,
            Botstrap will try to determine an appropriate name from module and/or file
            metadata. If unsuccessful, it will simply use the default name: "bot".
        colors:
            A `ThemeColors` instance specifying the colors to be used by the CLI for
            this Botstrap integration. Defaults to commonly-used colors (e.g. green for
            success, red for error). Set this to `ThemeColors.off()` to disable colors.
        strings:
            A `Strings` instance specifying the strings to be used by the CLI for this
            Botstrap integration. Defaults to English text with liberal spacing for
            readability. Set this to `Strings.compact()` to disable superfluous spacing.
    """

    def __init__(
        self,
        name: str | None = None,
        colors: ThemeColors = ThemeColors.default(),
        strings: Strings = Strings.default(),
    ) -> None:
        name = name or Metadata.guess_program_name() or _DEFAULT_PROGRAM_NAME
        super().__init__(name, colors, strings)
        self._tokens_by_uid: Final[dict[str, Token]] = {}
        self._active_token: Token | None = None

    def register_token(
        self,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
        allow_overwrites: bool = False,
    ) -> Botstrap:
        """Defines a token to be managed by this Botstrap integration.

        After creating a `Botstrap` instance and before calling any of the other API
        methods, this method should be called once for each unique token that may be
        used by your bot. If only one token is required, you may skip this step, and a
        basic "default" token will be automatically registered.

        This method does not have anything to do with the actual "secret data" for the
        token, which may or may not exist at the time this method is called. Rather, it
        is a way to declare the token's usage and display characteristics. The "secret
        data" will be requested interactively and securely through the CLI only if/when
        the token is actually needed, at which point it will be encrypted and saved for
        future use.

        Example:
            >>> from botstrap import Botstrap, Color
            >>>
            >>> Botstrap().register_token(
            >>>     uid="dev",
            >>>     display_name=Color.yellow("development"),
            >>> ).register_token(
            >>>     uid="prod",
            >>>     requires_password=True,
            >>>     display_name=Color.green("production"),
            >>> )

        Args:
            uid:
                A unique string identifying this token. Will be used as a file name for
                the encrypted `.key` files containing this token's data.
            requires_password:
                Whether a user-provided password is required in order to create and/or
                retrieve this token. Defaults to `False`.
            display_name:
                A human-readable string describing this token. May include formatting
                characters, such as those provided by `Color` methods. Will be displayed
                in the CLI when referring to this token. If omitted, the `uid` for this
                token will be displayed instead.
            storage_directory:
                The location in which to store the encrypted `.key` files containing the
                data for this token. If omitted, the files will be placed in a directory
                named ".botstrap_keys", which will be created in the same location as
                the file containing the `__main__` module for the executing script.
            allow_overwrites:
                Whether to allow this token to be registered even if `uid` belongs to a
                token that has already been registered. If `True`, this token will
                overwrite the previously registered token. Defaults to `False`.

        Returns:
            This `Botstrap` instance, to allow chaining method calls.

        Raises:
            ValueError:
                If `storage_directory` does not point to a valid directory (e.g. is
                nonexistent or points to a file), OR if `allow_overwrites` is `False`
                and `uid` belongs to a token that has already been registered.
        """
        token = Token(self, uid, requires_password, display_name, storage_directory)
        if (not allow_overwrites) and (token.uid in self._tokens_by_uid):
            raise ValueError(f'A token with unique ID "{token.uid}" already exists.')
        self._tokens_by_uid[token.uid] = token
        return self

    def parse_args(
        self,
        *,
        description: str | None = None,
        version: str | None = None,
    ) -> Botstrap:
        """Parses any arguments and options passed in via the command line.

        This method should only be called after all expected tokens have been defined
        with `register_token()`, in order to ensure that the "active" token can be
        correctly determined from command-line arguments to your bot script.

        If your bot doesn't require the customization provided by the parameters to this
        method, you may skip calling this method so long as `allow_auto_parse_args` is
        set to `True` (its default value) in any subsequent API method calls.

        Example:
            >>> from botstrap import Botstrap
            >>>
            >>> Botstrap().parse_args(
            >>>     description="A really cool Discord bot that uses Botstrap!"
            >>> )

            $ python coolbot.py -h
            usage: python coolbot.py [--help] [-t]

              A really cool Discord bot that uses Botstrap!
              Run "python coolbot.py" with no parameters to start the bot.

            options:
              -t, --tokens  View/manage your saved Discord bot tokens.
              -h, --help    Display this help message.

        Args:
            description:
                An optional string containing a short human-readable description/summary
                of your bot. May include formatting characters. Will be displayed when
                the `--help` option is specified on the command line, along with some
                usage instructions for running your bot. If omitted or empty, Botstrap
                will try to populate this field from package metadata (if available).
                Otherwise, only the usage instructions will be displayed.
            version:
                An optional string representing the version of your bot. May include
                formatting characters. Will be displayed when the `--version` option is
                specified on the command line. If omitted or empty, the `--version`
                option will not be available (as is the case in the example above).

        Returns:
            This `Botstrap` instance, to allow chaining method calls.

        Raises:
            SystemExit:
                If a command-line option was specified that calls for an alternative
                program flow and exits upon completion (e.g. `--help`, `--version`).
        """
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
