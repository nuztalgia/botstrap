from __future__ import annotations

from pathlib import Path
from typing import Final

from botstrap.colors import CliColors
from botstrap.internal import Argstrap, CliManager, Metadata, Token
from botstrap.strings import CliStrings

_DEFAULT_PROGRAM_NAME: Final[str] = "bot"
_DEFAULT_TOKEN_NAME: Final[str] = "default"


class BotstrapFlow(CliManager):
    """The primary flow for handling bot token storage, retrieval, and management.

    This class contains methods that facilitate the simple and secure handling of
    Discord bot tokens. It maintains a token registry to enable programmatic declaration
    of expected/allowed tokens, and provides a CLI for interactive addition and deletion
    of encrypted token data. This class also maintains some state corresponding to its
    constructor arguments, which collectively ensure a consistent look and feel for the
    aforementioned CLI.
    """

    def __init__(
        self,
        name: str | None = None,
        colors: CliColors = CliColors.default(),
        strings: CliStrings = CliStrings.default(),
    ) -> None:
        """Initializes a new `BotstrapFlow` instance.

        Args:
            name:
                The name of your bot. If omitted, Botstrap will try to determine an
                appropriate name from package and/or file metadata. If unsuccessful, it
                will use the default name: `#!py "bot"`.
            colors:
                The colors to be used by the CLI. Defaults to commonly-used colors (e.g.
                green for success, red for error). Set this to `CliColors.off()` to
                disable all colors.
            strings:
                The strings to be used by the CLI. Defaults to English text with ample
                vertical spacing for readability. Set this to `CliStrings.compact()` to
                minimize spacing.
        """
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
    ) -> BotstrapFlow:
        """Defines a token to be managed by this Botstrap integration.

        After creating a `BotstrapFlow` instance and before calling any of the other API
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
            ```py title="bot.py"
            from botstrap import BotstrapFlow, Color

            BotstrapFlow().register_token(
                uid="dev",
                display_name=Color.yellow("development"),
            ).register_token(
                uid="prod",
                requires_password=True,
                display_name=Color.green("production"),
            )
            ```

        Args:
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
                Where to store the files containing this token's data. If omitted, the
                files will be saved in a folder named `.botstrap_keys`, which will be
                created in the same location as the `#!py "__main__"` module of your
                script.
            allow_overwrites:
                Whether to allow this token to be registered even if `uid` already
                belongs to a registered token. If `True`, this token will clobber the
                previous token. If `False`, a `#!py ValueError` will be raised.

        Returns:
            This `BotstrapFlow` instance.

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
    ) -> BotstrapFlow:
        """Parses any arguments and options passed in via the command line.

        This method should only be called after all expected tokens have been defined
        with `register_token()`, in order to ensure that the "active token" can be
        correctly determined from command-line arguments to your bot script.

        If your bot doesn't require the customization provided by the parameters to this
        method, you may skip calling this method so long as `allow_auto_parse_args` is
        set to `True` (its default value) in any subsequent API method calls.

        Example:
            ```py title="bot.py"
            from botstrap import BotstrapFlow

            BotstrapFlow().parse_args(
                description="A really cool Discord bot that uses Botstrap!"
            )
            ```

            ```console title="Console Session" hl_lines="5"
            $ python bot.py -h

            usage: bot.py [--help] [-t]

              A really cool Discord bot that uses Botstrap!
              Run "python bot.py" with no parameters to start the bot.

            options:
              -t, --tokens  View/manage your saved Discord bot tokens.
              -h, --help    Display this help message.
            ```

        Args:
            description:
                A short human-readable description of your bot. Will be displayed when
                the `--help` option is passed to the CLI. If omitted, Botstrap will try
                to fill this field from package metadata. If unsuccessful, this line
                will be left blank.
            version:
                A string representing the current version of your bot. Will be displayed
                when the `--version` option is passed to the CLI. If omitted, that
                option will not be available in your bot's CLI.

        Returns:
            This `BotstrapFlow` instance.

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
        elif args.manage_tokens:
            self._manage_tokens(tokens)
        else:
            # If no tokens were manually registered, don't assign the active token here.
            # The default token will be used if/when a token is needed by other methods.
            if tokens:
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
        """Returns the value of the active token, if it exists and can be decrypted.

        The "active token" is the token that should be used to run your bot, taking into
        account all tokens that have been registered and any arguments that were passed
        in from the command line. If no custom tokens have been defined, this will be
        the basic "default" token, as in the example below.

        The "value" of the token is a string containing its decrypted data, which can be
        plugged into your bot's `run()` method to authenticate and start up your bot.
        This value should be kept secret and can be very damaging if leaked, so make
        sure you don't `print()` or otherwise log the result of this method.

        If your bot is modularly coded such that it can be "atomically" instantiated and
        run by `run_bot()`, consider using that method instead for brevity and safety.
        This method is provided for cases in which that isn't a viable option, but
        should be avoided if possible to prevent potential security mishaps.

        Example:
            ```py title="bot.py"
            from botstrap import BotstrapFlow

            BotstrapFlow(name="example-bot").retrieve_active_token()
            ```

            ```console title="Console Session"
            $ python bot.py

            example-bot: You currently don't have a saved default bot token.
            Would you like to add one now? If so, type "yes" or "y":
            ```

        Args:
            allow_auto_register_token:
                Whether to automatically register a simple `#!py "default"` token if no
                tokens have been manually registered.
            allow_auto_parse_args:
                Whether to automatically parse command-line options and args if
                [`parse_args()`][botstrap.BotstrapFlow.parse_args] has not been
                manually invoked.
            allow_token_creation:
                Whether to interactively prompt to create (i.e. add and encrypt) a new
                token if the active token has not already been created.

        Returns:
            The active token `#!py str` if it exists & can be decrypted, or else `None`.

        Raises:
            RuntimeError:
                If no tokens have been registered and `allow_auto_register_token` is set
                to `False`, OR if args have not been parsed and `allow_auto_parse_args`
                is set to `False`.
        """
        if not self._tokens_by_uid:
            if allow_auto_register_token:
                self._tokens_by_uid[_DEFAULT_TOKEN_NAME] = self._create_default_token()
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
                return token.resolve(allow_token_creation=allow_token_creation)
            except KeyboardInterrupt:
                self.cli.exit_process(self.strings.m_exit_by_interrupt, is_error=False)

        return None

    def run_bot(self, bot_class: str | type = "discord.Bot", **options) -> None:
        """Instantiates the bot as specified and runs it using the active token.

        In the simplest use case, this method will work out-of-the-box with no extra
        customization needed, as in the example below. This assumes a default token has
        already been created and that you are using one of the more common Python API
        wrappers for Discord: discord.py or Pycord.

        In practice, you will likely have to provide a little more information, such as
        the name (or type) of your `bot_class` if your bot subclasses `discord.Bot` or
        uses a different Discord library. This method provides a straightforward answer
        to these more complex use cases, while at the same time preserving most (if not
        all) of the flexibility provided by your chosen Discord library. See below for
        more information about the parameters you can pass into this method.

        Example:
            ```py title="bot.py"
            from botstrap import BotstrapFlow

            BotstrapFlow().run_bot()
            ```

            ```console title="Console Session"
            $ python bot.py

            bot: default: Attempting to log in to Discord...
            bot: default: Successfully logged in as "BasicBot#1234".
            ```

        Args:
            bot_class:
                The class name or `#!py type` of your bot. Will be instantiated with the
                `options` keyword args. This arg's default value is compatible with the
                [`discord.py`](https://pypi.org/project/discord.py/) and
                [`py-cord`](https://pypi.org/project/py-cord/) packages.
            options:
                Optional keyword arguments that will be forwarded to one of two
                possible destinations:

                1. Any args accepted by
                [`retrieve_active_token()`][botstrap.BotstrapFlow.retrieve_active_token]
                will be passed to that method when it gets called by this one in order
                to obtain the token to run your bot.

                2. The remaining args will be passed to the constructor of `bot_class`
                upon instantiation. A common use case for this is specifying any special
                [`intents`](https://discord.com/developers/docs/topics/gateway#privileged-intents)
                your bot might need.

                Despite what the column to the right says, this parameter is <u>not
                required</u>. Any options that aren't specified (which may be all of
                them) will simply use their default values.

        Raises:
            ImportError:
                If the specified `bot_class` is a string that refers to a type that
                cannot be imported in the current environment.
            TypeError:
                If the specified `bot_class` is not an instantiable type.
            SystemExit:
                If Discord login fails, so the bot cannot run. This may be caused by
                an invalid bot token.
        """
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

    def _create_default_token(self) -> Token:
        return Token(
            self, (uid := _DEFAULT_TOKEN_NAME), display_name=self.colors.lowlight(uid)
        )

    def _init_bot(self, token_value: str, bot_class: type, **options) -> None:
        bot = bot_class(**options)
        token = self._active_token or self._create_default_token()

        @bot.event
        async def on_connect() -> None:
            bot_id = self.colors.highlight(getattr(bot, "user", type(bot).__name__))
            self.cli.print_prefixed_message(
                self.strings.m_login_success.substitute(bot_id=bot_id, token=token)
            )

        self.cli.print_prefixed_message(
            self.strings.m_login.substitute(token=token),
            suppress_newline=True,
        )

        try:
            bot.run(token_value)
        except KeyboardInterrupt:
            self.cli.exit_process(self.strings.m_exit_by_interrupt, is_error=False)
        except Metadata.import_class("discord.LoginFailure"):  # type: ignore[misc]
            self.cli.print_prefixed_message(is_error=True)
            self.cli.exit_process(self.strings.m_login_failure)

    def _manage_tokens(self, tokens: list[Token]) -> None:
        if not any(token for token in tokens if token.uid == _DEFAULT_TOKEN_NAME):
            tokens.append(self._create_default_token())

        while saved_tokens := [token for token in tokens if token.file_path.is_file()]:
            self.cli.print_prefixed_message(self.strings.t_manage_list)

            for count, token in enumerate(saved_tokens, start=1):
                index = str(token.file_path).rindex(token.uid) + len(token.uid)
                path = self.colors.lowlight(f"{str(token.file_path)[:index]}.*")
                print(f"  {count}) {self.colors.highlight(token.uid)} -> {path}")

            self.cli.confirm_or_exit(self.strings.t_delete)

            uids = [token.uid for token in saved_tokens]
            prompt = self.strings.t_delete_cue

            while (uid := self.cli.get_input(prompt)) not in uids:
                print(self.colors.warning(self.strings.t_delete_mismatch))
                print(self.strings.t_delete_hint.substitute(token_ids=uids))
                self.cli.confirm_or_exit(self.strings.t_delete_retry)

            next(token for token in tokens if token.uid == uid).clear()
            print(self.colors.success(self.strings.t_delete_success))

        self.cli.print_prefixed_message(self.strings.t_manage_none)
