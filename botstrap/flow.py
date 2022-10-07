"""This module features the `Botstrap` class, which is the primary integration point."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Final, cast

from botstrap.colors import CliColors
from botstrap.internal import Argstrap, CliSession, Metadata, Token
from botstrap.options import Option
from botstrap.strings import CliStrings


class Botstrap(CliSession):
    """The primary point of integration between a Discord bot and the Botstrap library.

    This class features a modular, step-by-step flow for securely handling Discord bot
    tokens and parsing/customizing command-line options. Each method in this class
    corresponds to a step in the flow, and all of them are highly customizable in order
    to adapt to the needs of individual bots.
    """

    def __init__(
        self,
        name: str | None = None,
        *,
        desc: str | None = None,
        version: str | None = None,
        colors: CliColors = CliColors.default(),
        strings: CliStrings = CliStrings.default(),
    ) -> None:
        """Initializes a new `Botstrap` instance.

        Args:
            name:
                The name of your bot. If omitted, Botstrap will try to determine an
                appropriate name from the package and/or file metadata. If unsuccessful,
                it will use the default name: `"bot"`.
            desc:
                A short, human-readable description of your bot. Will be displayed
                when `--help` or `-h` is specified on the command line. If omitted,
                Botstrap will try to get a description from the package metadata.
                If unsuccessful, the `-h` menu will only display usage instructions.
            version:
                A string representing the current version of your bot. Will be displayed
                when `--version` is specified on the command line. If omitted, this
                option will not be available in your bot's CLI.
            colors:
                The colors to be used by the CLI. Defaults to commonly-used colors (e.g.
                green for success, red for error). Set this to `CliColors.off()` to
                disable all colors.
            strings:
                The strings to be used by the CLI. Defaults to English text with ample
                vertical spacing for legibility. Set this to `CliStrings.compact()` to
                minimize spacing.
        """
        name = name or Metadata.guess_program_name() or "bot"
        super().__init__(name, colors, strings)
        self._desc: Final[str | None] = desc
        self._version: Final[str | None] = version
        self._tokens_by_uid: Final[dict[str, Token]] = {}
        self._active_token: Token | None = None

    def register_token(
        self,
        uid: str,
        *,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
        allow_overwrites: bool = False,
    ) -> Botstrap:
        """Defines a Discord bot token to be managed by this Botstrap integration.

        After instantiating this class and before calling any of its other methods, this
        one must be called for **each unique token** that may be used by your bot.
        For instance, to define a `"development"` token as well as a password-protected
        `"production"` token, you would call this method twice.

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
            `Secret` class.

        ??? note "Note - Automatically registering a default token"
            If <u>**all**</u> of the following statements are true, you can skip this
            method and move on to the [next step](./#botstrap-flowchart) in the flow:

            - **Your bot only uses one token** - it only needs to run in one
              environment, or only has a single configuration, or a similar
              reason along those lines.
            - **It doesn't require password-protection** - the Discord account it
              uses doesn't have access to any real users or servers that could
              potentially be damaged if a malicious actor were to gain control.
            - **You do not disable** `allow_token_registration` **in any subsequent
              method calls** - it's enabled by default, so unless you explicitly set
              it to `False`, you'll be fine.

            If you decide to skip this method, a simple token named `"default"` will
            be created when you first run your bot. It will be saved in a directory
            named `.botstrap_keys`, which will be created in the same location as
            the file containing the `"__main__"` module of your bot's script.

        ??? example "Example - Registering multiple tokens"
            This example uses `Color` functions to make the tokens more easily
            identifiable when they're mentioned in the CLI.

            ```py title="bot.py"
            from botstrap import Botstrap, Color

            Botstrap().register_token(
                uid="dev",
                display_name=Color.yellow("development"),
            ).register_token(
                uid="prod",
                requires_password=True,
                display_name=Color.green("production"),
            ).run_bot()
            ```

            ```{.console title="Console Session" .ends-with-input}
            $ python bot.py --tokens

            bot.py: You currently have the following bot tokens saved:
              1. development ->  ~/path/to/your/bot/.botstrap_keys/.dev.*
              2. production  ->  ~/path/to/your/bot/.botstrap_keys/.prod.*

            Would you like to delete any of these tokens? If so, type "yes" or "y":
            ```

        Args:
            uid:
                A unique string identifying this token. Will be used in the names of
                the files holding this token's data.
            requires_password:
                Whether a password is required in order to create and subsequently
                retrieve this token.
            display_name:
                A human-readable string describing this token. Will be displayed in the
                CLI when referring to this token. If omitted, the `uid` will be shown
                instead.
            storage_directory:
                Where to store the files containing this token's data. If omitted, the
                files will be saved in a folder named `.botstrap_keys`, which will be
                created in the same location as the file containing the main module of
                your bot's script.
            allow_overwrites:
                Whether to allow this token to be registered even if `uid` already
                belongs to a registered token. If `True`, this token will clobber the
                previous token.

        Returns:
            This `Botstrap` instance, for chaining method calls.

        Raises:
            ValueError: If `storage_directory` does not point to a valid directory (i.e.
                it doesn't exist or points to a file), **OR** if `allow_overwrites` is
                `False` and `uid` belongs to a token that was already registered.
        """
        token = Token(self, uid, requires_password, display_name, storage_directory)
        if (not allow_overwrites) and (token.uid in self._tokens_by_uid):
            raise ValueError(f'A token with unique ID "{token.uid}" already exists.')
        self._tokens_by_uid[token.uid] = token
        return self

    def parse_args(self, **custom_options: Option) -> Option.Results:
        """Parses any arguments and options passed in via the command line.

        This should only be invoked after **all** of your bot's tokens are declared
        using [`register_token()`][botstrap.Botstrap.register_token] in order to ensure
        that the [active token][botstrap.Botstrap.retrieve_active_token] can be
        correctly determined from the command that was used to run your bot's script.

        If you decide that your bot doesn't need any custom command-line options, you
        may safely skip ahead to the [next step](./#botstrap-flowchart) in the flow.
        Behind the scenes, this method will be called with no params so that Botstrap
        can identify the active token and process any built-in options (such as `-h`).

        ??? tip "Tip - Define your own command-line options!"
            By default, your bot's CLI will include options for `--tokens` and `--help`
            (and `--version`, if you specify a version). However, you aren't limited to
            just those three - you can define as many `**custom_options` as you want!
            :tada:

            To add custom command-line options, simply create `Option` objects and pass
            them in as keyword arguments when you call this method. The **names** you
            choose for your keyword arguments will determine the names of the options.
            For example, an arg named `my_custom_flag` will create the CLI option
            `--my-custom-flag`.

            ---
            For more information, check out:

            - The **API reference** for `Option`. It includes plenty of examples and
              goes into detail about the fields you need to specify when defining your
              own custom options.
            - The documentation for this method's **return type**, `Option.Results`.
              (It only occupies a short section at the very bottom, so it might be
              easy to miss.)
            - ... and if you're curious about how **option abbreviations** (such as `-h`
              and `-v`) are allotted, you can venture into the internal documentation to
              read [this note](../../internal/argstrap#abbr-priority), which explains
              this process and the reasoning behind it.

        ??? example "Example - Adding a custom option to the CLI"
            ```py title="bot.py"
            from botstrap import Botstrap, Option

            Botstrap(
                desc="An example bot with a single custom option that does nothing.",
            ).parse_args(
                custom_flag=Option(flag=True, help="Hello! I'm a command-line flag!"),
            )
            ```

            ```console title="Console Session"
            $ python bot.py -h
            usage: bot.py [-c] [-t] [--help]

              An example bot with a single custom option that does nothing.
              Run "python bot.py" with no parameters to start the bot.

            options:
              -c, --custom-flag  Hello! I'm a command-line flag!
              -t, --tokens       View/manage your saved Discord bot tokens.
              -h, --help         Display this help message.
            ```

        Args:
            **custom_options:
                Keyword arguments that define your bot's custom command-line options.
                If none are provided, then only the default options will be available
                in your bot's CLI.

        Returns:
            An object with attribute names & values corresponding to the parsed options.

        Raises:
            SystemExit: If a specified command-line option calls for an alternate
                program flow that exits on completion, such as `--help` or `--version`.
        """
        argstrap = Argstrap(
            cli=self,
            tokens=list(self._tokens_by_uid.values()),
            description=self._desc,
            version=self._version,
            **custom_options,
        )
        # The following call to `parse_bot_args()` may raise a `SystemExit` depending on
        # which options were specified on the command line. If it doesn't, then it will
        # set the value of `self._active_token` to a valid `Token` (i.e. not `None`).
        self._active_token, results = argstrap.parse_bot_args()
        return results

    def retrieve_active_token(  # type: ignore[return]
        self,
        *,
        allow_token_creation: bool = True,
        allow_token_registration: bool = True,
    ) -> str | None:
        """Returns the value of the active token, if it exists and can be decrypted.

        The **active token** is the one that should be used to run your bot, taking
        into account all tokens that have been registered and any arguments that were
        passed in from the command line. If no custom tokens have been defined, this
        will be the basic `"default"` token.

        The **value** of the token is a string containing its decrypted data,
        which can be plugged into your bot to log it into Discord.
        This can (and for security reasons, should) be handled automatically by
        [`run_bot()`][botstrap.Botstrap.run_bot] - which means that ideally, you
        won't need to call this method at all.

        ??? caution "Caution - Keep your tokens safe!"
            Token values should always be kept secret and can be very damaging if
            leaked... so **make sure** you don't `print()` (or log, or output in
            any way) the return value of this method! :zipper_mouth:

            If your bot is coded such that it can be both instantiated and started by
            [`run_bot()`][botstrap.Botstrap.run_bot], consider using that method instead
            for brevity and safety. This method is provided for cases in which that
            isn't a viable option, but it should be avoided if possible to prevent
            potential security mishaps.

        ??? example "Example - Retrieving a new default token"
            ```py title="bot.py"
            from botstrap import Botstrap

            Botstrap().retrieve_active_token()
            ```

            ```{.console title="Console Session" .ends-with-input}
            $ python bot.py

            bot.py: You currently don't have a saved default bot token.
            Would you like to add one now? If so, type "yes" or "y":
            ```

        Args:
            allow_token_creation:
                Whether to interactively prompt to create (i.e. add and encrypt)
                a new token if the active token has not already been created.
            allow_token_registration:
                Whether to automatically register a basic `"default"` token
                if no tokens have been explicitly defined with
                [`register_token()`][botstrap.Botstrap.register_token].

        Returns:
            The active token value if it exists and can be decrypted, otherwise `None`.

        Raises:
            RuntimeError: If no tokens have been registered and
                `allow_token_registration` is set to `False`.
        """
        if not self._tokens_by_uid:
            if allow_token_registration:
                default_token = Token.get_default(self)
                self._tokens_by_uid[default_token.uid] = default_token
            else:
                raise RuntimeError(
                    "There are no registered tokens to retrieve.\nTo fix this, you can "
                    "allow auto-register and/or explicitly call `register_token()`."
                )

        if not self._active_token:
            # This call to `parse_args()` will either set `self._active_token` to a
            # valid `Token`, or switch to an alternate flow and then exit the process.
            self.parse_args()

        try:
            return cast(Token, self._active_token).resolve(allow_token_creation)
        except KeyboardInterrupt:
            self.exit_process(self.strings.m_exit_by_interrupt, is_error=False)

    def run_bot(
        self,
        bot_class: str | type = "",
        *,
        run_method_name: str = "run",
        init_with_token: bool = False,
        **options: Any,
    ) -> None:
        """Instantiates the bot class as specified, and runs it using the active token.

        In the simplest use case, this method will work out-of-the-box with no
        customization required. But in practice, you will most likely have to specify
        information such as the fully-qualified name (or the `type`) of your
        `bot_class`, and/or any `**options` expected by its constructor.

        This method's parameters provide a straightforward solution for more complex use
        cases while preserving most, if not all, of the flexibility afforded by your
        chosen [Discord API wrapper][1] - as long as you're using one of the Python
        ones, of course. :snake: See the parameter descriptions below for more detailed
        usage instructions.

        ??? example "Example - The simplest use case"
            This example makes the following assumptions:

            - You're using one of the Python Discord libraries for which Botstrap
              includes built-in support:<br>[discord.py][2A],&nbsp; [disnake][2B],&nbsp;
              [hikari][2C],&nbsp; [interactions.py][2D],&nbsp; [NAFF][2E],&nbsp;
              [Nextcord][2F], or&thinsp;&thinsp;[Pycord][2G].
            - Your bot does **not** subclass the default `bot_class` (often named `Bot`
              or `Client`) from your chosen library.<br>**Note:** Subclassing is often
              useful, especially when integrating with Botstrap. [This guide][3]
              explains the basics.
            - You've already completed the CLI flow to set up the `"default"` token
              for your bot.

            If all of the above statements are true, then you can run your bot with
            this extremely pared-down code:

            ```py title="bot.py"
            from botstrap import Botstrap

            Botstrap().run_bot()
            ```

            ```console title="Console Session"
            $ python bot.py

            bot.py: default: Attempting to log in to Discord...
            bot.py: default: Successfully logged in as "BotstrapBot#1234".
            ```

            Of course, this simple example probably isn't very helpful unless you're
            trying to play [golf][4] with your bot's setup code.
            For a much more complex and interesting example, check out the one
            [at the top](./#botstrap-example) of this page.

        [1]: https://discord.com/developers/docs/topics/community-resources
        [2A]: https://github.com/Rapptz/discord.py
        [2B]: https://github.com/DisnakeDev/disnake
        [2C]: https://github.com/hikari-py/hikari
        [2D]: https://github.com/interactions-py/library
        [2E]: https://github.com/NAFTeam/NAFF
        [2F]: https://github.com/nextcord/nextcord
        [2G]: https://github.com/Pycord-Development/pycord
        [3]: https://guide.pycord.dev/popular-topics/subclassing-bots/
        [4]: https://www.geeksforgeeks.org/code-golfing-in-python/

        Args:
            bot_class:
                The fully-qualified class name or the `type` of your bot. If omitted,
                Botstrap will look for installed Discord libraries and try to select
                a class from one of them. The class identified by this arg will be
                instantiated with the `**options` keyword args, as well as the
                value of the active token **if** `init_with_token` is set to `True`.
            run_method_name:
                The name of the `bot_class` method that logs the bot in using its token
                and connects to Discord, effectively "running" or "starting" the bot.
                This method will receive the token value **unless** `init_with_token`
                is set to `True`, in which case it will be called with no args.
            init_with_token:
                Whether to pass the token value into the constructor of the `bot_class`,
                instead of the method specified by `run_method_name`. By default, it
                will go to the latter.
            **options:
                Optional keyword arguments that will each be forwarded to one of two
                possible destinations:

                1. Any arguments with names matching the ones accepted by
                [`retrieve_active_token()`][botstrap.Botstrap.retrieve_active_token]
                will be passed to that method when it gets called by this one in order
                to obtain the token to run your bot.

                2. The remaining arguments will be passed to the constructor of
                `bot_class` upon instantiation. This allows you to, for example, define
                any special [`intents`][1] that might be required by your bot.

                Any options that aren't specified will simply use the default values
                defined by their respective methods.

                [1]: https://discord.com/developers/docs/topics/gateway#gateway-intents

        Raises:
            RuntimeError: If `bot_class` is not provided and a class to use can't be
                determined from installed packages.
            ImportError: If `bot_class` is a `str` that refers to a type that can't be
                imported in the current environment.
            TypeError: If `bot_class` (after it's converted to a `type`, if it wasn't
                already) isn't an instantiable type.
        """

        def filter_options(**target_options: Any) -> dict[str, Any]:
            """Pops the given options out of the original `**options` & returns them."""
            return {
                option_key: options.pop(option_key, default_value)
                for option_key, default_value in target_options.items()
            }

        # The call to `retrieve_active_token()` will (try to) set `self._active_token`.
        token_value = self.retrieve_active_token(
            **filter_options(allow_token_creation=True, allow_token_registration=True)
        )
        # An appropriate message will have been shown if either of these is unavailable.
        if (not token_value) or not (token := self._active_token):
            return

        # Begin the process of trying to determine and/or instantiate the bot class.
        original_bot_class = bot_class
        token_kwarg = {"token": token_value}

        if not bot_class:
            bot_class, run_method_name, init_with_token = Metadata.get_bot_class_info()

        if isinstance(bot_class, str):
            bot_class = Metadata.import_class(bot_class)

        if not isinstance(bot_class, type):
            raise TypeError(f'Unable to instantiate bot class: "{original_bot_class}"')

        qualified_bot_name = ".".join((bot_class.__module__, bot_class.__name__))
        if (qualified_bot_name == "discord.client.Client") and "intents" not in options:
            # The constructor of discord.py's `Client` requires the `intents` parameter.
            intents = Metadata.import_class("discord.Intents")
            options["intents"] = intents.default()  # type: ignore[attr-defined]

        # At this point, `bot_class` is a `type`, and all `**options` are bot-related.
        bot = bot_class(**(options | (token_kwarg if init_with_token else {})))

        if getattr(bot, "event", None):
            # If we can easily add an event listener, do so to confirm successful login.
            success_text = self.strings.m_login_success

            @bot.event
            async def on_connect() -> None:
                bot_id = self.colors.highlight(getattr(bot, "user", type(bot).__name__))
                self.print_prefixed(success_text.substitute(bot_id=bot_id, token=token))

        self.print_prefixed(self.strings.m_login.substitute(token=token))

        # Invoke the run method, and try to handle keyboard interrupts & login failures.
        try:
            getattr(bot, run_method_name)(**({} if init_with_token else token_kwarg))
        except KeyboardInterrupt:
            self.exit_process(self.strings.m_exit_by_interrupt, is_error=False)
        except Exception as exception:
            if type(exception).__name__ in ("LoginFailure", "UnauthorizedError"):
                self.print_prefixed(is_error=True)
                self.exit_process(self.strings.m_login_failure)
            else:
                raise  # Propagate the exception.
