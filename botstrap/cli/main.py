"""This module contains the implementation of Botstrap's standalone CLI."""
from __future__ import annotations

import functools
import re
import sys
import webbrowser
from argparse import ArgumentParser
from typing import Any, Callable, Final, Match, cast

from botstrap import CliColors, Color
from botstrap.internal import CliSession, Metadata

_CONTENT_WIDTH: Final[int] = 69
_ASCII_HEADER: Final[tuple[tuple[str, Callable[[str], str]], ...]] = (
    (r" _           _       _                   ", Color.pink),
    (r"| |__   ___ | |_ ___| |_ _ __ __ _ _ __  ", Color.pink),
    (r"| '_ \ / _ \| __/ __| __| '__/ _` | '_ \ ", Color.yellow),
    (r"| |_) | (_) | |_\__ \ |_| | | (_| | |_) |", Color.green),
    (r"|_.__/ \___/ \__|___/\__|_|  \__,_| .__/ ", Color.cyan),
    (r"                                  |_|    ", Color.cyan),
)
_NOTE_TEXT: Final[str] = "This is the standalone CLI. For the Python API, see the docs."
_HELP_ARGS: Final[tuple[str, str]] = ("-h", "--help")
_NO_COLORS_ARGS: Final[tuple[str, str]] = ("-n", "--no-colors")


class BotstrapCli(CliSession):
    """Encapsulates Botstrap's standalone command-line interface."""

    def __init__(self, enable_colors: bool) -> None:
        """Initializes a new `BotstrapCli` instance.

        Args:
            enable_colors:
                Whether the console output text should be colored.
        """
        metadata = Metadata.get_package_info("botstrap")
        colors = CliColors(primary=Color.pink) if enable_colors else CliColors.off()
        super().__init__(name=cast(str, metadata["name"]), colors=colors)

        self.parser: Final[ArgumentParser] = ArgumentParser(self.name, add_help=False)
        self._command_parsers: Final[Any] = self.parser.add_subparsers()
        self._help: Final[list[str]] = [
            self._build_header(f"version {metadata['version']}", enable_colors),
            f"\n  {metadata['summary']}",
            colors.lowlight(f"  NOTE: {_NOTE_TEXT}"),
            (
                f"\n{colors.highlight('Usage:')}\n  {self.name} "
                f"{colors.primary('<command>')} {colors.lowlight('[options]')}"
            ),
            colors.highlight("\nCommands:"),
        ]  # More lines of text will be appended to this list throughout this method.

        def get_project_url(label: str) -> str:
            """Returns the project_url (from metadata) that matches the given label."""
            return next(s.split()[-1] for s in metadata["project_url"] if label in s)

        self._add_subcommand(
            "docs",
            description="Open the Botstrap API documentation in your web browser.",
            url=get_project_url("Documentation"),
        )
        self._add_subcommand(
            "repo",
            description="Open the Botstrap repository on GitHub in your web browser.",
            url=get_project_url("Source Code"),
        )
        self._add_subcommand(
            "site",
            description="Open the Botstrap website in your browser.",
            url=metadata["home_page"],
        )
        self._add_subcommand(
            "help", description="Display this help message.", callback=self._print_help
        )

        self._help.append(colors.highlight("\nGeneral Options:"))
        self._add_option(*_HELP_ARGS, description="Display help.")
        self._add_option(*_NO_COLORS_ARGS, description="Suppress colored output.")
        self.parser.set_defaults(callback=self._print_help)

    def _add_option(self, *flags: str, description: str) -> None:
        """Adds a generally-available CLI option. Logic is implemented elsewhere."""
        self.parser.add_argument(*flags, action="store_true")
        description = self.colors.lowlight(description)
        self._help.append(f"  {', '.join(flags).ljust(18)} {description}")

    def _add_subcommand(
        self,
        name: str,
        description: str,
        callback: Callable[..., Any] = webbrowser.open,
        **callback_kwargs: Any,
    ) -> None:
        """Adds a rudimentary CLI subcommand that simply invokes a callback function."""
        subparser = self._command_parsers.add_parser(name, add_help=False)
        subparser.add_argument(
            *_HELP_ARGS, action="store_const", const=self._print_help, dest="callback"
        )
        subparser.add_argument(*_NO_COLORS_ARGS, action="store_true")
        subparser.set_defaults(callback=functools.partial(callback, **callback_kwargs))
        self._help.append(f"  {self.colors.primary(name.ljust(8))} {description}")

    def _build_header(self, version: str, enable_colors: bool) -> str:
        """Returns a multi-line string containing the formatted header for the CLI."""
        width = _CONTENT_WIDTH + (len(self.colors.primary("")) if enable_colors else 0)
        lines = [(color(s) if enable_colors else s) for s, color in _ASCII_HEADER[:-1]]
        last_line, last_color = _ASCII_HEADER[-1]
        sub = version.center(sub_width := cast(Match, re.match("^ *", last_line)).end())
        last_line = self.colors.lowlight(sub + (tail := last_line[sub_width:]))
        if enable_colors:
            last_line = last_line.center(width).replace(tail, last_color(tail))
        return "\n".join(line.center(width) for line in [*lines, last_line])

    def _print_help(self) -> None:
        """Prints a nicely-formatted help message for the standalone CLI."""
        print("\n".join(self._help), end="\n\n")


def main() -> None:
    """Acts as the primary entry point for (and executes) Botstrap's standalone CLI."""
    cli = BotstrapCli(enable_colors=not any(arg in sys.argv for arg in _NO_COLORS_ARGS))
    cli.parser.parse_args().callback()
