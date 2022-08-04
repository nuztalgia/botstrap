from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Final, Optional

from botstrap.cli import Manager
from botstrap.colors import ThemeColors
from botstrap.metadata import Metadata
from botstrap.strings import Strings
from botstrap.tokens import Token

_HELP_KEY: Final[str] = "help"
_VERSION_KEY: Final[str] = "version"
_TOKEN_KEY: Final[str] = "token"
_TOKEN_METAVAR: Final[str] = "<token id>"


class ArgParser(ArgumentParser):
    def __init__(
        self,
        manager: Manager,
        description: Optional[str],
        version: Optional[str],
        registered_tokens: list[Token],
        additional_parsers: list[ArgumentParser],
    ) -> None:
        prog = Metadata.get_program_command(manager.name)
        is_multi_token = len(registered_tokens) > 1
        default_token = registered_tokens[0] if is_multi_token else None

        super().__init__(
            prog=manager.colors.primary(prog),
            usage=_build_usage_string(manager.colors, prog, version, is_multi_token),
            description=_build_description_string(manager, description, default_token),
            parents=additional_parsers,
            formatter_class=RawTextHelpFormatter,
            add_help=False,
        )

        if is_multi_token:
            self._add_token_argument(manager.strings, registered_tokens)

        if version:
            self._add_option_argument(_VERSION_KEY, manager.strings.cli_desc_version)

        self._add_option_argument(
            _HELP_KEY, manager.strings.cli_desc_help, action="help"
        )

    def _add_token_argument(self, strings: Strings, valid_tokens: list[Token]) -> None:
        self.add_argument(
            _TOKEN_KEY,
            metavar=_TOKEN_METAVAR,
            nargs="?",
            choices=(uids := [token.uid for token in valid_tokens]),
            default=uids[0],
            help=strings.cli_desc_token_id,
        )

    def _add_option_argument(
        self,
        name: str,
        help_string: str,
        action: str = "store_true",
    ) -> None:
        self.add_argument(f"-{name[0]}", f"--{name}", help=help_string, action=action)


def _build_usage_string(
    colors: ThemeColors,
    prog_name: str,
    version: Optional[str],
    is_multi_token: bool,
) -> str:
    usage_components = [colors.primary(prog_name)]

    def add_component(display_name: str, is_option: bool = True) -> None:
        usage_components.append(f"[{'--' if is_option else ''}{display_name}]")

    add_component(_HELP_KEY)
    if version:
        add_component(_VERSION_KEY)
    if is_multi_token:
        add_component(colors.lowlight(_TOKEN_METAVAR), is_option=False)

    return " ".join(usage_components)


def _build_description_string(
    manager: Manager,
    description: Optional[str],
    default_token: Optional[Token],
    indentation: str = "  ",
) -> str:
    if (not description) and (info := Metadata.get_package_info(manager.name)):
        description = desc if isinstance(desc := info.get("summary"), str) else ""

    description = f"{indentation}{description.strip()}\n" if description else ""
    description += indentation

    token_spec = (
        (token_label := default_token and default_token.display_name)
        and manager.strings.cli_desc_info_specifier.substitute(token_label=token_label)
    ) or ""

    return description + manager.strings.cli_desc_info.substitute(
        program_name=Metadata.get_program_command(manager.name),
        token_specifier=f" {token_spec.strip()}" if token_spec else "",
    )
