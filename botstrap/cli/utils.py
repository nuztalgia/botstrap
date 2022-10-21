"""This module contains general utility functions for the `botstrap` standalone CLI ."""
from __future__ import annotations

import re
import shutil
import subprocess
from os import PathLike
from pathlib import Path
from typing import Final

from botstrap import CliColors, CliStrings
from botstrap.internal import Metadata

_TEXT_CHARS: Final[bytearray] = (
    bytearray([7, 8, 9, 10, 11, 12, 13, 27])
    + bytearray(range(0x20, 0x7F))
    + bytearray(range(0x80, 0x100))
)


def get_discord_lib(colors: CliColors = CliColors.off()) -> str | None:
    """Returns a Discord library name if exactly one is installed, otherwise None."""
    installed_libs = Metadata.get_discord_libs()
    error_text = ""

    if not installed_libs:
        error_text = "You don't have any of the supported Discord libraries installed."
    elif len(installed_libs) > 1:
        lib_names = CliStrings.default().join_choices(
            installed_libs, colors.primary, quote_choices=False, conjunction="and"
        )
        error_text = f"You have multiple Discord libraries installed ({lib_names})."

    if not error_text:
        return installed_libs[0]

    hint_text = colors.lowlight(
        "Please make sure you have exactly *one* installed, then re-run this command."
    )
    print(f"\n{colors.error('ERROR:')} {error_text}\n{hint_text}\n")
    return None


def get_lib_example(discord_lib_id: str) -> tuple[str, str]:
    """Returns a tuple of the source/dest filenames for the library-specific example."""
    if discord_lib_id in ("discordpy", "disnake", "nextcord", "pycord"):
        return "example_cog.py", "cogs/example.py"
    elif discord_lib_id in ("interactions", "naff"):
        return "example_extension.py", "extensions/example.py"
    elif discord_lib_id == "hikari":
        return "bot.py", "bot.py"
    else:
        raise RuntimeError(f"Unrecognized Discord library ID: '{discord_lib_id}'.")


def initialize_git(path: Path, colors: CliColors = CliColors.off()) -> bool:
    """Returns `True` if a Git repo is available (creating one if needed/possible)."""
    git_proc = run_git("rev-parse", "--git-dir", cwd=path)

    if git_proc.returncode:
        git_repo_text = colors.lowlight(f"({path / '.git'})")
        print(f"Initializing new Git repository. {git_repo_text}")

        if (git_init_proc := run_git("init", cwd=path)).returncode:
            hint = "Please make sure Git is installed on your system."
            print_error("\n", "'git init' failed", hint, git_init_proc.stderr, colors)
            return False
    else:
        git_output = git_proc.stdout.decode().split("\n")[0]
        git_repo_text = colors.lowlight(f"({(path / git_output).resolve()})")
        print(f"Using existing Git repository. {git_repo_text}")

    print()  # Extra newline for better readability.
    return True


def is_text_file(filename: str) -> bool:
    """Returns whether the file appears to be text, based on its first KB of content.

    This is roughly based on the binary/text detection in pre-commit/identify:
    https://github.com/pre-commit/identify/blob/main/identify/identify.py
    """
    with open(filename, "rb") as file:
        return not bool(file.read(1024).translate(None, _TEXT_CHARS))


def print_error(
    line_spacing: str,
    summary: str,
    hint_text: str,
    stderr: bytes,
    colors: CliColors = CliColors.off(),
) -> None:
    """Prints the `stderr` from a subprocess in a prettier format with hint text."""
    print(f"{line_spacing}{colors.error(f'ERROR: {summary}.')} {hint_text}", end="")
    if error_lines := stderr.decode().strip().split("\n"):
        print(f"\n  {colors.error('└─')} {colors.lowlight(error_lines[0])}", end="")
    print(line_spacing)


def run_git(
    *args: str, cwd: str | PathLike[str] | None = None
) -> subprocess.CompletedProcess:
    """Returns the result of running `git` with the given arguments in a subprocess."""
    git_path = shutil.which("git") or "/usr/bin/git"  # Hazard a guess, no big if wrong.
    try:
        return subprocess.run([git_path, *args], cwd=cwd, capture_output=True)
    except FileNotFoundError as file_error:
        stderr = f"fatal: {file_error.strerror.lower()}: git (executable)".encode()
        return subprocess.CompletedProcess(git_path, returncode=1, stderr=stderr)


def slugify(text: str) -> str:
    """Returns a "slugified" version of the text (i.e. ExampleName -> example-name)."""
    slugified_text = re.sub(r"([A-Z][a-z]+|[A-Z]+)", r"-\1", text)
    return re.sub(r"[\W_]+", "-", slugified_text).strip("-").lower()
