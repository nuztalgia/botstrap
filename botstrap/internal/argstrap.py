"""This module contains the `Argstrap` class, which parses arguments for a bot's CLI."""
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Any, Final, Optional

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_TOKEN_METAVAR: Final[str] = "<token id>"


class Argstrap(ArgumentParser):
    """Parses command-line args and provides part of the CLI for bots that use Botstrap.

    This class extends
    [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser)
    and operates almost identically, except that it also automatically handles a number
    of Botstrap-specific command-line options.
    """

    def __init__(
        self,
        cli: CliSession,
        tokens: list[Token],
        description: Optional[str] = None,
        version: Optional[str] = None,
        **custom_options: dict[str, Any],
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
        """
        self.cli: Final[CliSession] = cli
        self.tokens: Final[list[Token]] = tokens
        self.version: Final[Optional[str]] = version

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
                metavar=_TOKEN_METAVAR,
                nargs="?",
                choices=(token_uids := [token.uid for token in self.tokens]),
                default=token_uids[0],
                help=self.cli.strings.h_token_id.substitute(token_ids=token_uids),
            )

        def add_option(name: str, action: str = "store_true", **kwargs) -> None:
            """Adds the specified option (and its abbreviated form) to the parser."""
            self.add_argument(f"-{name[0]}", f"--{name}", action=action, **kwargs)

        # Add custom options before default ones so off-limits names can be overwritten.
        for option_name, option_kwargs in custom_options.items():
            add_option(option_name, action="store", **option_kwargs)

        # Add default options in order of relevance/usefulness, beginning with `-t`.
        add_option(_TOKENS_KEY, help=self.cli.strings.h_tokens)  # For token management.

        if self.version:
            add_option(_VERSION_KEY, help=self.cli.strings.h_version)

        add_option(_HELP_KEY, action="help", help=self.cli.strings.h_help)

    @property
    def _is_multi_token(self) -> bool:
        """Returns True if this instance serves a bot that uses more than one token."""
        return len(self.tokens) > 1

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
            add_component(self.cli.colors.lowlight(_TOKEN_METAVAR), is_option=False)

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

    def parse_bot_args(self, custom_options: Optional[dict[str, Any]] = None) -> Token:
        """Returns the token to use, if it can be determined based on command-line args.

        Raises:
            SystemExit: If a specified command-line option calls for an alternate
                program flow that exits on completion, such as `--help` or `--version`.
        """
        args = vars(super().parse_args())

        def update_options() -> None:
            """Updates the `custom_options` dict param in-place with the parsed args."""
            if custom_options:
                for custom_key in custom_options:
                    if (custom_key != _TOKEN_KEY) and (custom_key in args):
                        custom_options[custom_key] = args.pop(custom_key)

        def select_token() -> Token:
            """Determines the token to use, based on command-line args or defaults."""
            match len(self.tokens):
                case 0:
                    return Token.get_default(self.cli)
                case 1:
                    return self.tokens[0]
                case _:
                    uid = args.pop(_TOKEN_KEY)  # Guaranteed to be a valid/existing uid.
                    return next(token for token in self.tokens if token.uid == uid)

        if self.version and args.pop(_VERSION_KEY, False):
            print(self.version)
        elif args.pop(_TOKENS_KEY, False):
            self.manage_tokens()
        else:  # The only path that will continue execution of the "main" program flow.
            update_options()
            return select_token()

        # Silently and successfully exit if an alternate flow was chosen and completed.
        raise SystemExit(0)

    def manage_tokens(self) -> None:
        """Starts the token management flow, allowing viewing/deletion of saved tokens.

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
