"""This module contains most of the implementation of Botstrap's standalone CLI."""
from __future__ import annotations

import functools
import re
import sys
import webbrowser
from argparse import ArgumentParser
from typing import Any, Callable, Final, Match, cast

from botstrap import CliColors, Color
from botstrap.cli.scan import detect_bot_tokens
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
_ARG_NAMES: Final[str] = "name_or_flags"
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
        super().__init__(
            name=cast(str, (metadata := Metadata.get_package_info("botstrap"))["name"]),
            colors=CliColors(primary=Color.pink) if enable_colors else CliColors.off(),
        )

        self.parser: Final[ArgumentParser] = ArgumentParser(self.name, add_help=False)
        self._command_parsers: Final[Any] = self.parser.add_subparsers()
        self._help: Final[list[str]] = [
            self._build_header(f"version {metadata['version']}", enable_colors),
            f"\n  {metadata['summary']}",
            self.colors.lowlight(f"  NOTE: {_NOTE_TEXT}"),
            self._build_usage(),
            self.colors.highlight("\nCommands:"),
        ]  # More lines of text will be appended to this list throughout this method.

        def get_project_url(label: str) -> str:
            """Returns the project_url (from metadata) that matches the given label."""
            return next(s.split()[-1] for s in metadata["project_url"] if label in s)

        self._add_subcommand(
            "scan",
            "Scan for plaintext bot tokens in the current Git repository.",
            detect_bot_tokens,
            {
                _ARG_NAMES: ("paths",),
                "nargs": "*",
                "help": "Paths to check. Leave blank to scan the entire repository.",
            },
            {
                _ARG_NAMES: ("-q", "--quiet"),
                "action": "store_true",
                "help": "Suppress output if no plaintext bot tokens are detected.",
            },
            {
                _ARG_NAMES: ("-v", "--verbose"),
                "action": "store_true",
                "help": "Show output for all scanned files. No effect if `-q` is set.",
            },
            colors=self.colors,
        )
        self._add_subcommand(
            "docs",
            "Open the Botstrap API documentation in your web browser.",
            webbrowser.open,
            url=get_project_url("Documentation"),
        )
        self._add_subcommand(
            "repo",
            "Open the Botstrap repository on GitHub in your web browser.",
            webbrowser.open,
            url=get_project_url("Source Code"),
        )
        self._add_subcommand(
            "site",
            "Open the Botstrap website in your browser.",
            webbrowser.open,
            url=metadata["home_page"],
        )
        self._add_subcommand("help", "Display this help message.", self._print_help)

        self._add_general_options()
        self.parser.set_defaults(callback=self._print_help, callback_keys=())

    def _add_argument(
        self,
        target_parser: ArgumentParser,
        target_help: list[str],
        *arg_name_or_flags: str,
        **arg_parameters: Any,
    ) -> None:
        """Adds the specified argument to the targeted parser and help text list."""
        target_help.append(
            f"  {', '.join(arg_name_or_flags).ljust(18)} "
            f"{self.colors.lowlight(arg_parameters.pop('help', None))}"
        )
        target_parser.add_argument(*arg_name_or_flags, **arg_parameters)

    def _add_general_options(
        self,
        custom_parser: ArgumentParser | None = None,
        custom_help: list[str] | None = None,
    ) -> None:
        """Adds the two "general options" (`-h` and `-n`) to the appropriate parser."""
        target_parser = custom_parser or self.parser
        target_help = custom_help or ((not custom_parser) and self._help) or []
        target_help.append(self.colors.highlight("\nGeneral Options:"))
        self._add_argument(
            target_parser,
            target_help,
            *_HELP_ARGS,
            help="Display help.",
            action="store_const",
            const=functools.partial(self._print_help, custom_help=custom_help),
            dest="callback",
        )
        self._add_argument(
            target_parser,
            target_help,
            *_NO_COLORS_ARGS,
            help="Suppress colored output.",
            action="store_true",
        )

    def _add_subcommand(
        self,
        name: str,
        description: str,
        callback: Callable[..., Any],
        *callback_args: dict[str, Any],
        **callback_kwargs: Any,
    ) -> None:
        """Adds a subcommand (with a callback & optional args of its own) to the CLI."""
        subparser = self._command_parsers.add_parser(name, add_help=False)
        callback_keys, custom_help = [], []

        if callback_args:
            usage_keys = []
            custom_help.extend(
                [f"  {description}", self.colors.highlight("\nCommand Options:")]
            )
            for arg_params in callback_args:
                usage_keys.append((name_or_flags := arg_params.pop(_ARG_NAMES))[0])
                callback_keys.append(name_or_flags[-1].strip("-"))
                self._add_argument(subparser, custom_help, *name_or_flags, **arg_params)
            custom_help.insert(0, f"{self._build_usage(name, *usage_keys)}\n")

        subparser.set_defaults(
            callback=functools.partial(callback, **callback_kwargs),
            callback_keys=callback_keys,
        )
        self._add_general_options(subparser, custom_help)
        self._help.append(f"  {self.colors.primary(name.ljust(8))} {description}")

    def _build_header(self, version: str, enable_colors: bool) -> str:
        """Returns a multi-line string containing the formatted header for the CLI."""
        width = _CONTENT_WIDTH + (len(self.colors.primary("")) if enable_colors else 0)
        lines = [(color(s) if enable_colors else s) for s, color in _ASCII_HEADER[:-1]]
        last_line, last_color = _ASCII_HEADER[-1]
        version_width = cast(Match, re.match(r" *", last_line)).end()
        version = version.center(version_width)
        last_line = self.colors.lowlight(version + (tail := last_line[version_width:]))
        if enable_colors:
            last_line = last_line.center(width).replace(tail, last_color(tail))
        return "\n".join(line.center(width) for line in [*lines, last_line])

    def _build_usage(self, command: str = "", *extra_arg_names: str) -> str:
        """Returns formatted usage info text for the command, or the CLI in general."""
        name = f" {self.colors.primary(self.name)}" if command else f"\n  {self.name}"
        component_strings = [
            f"\n{self.colors.highlight('Usage:')}{name}",
            self.colors.primary(command or "<command>"),
            *[f"[{extra_arg_name}]" for extra_arg_name in extra_arg_names],
            self.colors.lowlight("[-h] [-n]" if command else "[options]"),
        ]
        return " ".join(component_strings)

    def _print_help(self, custom_help: list[str] | None = None) -> None:
        """Prints nicely-formatted help text for (a command in) the standalone CLI."""
        print("\n".join(custom_help or self._help), end="\n\n")


def main() -> None:
    """Acts as the primary entry point for (and executes) Botstrap's standalone CLI."""

    def has_args(*args_to_check: str) -> bool:
        """Returns True if any of the given args were specified on the command line."""
        return any(arg in sys.argv for arg in args_to_check)

    args = BotstrapCli(enable_colors=not has_args(*_NO_COLORS_ARGS)).parser.parse_args()
    result = (
        args.callback(**{k: v for k, v in vars(args).items() if k in expected_keys})
        if (expected_keys := args.callback_keys) and (not has_args(*_HELP_ARGS))
        else args.callback()
    )
    raise SystemExit(result or 0)
