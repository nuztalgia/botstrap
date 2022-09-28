"""This module contains functions used by the `botstrap scan` standalone CLI command."""
from __future__ import annotations

import os
import re
import shutil
import string
import subprocess
from typing import Callable, Final, Sequence

from botstrap import CliColors

_IGNORED_DIR_ARGS: Final[tuple[str, ...]] = tuple(
    f":!:*{dir_name}/*" for dir_name in (".*_cache", ".tox", "__pycache__", "venv")
)
_TEXT_CHARS: Final[bytearray] = (
    bytearray([7, 8, 9, 10, 11, 12, 13, 27])
    + bytearray(range(0x20, 0x7F))
    + bytearray(range(0x80, 0x100))
)
_TOKEN_PATTERN: Final[re.Pattern] = re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")


def _is_text_file(filename: str) -> bool:
    """Returns whether the file appears to be text, based on its first KB of content.

    This is roughly based on the binary/text detection in pre-commit/identify:
    https://github.com/pre-commit/identify/blob/main/identify/identify.py
    """
    with open(filename, "rb") as file:
        return not bool(file.read(1024).translate(None, _TEXT_CHARS))


def detect_bot_tokens(
    paths: Sequence[str] | None = None,
    quiet: bool = False,
    verbose: bool = False,
    colors: CliColors = CliColors.off(),
) -> int:
    """Returns 1 if any plaintext tokens are found in the current repo, or 0 if not."""
    all_files: Final[set] = set()
    files_with_tokens: Final[list] = []
    git_path: Final[str] = shutil.which("git") or "/usr/bin/git"
    line_spacing: Final[str] = "" if quiet else "\n"

    def run_git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
        """Returns the result of running `git` with the given args in a subprocess."""
        try:
            return subprocess.run([git_path, *args], cwd=cwd, capture_output=True)
        except FileNotFoundError as file_error:
            stderr = f"fatal: {file_error.strerror.lower()}: git (executable)".encode()
            return subprocess.CompletedProcess(git_path, returncode=1, stderr=stderr)

    def print_error(summary: str, hint_text: str, stderr: bytes) -> None:
        """Prints the `stderr` from a subprocess in a pretty format with hint text."""
        print(f"{line_spacing}{colors.error(f'ERROR: {summary}.')} {hint_text}", end="")
        if error_lines := stderr.decode().strip().split("\n"):
            print(f"\n  {colors.error('└─')} {colors.lowlight(error_lines[0])}", end="")
        print(line_spacing)

    # https://git-scm.com/docs/git-rev-parse#Documentation/git-rev-parse.txt---show-cdup
    if (cdup_proc := run_git("rev-parse", "--show-cdup")).returncode:
        hint = "Is it installed, and are you in a Git repository directory?"
        print_error("Git command failed", hint, cdup_proc.stderr)
        return 1

    repo_root = cdup_proc.stdout.decode().strip() or None
    repo_paths = [os.path.relpath(path).replace("\\", "/") for path in (paths or [])]

    def get_repo_files(*args: str, include_repo_path_args: bool = True) -> None:
        """Populates `all_files` by executing `git ls-files` with the specified args."""
        repo_path_args = repo_paths if include_repo_path_args else []
        ls_proc = run_git("ls-files", "-z", *repo_path_args, *args, cwd=repo_root)
        ls_proc.check_returncode()  # Raise a CalledProcessError if nonzero return code.
        ls_files = ls_proc.stdout.decode().strip("\0").split("\0")
        all_files.update(ls_filename for ls_filename in ls_files if ls_filename)

    try:
        get_repo_files()  # Files that are tracked/cached by Git.
        get_repo_files("-o", *_IGNORED_DIR_ARGS)  # Untracked files in non-ignored dirs.
        for path in repo_paths:
            if path not in all_files:  # Double-check specified paths are valid/present.
                get_repo_files("--error-unmatch", path, include_repo_path_args=False)
    except subprocess.CalledProcessError as process_error:
        hint = "Specified path(s) must point to files/folders in the active repo."
        print_error("Invalid path", hint, process_error.stderr)
        return 1

    if not quiet:
        file_count = f"{len(all_files)} file{'' if len(all_files) == 1 else 's'}"
        get_scan_summary = string.Template("\nScanning ${file_count}...").substitute
        if verbose:
            print(colors.highlight(get_scan_summary(file_count=file_count)))
        else:
            print(get_scan_summary(file_count=colors.highlight(file_count)))

    file_number_width = (len(str(len(all_files))) + 2) if (verbose and not quiet) else 0

    def show_filename(color: Callable[[str], str] | None = None, ext: str = "") -> None:
        """Prints the file name/num in a pretty format, iff `-v` is set but not `-q`."""
        if file_number_width:
            print(
                colors.primary(f"{str(file_number).rjust(file_number_width)} ")
                + (color(f"{filename} [{ext}]") if (color and ext) else filename)
            )

    # Loop through files alphabetically, open text files, & search for the token regex.
    for file_number, filename in enumerate(sorted(all_files), start=1):
        if _is_text_file(filename):
            with open(filename, "r", encoding="utf-8") as file:
                if _TOKEN_PATTERN.search(file.read()):
                    files_with_tokens.append(filename)
                    show_filename(colors.warning, "WARNING: Contains plaintext token.")
                else:
                    show_filename()
        else:
            show_filename(colors.lowlight, "SKIPPED: Not a text file.")

    # Return 1 (exit code for error) if any files with unencrypted tokens were found.
    if files_with_tokens:
        error_label = colors.error(f"{line_spacing}Plaintext bot token(s) detected in:")
        print("\n  - ".join([error_label, *files_with_tokens]), end=f"\n{line_spacing}")
        return 1

    if not quiet:
        print(colors.success("\nNo plaintext bot tokens detected.\n"))

    return 0
