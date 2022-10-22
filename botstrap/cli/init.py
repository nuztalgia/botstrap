"""This module contains functions used by the `botstrap init` standalone CLI command."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template
from typing import Final
from urllib.request import urlopen

from botstrap import CliColors
from botstrap.cli.utils import get_discord_lib, get_lib_example, initialize_git, slugify
from botstrap.internal import CliSession, Metadata

_RAW_REPO_URL: Final[str] = "https://raw.githubusercontent.com/nuztalgia/botstrap/main"


def initialize_bot(
    name: str = "",
    no_slugs: bool = False,
    no_install: bool = False,
    colors: CliColors = CliColors.off(),
) -> int:
    """Returns 0 if a new Discord bot was successfully initialized, or 1 if not."""
    if discord_lib := get_discord_lib(colors):
        print(f"\nPreparing to initialize a new {colors.primary(discord_lib)} bot.")
        return BotstrapInitializer(colors, discord_lib).run(
            bot_name=name,
            slugify_bot_name=not no_slugs,
            install_bot=not no_install,
        )
    else:
        return 1  # An error message will already have been printed.


class BotstrapInitializer(CliSession):
    """Encapsulates the Discord bot setup/creation flow in Botstrap's standalone CLI."""

    def __init__(self, colors: CliColors, discord_lib: str) -> None:
        """Initializes a new `BotstrapInitializer` instance."""
        super().__init__(name="botstrap", colors=colors)
        self.discord_lib: Final[str] = discord_lib
        self.cwd: Final[Path] = Path.cwd().resolve()

    def run(self, bot_name: str, slugify_bot_name: bool, install_bot: bool) -> int:
        """Calls internal methods & returns 0 if a new bot was created, or 1 if not."""
        try:
            bot_name, bot_dir = self._get_bot_info(bot_name, slugify_bot_name)
        except KeyboardInterrupt:
            exit_text = f"{self.strings.m_exit_by_interrupt} Exiting initialization.\n"
            print(self.colors.lowlight(exit_text))
            return 1

        bot_dir_text = self.colors.lowlight(f"({bot_dir})")
        if bot_dir.is_dir():
            print(f"\nUsing existing directory. {bot_dir_text}")
        else:
            print(f"\nCreating new directory. {bot_dir_text}")
            bot_dir.mkdir(parents=True)

        if not initialize_git(bot_dir, self.colors):
            return 1  # An error message will already have been printed.

        bot_package = re.sub(r"[^a-z0-9]", "", bot_name.lower())
        if not self._initialize_all_files(bot_dir, bot_name, bot_package):
            warning = "No files were created. It looks like that bot already exists."
            print(f"\n{self.colors.warning(warning)}\n")
            return 1

        print(self.colors.success("\nSuccessfully created all required files!\n"))

        if install_bot and self._install_bot(bot_dir, bot_name):
            command = self.colors.highlight(bot_name)
            command_dir = "any directory"
        else:
            if install_bot:
                warning = "An editable installation could not be created at this time."
                print(f"\033[F\033[1A{self.colors.warning(warning)}\n")
            command = self.colors.highlight(f"python -m {bot_package}")
            command_dir = (
                f"the {self.colors.primary(relative_dir)} directory"
                if ((relative_dir := str(bot_dir.relative_to(self.cwd))) != ".")
                else "this directory"
            )

        print(f"To run your new bot, use the {command} command from {command_dir}.\n")
        return 0

    def _get_bot_info(self, bot_name: str, slugify_bot_name: bool) -> tuple[str, Path]:
        """Returns a tuple of the name & path that should be used to create the bot."""
        if bot_name:
            message = f"Provided bot name: '{bot_name}'."
        else:
            message = f"Bot name not provided. Using directory name: '{self.cwd.name}'."
            bot_name = self.cwd.name
        print(self.colors.lowlight(f"  - {message}"))

        is_sub_dir = self.cwd.name != bot_name  # Check for equality before slugifying.
        slugified_name = slugify(bot_name) if slugify_bot_name else bot_name

        if bot_name == slugified_name:
            message = "Using name as-is (no slugification)."
        else:
            message = (
                f"Using slugified bot name: '{bot_name}' -> '{slugified_name}'."
                f"\n    (To disable this behavior, use the '-s' option.)"
            )
            bot_name = slugified_name
        print(self.colors.lowlight(f"  - {message}"))

        preset_dirs = {self.cwd, self.cwd / bot_name}
        while not (bot_dir := self._confirm_bot_dir(bot_name, is_sub_dir, preset_dirs)):
            is_sub_dir = not is_sub_dir

        return bot_name, bot_dir

    def _confirm_bot_dir(
        self, name: str, is_sub_dir: bool, preset_dirs: set[Path]
    ) -> Path | None:
        """Returns a path for the bot directory if the user confirms, otherwise None."""
        if preset_dirs:
            bot_dir = (self.cwd / name) if is_sub_dir else self.cwd
        else:
            bot_dir = None

        while not bot_dir:
            bot_dir = self.cwd / self.get_input(
                "\nPlease enter the name of the directory in which to create your bot:"
            )
            if bot_dir.is_file():
                filename = self.colors.primary(str(bot_dir.relative_to(self.cwd)))
                self.confirm_or_exit(
                    f"{self.colors.error('ERROR:')} {filename} is the name of an "
                    "existing file.\n\nWould you like to choose a different name?"
                )
                bot_dir = None

        preset_dirs.discard(bot_dir)
        print(f"\nWill create bot files in: {self.colors.primary(str(bot_dir))}")
        return bot_dir if self.get_bool_input("Is this correct?") else None

    def _initialize_all_files(
        self, bot_dir: Path, bot_name: str, bot_package: str
    ) -> bool:
        """Initializes all the necessary files to set up a bot with the given library.

        If a file with a targeted name already exists, this function will not overwrite
        it, regardless of its contents. This function will return `True` if at least one
        new file was created, or `False` if all the targeted file names already existed.
        """
        bot_class = "".join(s.title() for s in re.split(r"[\W_]", bot_name))

        def get_package_version(package_name: str) -> str:
            """Returns a version constraint if available, otherwise the empty string."""
            version = Metadata.get_package_info(package_name)["version"]
            return f" == {version}" if (version and isinstance(version, str)) else ""

        botstrap_version = get_package_version("botstrap")
        discord_lib_version = get_package_version(self.discord_lib)

        def get_pypi_link(package_name: str) -> str:
            """Returns a Markdown-formatted link for the specified package on PyPI."""
            return f"[`{package_name}`](https://pypi.org/project/{package_name})"

        readme_file_contents = (
            f"# {bot_name}\n\nA Discord bot powered by "
            f"{get_pypi_link(self.discord_lib)} and {get_pypi_link('botstrap')}.\n"
        )

        def fetch_file_from_url(url: str) -> str:
            """Opens the given url (must be https) and returns its contents as a str."""
            if not url.startswith("https://"):
                raise ValueError(f"File URL must start with 'https': {url}")
            return urlopen(url, timeout=10).read().decode()

        def get_file_contents(source_path: str) -> str:
            """Fetches and returns the file template with all placeholders filled in."""
            template_url = f"{_RAW_REPO_URL}/botstrap/cli/templates/{source_path}"
            return Template(fetch_file_from_url(template_url)).safe_substitute(
                bot_class=bot_class,
                bot_name=bot_name,
                bot_package=bot_package,
                botstrap_version=botstrap_version,
                discord_lib=self.discord_lib,
                discord_lib_version=discord_lib_version,
            )

        discord_lib_id = re.sub(r"(?:[a-z]+-){2,}|\.|-", "", self.discord_lib)
        main_file_template = Template(get_file_contents("__main__.txt"))
        main_footer_unindented = get_file_contents(f"footers/{discord_lib_id}.txt")

        main_file_contents = main_file_template.safe_substitute(
            main_header=get_file_contents(f"headers/{discord_lib_id}.txt"),
            main_footer=main_footer_unindented.replace("\n", "\n    ").strip(),
        )

        lib_example = get_lib_example(discord_lib_id)
        lib_example_file_name, lib_example_file_url = (
            f"{bot_package}/{lib_example[1]}",
            f"{_RAW_REPO_URL}/examples/libraries/{discord_lib_id}_bot/{lib_example[0]}",
        )
        (bot_dir / lib_example_file_name).parent.mkdir(parents=True, exist_ok=True)

        return 0 != sum(
            self._initialize_file(bot_dir / file_name, file_contents)
            for file_name, file_contents in [
                (".gitattributes", "* text=auto eol=lf\n"),
                (".gitignore", get_file_contents(".gitignore")),
                ("README.md", readme_file_contents),
                ("pyproject.toml", get_file_contents("pyproject.txt")),
                (f"{bot_package}/__init__.py", 'VERSION: str = "1.0.0"\n'),
                (f"{bot_package}/__main__.py", main_file_contents),
                (lib_example_file_name, fetch_file_from_url(lib_example_file_url)),
            ]
        )

    def _initialize_file(self, file_path: Path, file_contents: str) -> bool:
        """Writes the contents to the given path if it isn't already an existing file.

        Will return `True` if the file was written; `False` if the name was unavailable.
        """
        display_path = self.colors.primary(str(file_path.relative_to(self.cwd)))
        if file_path.exists():
            print(
                self.colors.lowlight(f"Skipping file {display_path}")
                + self.colors.lowlight(" because it already exists.")
            )
            return False
        else:
            print(f"Creating file: {display_path}")
            file_path.write_text(file_contents, newline="\n")
            return True

    def _install_bot(self, bot_dir: Path, bot_name: str) -> bool:
        """Returns `True` if an editable installation was created, or `False` if not."""
        is_venv = sys.prefix != sys.base_prefix
        venv_label = " in the current virtual env" if is_venv else ""
        print(
            f"Setting up {'an' if is_venv else 'a global'} editable installation"
            f" of {self.colors.highlight(bot_name)}{venv_label}...\n"
        )

        status_finished_regex = re.compile(": finished with status '(.+)'\n")
        omission_regex = re.compile("(^Requirement already satisfied|[a-z0-9]{50,}\n)")

        install_proc = subprocess.Popen(
            [shutil.which("pip") or f"{sys.executable} -m pip", "install", "-e", "."],
            cwd=bot_dir,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        for output_line in install_proc.stdout:  # type: ignore[union-attr]
            if output_line.startswith("Successfully "):
                print(self.colors.success(f"{output_line.strip()}!\n"))
            elif (status_index := output_line.find(": started")) > 0:
                print(self.colors.lowlight(f"{output_line[:status_index]}..."), end=" ")
            elif status_match := status_finished_regex.search(output_line):
                print(self.colors.lowlight(f"{status_match[1]}."))
            elif not omission_regex.search(output_line):
                print(self.colors.lowlight(output_line.replace("///", " ")), end="")

        install_proc.communicate()
        return install_proc.returncode == 0
