"""This module contains the `Argstrap` class, which parses arguments for a bot's CLI."""
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Final, Optional

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_TOKEN_METAVAR: Final[str] = "<token id>"
_TOKENS_DEST: Final[str] = "manage_tokens"


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
            usage=self._build_usage_string(program_name),
            description=self._build_description_string(program_command, description),
            formatter_class=RawTextHelpFormatter,
            add_help=False,
        )

        if self._is_multi_token:
            self.add_argument(
                _TOKEN_KEY,
                metavar=_TOKEN_METAVAR,
                nargs="?",
                choices=(token_uids := [token.uid for token in self.tokens]),
                default=token_uids[0],
                help=self.cli.strings.h_token_id.substitute(token_ids=token_uids),
            )

        def add_option_argument(
            name: str, info: str, action: str = "store_true", dest: Optional[str] = None
        ) -> None:
            """Local helper function for adding an optional command-line argument."""
            self.add_argument(
                f"-{name[0]}", f"--{name}", help=info, action=action, dest=dest
            )

        # Add available options in order of relevance/usefulness, beginning with `-t`.
        add_option_argument(_TOKENS_KEY, self.cli.strings.h_tokens, dest=_TOKENS_DEST)

        if self.version:
            add_option_argument(_VERSION_KEY, self.cli.strings.h_version)

        add_option_argument(_HELP_KEY, self.cli.strings.h_help, action="help")

    @property
    def _is_multi_token(self) -> bool:
        """Returns True if this instance serves a bot that uses more than one token."""
        return len(self.tokens) > 1

    def _build_usage_string(self, program_name: str) -> str:
        """Returns a str explaining how to run the bot's program on the command line."""
        usage_components = [self.cli.colors.primary(program_name)]

        def add_component(
            display_name: str, *, is_option: bool = True, abbreviate_option: bool = True
        ) -> None:
            """Local helper function for appending an argument to the usage string."""
            prefix_chars = 0
            if is_option:
                display_name = display_name[0] if abbreviate_option else display_name
                prefix_chars = 1 if abbreviate_option else 2
            usage_components.append(f"[{'-' * prefix_chars}{display_name}]")

        add_component(_HELP_KEY, abbreviate_option=False)
        add_component(_TOKENS_KEY)

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
