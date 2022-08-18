"""This is the main Botstrap module, featuring the `BotstrapFlow` class."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Final

from botstrap.colors import CliColors
from botstrap.internal import Argstrap, CliSession, Metadata, Token
from botstrap.options import CliOption
from botstrap.strings import CliStrings


class BotstrapFlow(CliSession):
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
        name = name or Metadata.guess_program_name() or "bot"
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
        """Defines a Discord bot token to be managed by this flow.

        After instantiating this class and before calling any of its other methods, this
        one must be called for **each unique token** that may be used by your bot. For
        instance, to define a `#!py "development"` token as well as a password-protected
        `#!py "production"` token, you would call this method twice.

        This is what lets Botstrap know how to display the token's name, whether to ask
        for a password when it's accessed, and where to find (or create) its files. In
        other words, this method is simply a way to declare the token's behavior -
        **not** its value.

        ??? question "FAQ - Where is the token value defined?"
            So far, we haven't mentioned the **value** or "secret data" of the token,
            which may or may not exist at the time this method is called - it makes no
            difference at this point. The token value will be requested interactively
            and securely through the CLI only if/when it's actually needed, at which
            point it will be encrypted and saved for future use. :lock:

            For more technical details about how the token values are encrypted and
            decrypted, feel free to check out the documentation for the internal
            [`secrets`](../../internal/secrets) module.

        ??? note "Note - Automatically registering a default token"
            If <u>**all**</u> of the following statements are true, you can skip this
            method and move on to the [next one][botstrap.BotstrapFlow.parse_args]
            in the flow:

            - **Your bot only uses one token** - it only needs to run in one
              environment, or only has a single configuration, or a similar
              reason along those lines.
            - **It doesn't require password-protection** - the Discord account it
              uses doesn't have access to any real users or servers that could
              potentially be damaged if a malicious actor were to gain control.
            - **You do not disable** `allow_auto_register_token` **in any subsequent
              method calls** - it's enabled by default, so unless you explicitly set
              it to `False`, you'll be fine.

            If you decide to skip this method, a simple token named `#!py "default"`
            will be created when you first run your bot. It will be saved in a directory
            named `.botstrap_keys`, which will be created in the same location as the
            file containing the `#!py "__main__"` module of your bot's script.

        ??? example "Example - Registering multiple tokens"
            This example uses [`Color`][botstrap.Color] functions to make the tokens
            more easily identifiable when they're mentioned in the CLI.

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
                created in the same location as the main module of your bot's script.
            allow_overwrites:
                Whether to allow this token to be registered even if `uid` already
                belongs to a registered token. If `True`, this token will clobber the
                previous token.

        Returns:
            This `BotstrapFlow` instance, for chaining method calls.

        Raises:
            ValueError: If `storage_directory` does not point to a valid directory (i.e.
                it doesn't exist or points to a file), **OR** if `allow_overwrites` is
                `False` and `uid` belongs to a token that has already been registered.
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
        custom_options: dict[str, str | bool | int | float | CliOption] | None = None,
    ) -> BotstrapFlow:
        """Parses any arguments and options passed in via the command line.

        This should only be invoked after **all** of your bot's tokens are declared
        using [`register_token()`][botstrap.BotstrapFlow.register_token], in order to
        ensure that the [active token][botstrap.BotstrapFlow.retrieve_active_token]
        can be correctly determined from any command-line arguments passed to your
        bot's script.

        ??? note "Note - Automatically parsing arguments"
            If your bot doesn't require the customization afforded by the parameters
            below, you can skip this method as long as you do **not** disable
            `allow_auto_parse_args` in any subsequent method calls to either
            [`retrieve_active_token()`][botstrap.BotstrapFlow.retrieve_active_token] or
            [`run_bot()`][botstrap.BotstrapFlow.run_bot]. It's enabled by default, so
            unless you explicitly set it to `False`, you'll be fine.

        ??? example "Example - Customizing your bot's description"
            ```py title="bot.py"
            from botstrap import BotstrapFlow

            BotstrapFlow().parse_args(
                description="A really cool Discord bot that uses Botstrap!"
            )
            ```

            ```console title="Console Session" hl_lines="4"
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
                option will not be present in your bot's CLI.

        Returns:
            This `BotstrapFlow` instance, for chaining method calls.

        Raises:
            SystemExit: If a specified command-line option calls for an alternate
                program flow that exits on completion, such as `--help` or `--version`.
        """
        argstrap = Argstrap(
            cli=self,
            tokens=list(self._tokens_by_uid.values()),
            description=description,
            version=version,
            **{  # Convert the `custom_options` into a format that Argstrap understands.
                k: (asdict(v) if isinstance(v, CliOption) else {"default": v})
                for k, v in (custom_options or {}).items()
            },
        )
        # The following call to `parse_bot_args()` may raise a `SystemExit` depending on
        # which options were specified on the command line. If it doesn't, then it will
        # modify the `custom_options` dict in-place (if that parameter was provided) and
        # set the value of `self._active_token` to a valid `Token` (i.e. not `None`).
        self._active_token = argstrap.parse_bot_args(custom_options)
        return self

    def retrieve_active_token(
        self,
        *,
        allow_auto_register_token: bool = True,
        allow_auto_parse_args: bool = True,
        allow_token_creation: bool = True,
    ) -> str | None:
        """Returns the value of the active token, if it exists and can be decrypted.

        The **active token** is the one that should be used to run your bot, taking
        into account all tokens that have been registered and any arguments that were
        passed in from the command line. If no custom tokens have been defined, this
        will be the basic `#!py "default"` token.

        The **value** of the token is a string containing its decrypted data,
        which can be plugged into your bot's `run()` method to log it into Discord.
        This can (and for security reasons, should) be handled automatically by
        [`run_bot()`][botstrap.BotstrapFlow.run_bot] - which means that ideally, you
        won't need to call this method at all.

        ??? caution "Caution - Keep your tokens safe!"
            Token values should always be kept secret and can be very damaging if
            leaked... so **make sure** you don't `#!py print()` (or log, or output in
            any way) the return value of this method! :zipper_mouth:

            If your bot is coded such that it can be both instantiated and started by
            [`run_bot()`][botstrap.BotstrapFlow.run_bot], consider using that method
            instead for brevity and safety. This method is provided for cases in which
            that isn't a viable option, but it should be avoided if possible to prevent
            potential security mishaps.

        ??? example "Example - Retrieving a new default token"
            ```py title="bot.py"
            from botstrap import BotstrapFlow

            BotstrapFlow(name="example-bot").retrieve_active_token()
            ```

            ```{.console title="Console Session" .colored-output .ends-with-input}
            $ python bot.py

            example-bot: You currently don't have a saved default bot token.
            Would you like to add one now? If so, type "yes" or "y":
            ```

        Args:
            allow_auto_register_token:
                Whether to automatically register a basic `#!py "default"` token
                if no tokens have been explicitly defined with
                [`register_token()`][botstrap.BotstrapFlow.register_token].
            allow_auto_parse_args:
                Whether to automatically parse command-line options and args if
                [`parse_args()`][botstrap.BotstrapFlow.parse_args]
                has not been explicitly invoked.
            allow_token_creation:
                Whether to interactively prompt to create (i.e. add and encrypt)
                a new token if the active token has not already been created.

        Returns:
            The active token value if it exists and can be decrypted, otherwise `None`.

        Raises:
            RuntimeError: If no tokens have been registered and
                `allow_auto_register_token` is `False`, <br>**OR** if
                args have not been parsed and `allow_auto_parse_args` is `False`.
        """
        if not self._tokens_by_uid:
            if allow_auto_register_token:
                default_token = Token.get_default(self)
                self._tokens_by_uid[default_token.uid] = default_token
            else:
                raise RuntimeError(
                    "There are no registered tokens to retrieve.\nTo fix this, you can "
                    "allow auto-register and/or explicitly call `register_token()`."
                )

        if not self._active_token:
            if allow_auto_parse_args:
                # This will set `self._active_token`, unless an alternate path is taken.
                self.parse_args()
            else:
                raise RuntimeError(
                    "Cannot confirm active token (args were not parsed).\nTo fix this, "
                    "you can allow auto-parse and/or explicitly call `parse_args()`."
                )

        if not self._active_token:  # In theory, there's no reason for it not to be set.
            raise RuntimeError("Something went wrong. Couldn't determine active token.")

        try:
            return self._active_token.resolve(allow_token_creation=allow_token_creation)
        except KeyboardInterrupt:
            self.exit_process(self.strings.m_exit_by_interrupt, is_error=False)
            return None  # Appease mypy, even though this is technically unreachable.

    def run_bot(self, bot_class: str | type = "discord.Bot", **options: Any) -> None:
        """Instantiates the bot class and passes the active token to its `run()` method.

        In the simplest use case, this method will work out-of-the-box with no
        customization required. But in practice, you will likely have to specify
        information such as the fully-qualified name of your `bot_class`, and/or any
        `#!py **options` expected by its constructor.

        These two parameters provide a straightforward solution for complex use cases
        while preserving most, if not all, of the flexibility afforded by your chosen
        [Discord
        library](https://discord.com/developers/docs/topics/community-resources) -
        as long as you're using one of the Python ones. :snake: See the descriptions
        below for more details.

        ??? example "Example - The simplest use case"
            This example makes the following assumptions:

            - You're using one of the more common Python libraries for Discord:
              either [discord.py](https://github.com/Rapptz/discord.py)
              or [Pycord](https://github.com/Pycord-Development/pycord).
            - Your bot does not subclass `discord.Bot`.
              (**Note:** Subclassing is often useful.
              [This guide](https://guide.pycord.dev/popular-topics/subclassing-bots/)
              explains why.)
            - You've already completed the CLI flow to set up the `#!py "default"`
              token for your bot.

            If all of the above statements are true, you can run your bot with this
            extremely simple code:

            ```py title="bot.py" hl_lines="3"
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
                The fully-qualified class name or the `#!py type` of your bot.
                Will be instantiated with the `#!py **options` keyword args.
                The default value of this argument is compatible with the
                [`discord.py`](https://pypi.org/project/discord.py/) and
                [`py-cord`](https://pypi.org/project/py-cord/) packages.
            **options:
                Optional keyword arguments that will each be forwarded to one of two
                possible destinations:

                1. Any args accepted by
                [`retrieve_active_token()`][botstrap.BotstrapFlow.retrieve_active_token]
                will be passed to that method when it gets called by this one in order
                to obtain the token to run your bot.

                2. The remaining args will be passed to the constructor of `bot_class`
                upon instantiation. A common use case for this is specifying any special
                [`intents`](https://discord.com/developers/docs/topics/gateway#privileged-intents)
                your bot might need.

                Any options that aren't specified will simply use the default values
                defined by their respective methods.

        Raises:
            ImportError: If `bot_class` is a `#!py str` that refers to a type that
                cannot be imported in the current environment.
            TypeError: If `bot_class` (after it's converted to a `#!py type`, if it
                wasn't one already) is not an instantiable type.
            SystemExit: If Discord login fails, which means the bot can't run. This
                may be caused by an invalid bot token.
        """

        def filter_options(**target_options: Any) -> dict[str, Any]:
            """Pops the given options out of the original `**options` & returns them."""
            return {
                option_key: options.pop(option_key, default_value)
                for option_key, default_value in target_options.items()
            }

        # The call to `retrieve_active_token()` will (try to) set `self._active_token`.
        token_value = self.retrieve_active_token(
            **filter_options(
                allow_auto_register_token=True,
                allow_auto_parse_args=True,
                allow_token_creation=True,
            )
        )
        # An appropriate message will have been shown if either of these is unavailable.
        if (not token_value) or not (token := self._active_token):
            return

        original_bot_class = bot_class
        if isinstance(bot_class, str):
            bot_class = Metadata.import_class(bot_class) or ""

        if not isinstance(bot_class, type):
            raise TypeError(f'Unable to instantiate bot class: "{original_bot_class}"')

        bot = bot_class(**options)  # Token-related `**options` have been filtered out.

        @bot.event
        async def on_connect() -> None:
            bot_id = self.colors.highlight(getattr(bot, "user", type(bot).__name__))
            self.print_prefixed(
                self.strings.m_login_success.substitute(bot_id=bot_id, token=token)
            )

        self.print_prefixed(
            self.strings.m_login.substitute(token=token),
            suppress_newline=True,
        )

        try:
            bot.run(token_value)
        except KeyboardInterrupt:
            self.exit_process(self.strings.m_exit_by_interrupt, is_error=False)
        except Metadata.import_class("discord.LoginFailure"):  # type: ignore[misc]
            self.print_prefixed(is_error=True)
            self.exit_process(self.strings.m_login_failure)
