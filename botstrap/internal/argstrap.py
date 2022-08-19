"""This module contains the `Argstrap` class, which parses arguments for a bot's CLI."""
import re
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Any, Callable, Final, Optional

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token
from botstrap.options import Option

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_TOKEN_METAVAR: Final[str] = "token id"

_HELP_PATTERN: Final[re.Pattern] = re.compile(r"(^|[^%])(%)([^%(]|$)")
_HELP_REPLACEMENT: Final[str] = r"\1\2\2\3"  # Escape the "%" by including it twice.


class Argstrap(ArgumentParser):
    """Parses command-line args and provides part of the CLI for bots that use Botstrap.

    This class extends
    [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser)
    and can operate similarly, but its primary use is to automatically handle both
    Botstrap-specific and custom-defined command-line options.
    """

    def __init__(
        self,
        cli: CliSession,
        tokens: list[Token],
        description: Optional[str] = None,
        version: Optional[str] = None,
        **custom_options: Option,
    ) -> None:
        """Initializes a new `Argstrap` instance.

        Args:
            cli:
                A `CliSession` providing the UX used by the CLI.
            tokens:
                The tokens that are defined for the bot. Will be used to determine its
                available command-line arguments (e.g. if multiple tokens are supported,
                a "token id" argument may be specified to select which one to use).
            description:
                A short human-readable description of the bot. Will be displayed when
                the `--help` option is passed to the CLI. If omitted, Botstrap will try
                to fill this field from package metadata. If unsuccessful, this line
                will be left blank.
            version:
                A string representing the current version of the bot. Will be displayed
                when the `--version` option is specified. If omitted, that option will
                not be present in the bot's CLI.
            **custom_options:
                A dictionary defining the bot's custom-defined command-line options.
                If omitted, only the default Botstrap options will be available in the
                bot's CLI.
        """
        self.cli: Final[CliSession] = cli
        self.tokens: Final[list[Token]] = tokens
        self.version: Final[Optional[str]] = version
        self._custom_callbacks: Final[dict[str, Callable[[Any], None]]] = {}

        program_command = Metadata.get_program_command(self.cli.name)
        program_name = program_command[-1]  # Last arg is the file/module/script name.

        super().__init__(
            prog=self.cli.colors.primary(program_name),
            usage=self._build_usage_string(program_name, list(custom_options.keys())),
            description=self._build_description_string(program_command, description),
            formatter_class=RawTextHelpFormatter,
            conflict_handler="resolve",
            add_help=False,
        )

        if self._is_multi_token:
            self.add_argument(  # This is the only positional argument.
                _TOKEN_KEY,
                nargs="?",
                choices=(token_uids := [token.uid for token in self.tokens]),
                default=token_uids[0],
                help=self.cli.strings.h_token_id.substitute(token_ids=token_uids),
                metavar=self._format_metavar(_TOKEN_METAVAR, lowlight=False),
            )

        def add_option(name: str, action: str = "store_true", **kwargs) -> None:
            """Adds the specified option (and its abbreviated form) to the parser."""
            self.add_argument(f"-{name[0]}", f"--{name}", action=action, **kwargs)

        # Add custom options before default ones so off-limits names can be overwritten.
        for option_key, option in custom_options.items():
            add_option(
                option_key.replace("_", "-"),
                **self._process_custom_option(option_key, option),
            )

        # Add default options in order of relevance/usefulness, beginning with `-t`.
        add_option(_TOKENS_KEY, help=self.cli.strings.h_tokens)  # For token management.

        if self.version:
            add_option(_VERSION_KEY, help=self.cli.strings.h_version)

        add_option(_HELP_KEY, action="help", help=self.cli.strings.h_help)

    @property
    def _is_multi_token(self) -> bool:
        """Returns True if this instance serves a bot that uses more than one token."""
        return len(self.tokens) > 1

    def _format_metavar(self, placeholder_text: str, lowlight: bool = True) -> str:
        """Returns the placeholder text, surrounded by chevrons & optionally colored."""
        metavar = f"<{placeholder_text}>"
        return self.cli.colors.lowlight(metavar) if lowlight else metavar

    def _build_usage_string(self, program_name: str, custom_options: list[str]) -> str:
        """Returns a str explaining how to run the bot's program on the command line."""
        usage_components = [self.cli.colors.primary(program_name)]

        def add_component(
            display_name: str, *, is_option: bool = True, abbreviate_option: bool = True
        ) -> None:
            """Appends the given usage component. Options are abbreviated by default."""
            prefix_chars = 0
            if is_option:
                display_name = display_name[0] if abbreviate_option else display_name
                prefix_chars = 1 if abbreviate_option else 2
            usage_components.append(f"[{'-' * prefix_chars}{display_name}]")

        add_component(_HELP_KEY, abbreviate_option=False)

        for option_name in [*custom_options, _TOKENS_KEY]:
            add_component(option_name)

        if self.version:
            add_component(_VERSION_KEY)

        if self._is_multi_token:
            add_component(self._format_metavar(_TOKEN_METAVAR), is_option=False)

        return " ".join(usage_components)

    def _build_description_string(
        self,
        program_command: list[str],
        original_desc: Optional[str],
        indentation: str = "  ",
    ) -> str:
        """Returns a str describing the bot and how to run it with its default token."""
        default_token = self.tokens[0] if self._is_multi_token else None
        desc = original_desc or ""

        if (not desc) and (info := Metadata.get_package_info(self.cli.name)):
            desc = summary if isinstance(summary := info.get("summary"), str) else ""

        indented_desc = (f"{indentation}{desc.strip()}\n" if desc else "") + indentation
        format_mode_text = self.cli.strings.h_desc_mode.substitute
        mode_addendum = (default_token and format_mode_text(token=default_token)) or ""

        return indented_desc + self.cli.strings.h_desc.substitute(
            program_command=" ".join(program_command),
            mode_addendum=f" {mode_addendum.strip()}" if mode_addendum else "",
        )

    def _process_custom_option(self, option_key: str, option: Option) -> dict[str, Any]:
        """Registers a callback and returns the Option in add_argument **kwargs form."""
        option_kwargs: dict[str, Any] = {
            "action": "store_true" if option.flag else "store",
            "help": _HELP_PATTERN.sub(_HELP_REPLACEMENT, option.help or ""),
        }
        if not option.flag:  # Non-flag options require more information.
            option_kwargs["default"] = option.default
            option_kwargs["type"] = (option_type := type(option.default))
            option_kwargs["choices"] = option.choices or None
            option_kwargs["metavar"] = self._format_metavar(option_type.__name__)

        def fallback_callback(option_value: Any) -> None:
            """Raises a nicely-formatted RuntimeError for options without a callback."""
            indentation = " " * len(f"{RuntimeError.__name__}: ")
            raise RuntimeError(
                f"Custom option '{option_key}' did not set a callback.\n"
                f"{indentation}Option type:  '{type(option_value).__name__}'\n"
                f"{indentation}Parsed value: '{option_value}'"
            )

        self._custom_callbacks[option_key] = (
            option.callback if (option.callback != print) else fallback_callback
        )
        return option_kwargs

    def parse_bot_args(self) -> Token:
        """Parses command-line args, calls option callbacks, & returns the active token.

        Returns:
            The token that should be decrypted and then plugged into the bot to run it.

        Raises:
            SystemExit: If a specified command-line option calls for an alternate
                program flow that exits on completion, such as `--help` or `--version`.
        """
        args = vars(super().parse_args())

        if self.version and args.pop(_VERSION_KEY, False):
            print(self.version)
        elif args.pop(_TOKENS_KEY, False):
            self.manage_tokens()
        else:
            # First, determine the token to use, based on command-line args or defaults.
            if not self.tokens:
                token = Token.get_default(self.cli)
            elif len(self.tokens) == 1:
                token = self.tokens[0]
            else:
                # Pop _TOKEN_KEY out so an error is raised if any custom options use it.
                # It's guaranteed to exist and be a valid uid iff len(self.tokens) > 1.
                token = next(t for t in self.tokens if t.uid == args.pop(_TOKEN_KEY))

            # Then, invoke the callbacks for all custom options, if any were specified.
            for option_name, callback in self._custom_callbacks.items():
                callback(args.pop(option_name))  # Pass in the value of the parsed arg.

            return token  # This is the only path that will continue program execution.

        # Silently and successfully exit if an alternate flow was chosen and completed.
        raise SystemExit(0)

    def manage_tokens(self) -> None:
        """Starts the token management flow, allowing viewing/deletion of saved tokens.

        This is automatically invoked by
        [`parse_bot_args()`][botstrap.internal.argstrap.Argstrap.parse_bot_args] when
        the `--tokens` option is specified on the command line (and if neither `-h`
        nor `-v` was specified, because those options take priority).

        ??? note "Note - Exiting this method"
            This method will only `#!py return` if/when the user has **no more files**
            for any of the [`tokens`][botstrap.internal.argstrap.Argstrap.__init__] that
            were specified upon instantiation of this class. If the `#!py "default"`
            token wasn't included in that original list of tokens, it will be appended
            for the purposes of this method, just in case the user has existing files
            associated with it.

            If the user still has existing token files but chooses not to delete any
            of them, this method will **end the process** with exit code `#!py 0` to
            indicate that this flow was completed successfully.

        Raises:
            SystemExit: If the user still has saved tokens, but chooses to exit the
                process rather than delete any of them.
        """
        default_token = Token.get_default(self.cli)
        if not any(t for t in self.tokens if t.uid == default_token.uid):
            self.tokens.append(default_token)

        while saved_tokens := [t for t in self.tokens if t.file_path.is_file()]:
            self.cli.print_prefixed(self.cli.strings.t_manage_list)

            for count, token in enumerate(saved_tokens, start=1):
                index = str(token.file_path).rindex(token.uid) + len(token.uid)
                path = self.cli.colors.lowlight(f"{str(token.file_path)[:index]}.*")
                print(f"  {count}) {self.cli.colors.highlight(token.uid)} -> {path}")

            self.cli.confirm_or_exit(self.cli.strings.t_delete)

            uids = [token.uid for token in saved_tokens]
            prompt = self.cli.strings.t_delete_cue

            while (uid := self.cli.get_input(prompt)) not in uids:
                print(self.cli.colors.warning(self.cli.strings.t_delete_mismatch))
                print(self.cli.strings.t_delete_hint.substitute(token_ids=uids))
                self.cli.confirm_or_exit(self.cli.strings.t_delete_retry)

            next(t for t in self.tokens if t.uid == uid).clear()
            print(self.cli.colors.success(self.cli.strings.t_delete_success))

        self.cli.print_prefixed(self.cli.strings.t_manage_none)
