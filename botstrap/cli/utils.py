"""This module contains general utility functions for the `botstrap` standalone CLI ."""
from __future__ import annotations

import shutil
import subprocess
from typing import Final

from botstrap import CliColors

_TEXT_CHARS: Final[bytearray] = (
    bytearray([7, 8, 9, 10, 11, 12, 13, 27])
    + bytearray(range(0x20, 0x7F))
    + bytearray(range(0x80, 0x100))
)


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


def run_git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Returns the result of running `git` with the given arguments in a subprocess."""
    git_path = shutil.which("git") or "/usr/bin/git"  # Hazard a guess, no big if wrong.
    try:
        return subprocess.run([git_path, *args], cwd=cwd, capture_output=True)
    except FileNotFoundError as file_error:
        stderr = f"fatal: {file_error.strerror.lower()}: git (executable)".encode()
        return subprocess.CompletedProcess(git_path, returncode=1, stderr=stderr)
