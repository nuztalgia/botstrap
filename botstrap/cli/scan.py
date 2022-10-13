"""This module contains functions used by the `botstrap scan` standalone CLI command."""
from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from string import Template
from subprocess import CalledProcessError
from typing import Final

from botstrap import CliColors
from botstrap.cli.utils import is_text_file, print_error, run_git
from botstrap.internal.tokens import PATTERN as TOKEN_PATTERN

_IGNORED_DIR_ARGS: Final[tuple[str, ...]] = tuple(
    f":!:*{dir_name}/*" for dir_name in (".*_cache", ".tox", "__pycache__", "venv")
)


def detect_bot_tokens(
    paths: Sequence[str] | None = None,
    quiet: bool = False,
    verbose: bool = False,
    colors: CliColors = CliColors.off(),
) -> int:
    """Returns 1 if any plaintext tokens are found in the current repo, or 0 if not."""
    line_spacing = "" if quiet else "\n"
    cdup_proc = run_git("rev-parse", "--show-cdup")

    if cdup_proc.returncode:
        hint = "Is it installed, and are you in a Git repository directory?"
        print_error(line_spacing, "Git command failed", hint, cdup_proc.stderr, colors)
        return 1

    try:
        repo_root_dir = cdup_proc.stdout.decode().strip()
        all_files = get_repo_files(paths or [], cwd=repo_root_dir)
    except CalledProcessError as subprocess_error:
        hint = "Specified path(s) must point to files/folders in the active repo."
        print_error(line_spacing, "Invalid path", hint, subprocess_error.stderr, colors)
        return 1

    files_with_tokens = []
    file_count = len(all_files)
    label_display_width = (len(str(file_count)) + 2) if (verbose and not quiet) else 0

    if not quiet:
        print_scan_header(file_count, verbose, colors)

    for file_number, filename in enumerate(sorted(all_files), start=1):
        if scan_file_for_token(file_number, filename, colors, label_display_width):
            files_with_tokens.append(filename)

    if files_with_tokens:
        error_label = colors.error(f"{line_spacing}Plaintext bot token(s) detected in:")
        print("\n  - ".join([error_label, *files_with_tokens]), end=f"\n{line_spacing}")
        return 1

    if not quiet:
        print(colors.success("\nNo plaintext bot tokens detected.\n"))

    return 0


def list_files(*args: str, cwd: str = "") -> list[str]:
    """Returns filenames obtained by running `git ls-files` with the specified args."""
    process = run_git("ls-files", "-z", *args, cwd=cwd or None)
    process.check_returncode()  # Raise a CalledProcessError if return code is non-zero.
    ls_files = process.stdout.decode().strip("\0").split("\0")
    return [ls_filename for ls_filename in ls_files if ls_filename]


def get_repo_files(paths: Sequence[str], cwd: str = "") -> list[str]:
    """Returns an alphabetical list of filenames matched by `paths` in the current repo.

    If `paths` is `None` or empty, the list will include all files in non-ignored dirs.
    """
    repo_paths = [os.path.relpath(path).replace("\\", "/") for path in paths]
    repo_files = set(
        list_files(*repo_paths, cwd=cwd)
        + list_files(*repo_paths, "-o", *_IGNORED_DIR_ARGS, cwd=cwd)
    )

    def no_prefixed_files(prefix: str) -> bool:
        return not any([repo_file.startswith(prefix) for repo_file in repo_files])

    for repo_path in repo_paths:  # Make sure the specified paths are present and valid.
        if (repo_path not in repo_files) and no_prefixed_files(repo_path.rstrip("*")):
            repo_files.update(list_files("--error-unmatch", repo_path, cwd=cwd))

    return sorted(repo_files)


def print_scan_header(file_count: int, verbose: bool, colors: CliColors) -> None:
    """Prints a header containing a summary (i.e. number of files) for the scan task."""
    file_count_text = f"{file_count} file{'' if (file_count == 1) else 's'}"
    template = Template("\nScanning ${file_count_text}...")
    if verbose:
        print(colors.highlight(template.substitute(file_count_text=file_count_text)))
    else:
        print(template.substitute(file_count_text=colors.highlight(file_count_text)))


def scan_file_for_token(
    file_number: int, filename: str, colors: CliColors, label_display_width: int
) -> bool:
    """Returns whether the file contains a bot token, & optionally prints the result."""

    def show_filename(color: Callable[[str], str] | None = None, ext: str = "") -> None:
        """Prints the file name/num in a pretty format if `label_display_width` != 0."""
        if label_display_width:
            print(
                colors.primary(f"{str(file_number).rjust(label_display_width)} ")
                + (color(f"{filename} [{ext}]") if (color and ext) else filename)
            )

    if is_text_file(filename):
        with open(filename, encoding="utf-8") as file:
            if TOKEN_PATTERN.search(file.read()):
                show_filename(colors.warning, "WARNING: Contains plaintext token.")
                return True
            else:
                show_filename()
    else:
        show_filename(colors.lowlight, "SKIPPED: Not a text file.")

    return False
