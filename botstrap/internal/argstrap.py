from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Final, Optional

from botstrap.internal.cmdline import CliManager
from botstrap.internal.colors import ThemeColors
from botstrap.internal.metadata import Metadata
from botstrap.internal.strings import Strings
from botstrap.internal.tokens import Token

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_TOKEN_METAVAR: Final[str] = "<token id>"
_TOKENS_DEST: Final[str] = "manage_tokens"


class Argstrap(ArgumentParser):
    """A subclass of `ArgumentParser` with logic to handle Botstrap-specific use cases.

    Args:
        manager:
            A `CliManager` instance specifying the `ThemeColors` and `Strings` to be
            used by the CLI.
        description:
            An optional string containing a description/summary of the bot. Will be
            displayed along with usage instructions when the `-h` option is specified.
            If omitted, this field will be populated from package metadata (if it is
            available). Otherwise, only the usage instructions will be displayed.
        version:
            An optional string representing the bot version. Will be displayed when the
            `-v` option is specified. If omitted, the `-v` option will not be available.
        registered_tokens:
            A `list` of all the `Token`s that are recognized by the bot. Will be used to
            determine the available command-line arguments (e.g. if multiple tokens are
            supported, a "token id" argument may be passed to select which one to run).
    """

    def __init__(
        self,
        manager: CliManager,
        description: Optional[str],
        version: Optional[str],
        registered_tokens: list[Token],
    ) -> None:
        prog = Metadata.get_program_command(manager.name)[-1]
        is_multi_token = len(registered_tokens) > 1
        default_token = registered_tokens[0] if is_multi_token else None

        super().__init__(
            prog=manager.colors.primary(prog),
            usage=_build_usage_string(manager.colors, prog, version, is_multi_token),
            description=_build_description_string(manager, description, default_token),
            formatter_class=RawTextHelpFormatter,
            add_help=False,
        )

        if is_multi_token:
            self._add_token_argument(manager.strings, registered_tokens)

        self._add_option_argument(
            _TOKENS_KEY, manager.strings.h_tokens, dest=_TOKENS_DEST
        )

        if version:
            self._add_option_argument(_VERSION_KEY, manager.strings.h_version)

        self._add_option_argument(_HELP_KEY, manager.strings.h_help, action="help")

    def _add_token_argument(self, strings: Strings, valid_tokens: list[Token]) -> None:
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
    colors: ThemeColors,
    prog_name: str,
    version: Optional[str],
    is_multi_token: bool,
) -> str:
    usage_components = [colors.primary(prog_name)]

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
        add_component(colors.lowlight(_TOKEN_METAVAR), is_option=False)

    return " ".join(usage_components)


def _build_description_string(
    manager: CliManager,
    description: Optional[str],
    default_token: Optional[Token],
    indentation: str = "  ",
) -> str:
    if (not description) and (info := Metadata.get_package_info(manager.name)):
        description = desc if isinstance(desc := info.get("summary"), str) else ""

    description = f"{indentation}{description.strip()}\n" if description else ""
    description += indentation

    mode_addendum = (
        default_token and manager.strings.h_desc_mode.substitute(token=default_token)
    ) or ""

    return description + manager.strings.h_desc.substitute(
        program_name=" ".join(Metadata.get_program_command(manager.name)),
        mode_addendum=f" {mode_addendum.strip()}" if mode_addendum else "",
    )
