"""This module contains a class and helper functions for parsing command-line args."""
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Final, Optional

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token
from botstrap.strings import CliStrings

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_TOKEN_METAVAR: Final[str] = "<token id>"
_TOKENS_DEST: Final[str] = "manage_tokens"


class Argstrap(ArgumentParser):
    """A subclass of `ArgumentParser` that handles Botstrap-specific use cases."""

    def __init__(
        self,
        cli: CliSession,
        description: Optional[str],
        version: Optional[str],
        registered_tokens: list[Token],
    ) -> None:
        """Initializes a new `Argstrap` instance.

        Args:
            cli:
                A `CliSession` providing the UX to be used by the CLI.
            description:
                A short human-readable description of the bot. Will be displayed when
                the `--help` option is passed to the CLI. If omitted, Botstrap will try
                to fill this field from package metadata. If unsuccessful, this line
                will be left blank.
            version:
                A string representing the current version of the bot. Will be displayed
                when the `--version` option is passed to the CLI. If omitted, that
                option will not be present in the bot's CLI.
            registered_tokens:
                The tokens that are defined for the bot. Will be used to determine its
                available command-line arguments (e.g. if multiple tokens are supported,
                a "token id" argument may be specified to select which one to run).
        """
        self._cli = cli
        prog_name = Metadata.get_program_command(cli.name)[-1]
        is_multi_token = len(registered_tokens) > 1
        default_token = registered_tokens[0] if is_multi_token else None

        super().__init__(
            prog=cli.colors.primary(prog_name),
            usage=self._build_usage_string(prog_name, version, is_multi_token),
            description=self._build_description_string(description, default_token),
            formatter_class=RawTextHelpFormatter,
            add_help=False,
        )

        if is_multi_token:
            self._add_token_argument(cli.strings, registered_tokens)

        self._add_option_argument(_TOKENS_KEY, cli.strings.h_tokens, dest=_TOKENS_DEST)

        if version:
            self._add_option_argument(_VERSION_KEY, cli.strings.h_version)

        self._add_option_argument(_HELP_KEY, cli.strings.h_help, action="help")

    def _add_token_argument(
        self,
        strings: CliStrings,
        valid_tokens: list[Token],
    ) -> None:
        self.add_argument(
            _TOKEN_KEY,
            metavar=_TOKEN_METAVAR,
            nargs="?",
            choices=(uids := [token.uid for token in valid_tokens]),
            default=uids[0],
            help=strings.h_token_id.substitute(token_ids=uids),
        )

    def _add_option_argument(
        self,
        name: str,
        help_string: str,
        action: str = "store_true",
        dest: Optional[str] = None,
    ) -> None:
        self.add_argument(
            f"-{name[0]}", f"--{name}", help=help_string, action=action, dest=dest
        )

    def _build_usage_string(
        self,
        prog_name: str,
        version: Optional[str],
        is_multi_token: bool,
    ) -> str:
        usage_components = [self._cli.colors.primary(prog_name)]

        def add_component(
            display_name: str, *, is_option: bool = True, abbreviate_option: bool = True
        ) -> None:
            prefix_chars = 0
            if is_option:
                display_name = display_name[0] if abbreviate_option else display_name
                prefix_chars = 1 if abbreviate_option else 2
            usage_components.append(f"[{'-' * prefix_chars}{display_name}]")

        add_component(_HELP_KEY, abbreviate_option=False)
        add_component(_TOKENS_KEY)

        if version:
            add_component(_VERSION_KEY)

        if is_multi_token:
            add_component(self._cli.colors.lowlight(_TOKEN_METAVAR), is_option=False)

        return " ".join(usage_components)

    def _build_description_string(
        self,
        description: Optional[str],
        default_token: Optional[Token],
        indentation: str = "  ",
    ) -> str:
        if (not description) and (info := Metadata.get_package_info(self._cli.name)):
            description = desc if isinstance(desc := info.get("summary"), str) else ""

        description = f"{indentation}{description.strip()}\n" if description else ""
        description += indentation

        format_mode_text = self._cli.strings.h_desc_mode.substitute
        mode_addendum = (default_token and format_mode_text(token=default_token)) or ""

        return description + self._cli.strings.h_desc.substitute(
            program_name=" ".join(Metadata.get_program_command(self._cli.name)),
            mode_addendum=f" {mode_addendum.strip()}" if mode_addendum else "",
        )
