"""This module contains the `Metadata` class, which provides metadata-related utils."""
from __future__ import annotations

import sys
from email.errors import MessageError
from importlib import import_module
from importlib.metadata import (
    PackageNotFoundError,
    entry_points,
    metadata,
    packages_distributions,
)
from pathlib import Path
from types import ModuleType
from typing import Final, Iterator, NamedTuple

_CURRENT_DIR: Final[Path] = Path(".").resolve()
_MAIN_MODULE: Final[ModuleType] = sys.modules["__main__"]


class Metadata:
    """A collection of utility functions related to file, package, and program metadata.

    This class relies heavily on the [`sys`][1], [`pathlib`][2], and [`importlib`][3]
    modules, all of which are part of the [Python Standard Library][4]. Links to
    specific sections in the documentation for those modules (and other useful
    resources) are provided where relevant in each function description.

    [1]: https://docs.python.org/3/library/sys.html
    [2]: https://docs.python.org/3/library/pathlib.html
    [3]: https://docs.python.org/3/library/importlib.html
    [4]: https://docs.python.org/3/library/index.html
    """

    class BotClassInfo(NamedTuple):
        """A `NamedTuple` containing information for an available Discord bot class."""

        qualified_name: str
        """The fully-qualified name of an available class representing a Discord bot."""

        run_method_name: str = "run"
        """The name of the method to run the bot. May accept a bot token parameter."""

        init_with_token: bool = False
        """Whether to pass the token into the constructor instead of the run method."""

    @classmethod
    def get_bot_class_info(cls) -> BotClassInfo:
        """Returns info about a Discord bot class that may be imported and instantiated.

        The return value of this function is a subclass of `NamedTuple` that will
        contain information about a bot class from **one** of the Python Discord
        libraries for which Botstrap includes built-in support: [discord.py][1],&nbsp;
        [disnake][2],&nbsp; [hikari][3],&nbsp; [interactions.py][4],&nbsp;
        [NAFF][5],&nbsp; [Nextcord][6], or&thinsp;&thinsp;[Pycord][7].

        If multiple supported libraries are installed, then one of them will be chosen
        arbitrarily. If **none** of the supported libraries are installed, this function
        will raise a `RuntimeError`.

        [1]: https://github.com/Rapptz/discord.py
        [2]: https://github.com/DisnakeDev/disnake
        [3]: https://github.com/hikari-py/hikari
        [4]: https://github.com/interactions-py/library
        [5]: https://github.com/NAFTeam/NAFF
        [6]: https://github.com/nextcord/nextcord
        [7]: https://github.com/Pycord-Development/pycord

        ??? info "Info - Contents of the resulting tuple"
            This function's return type, `BotClassInfo`, is fundamentally just a `tuple`
            with three named fields:

            - `qualified_name: str` <br>
              The fully-qualified name of an available class representing a Discord bot.
            - `run_method_name: str` <br>
              The name of the method to run the bot. May accept a bot token parameter.
              Defaults to `"run"`.
            - `init_with_token: bool` <br>
              Whether to pass the token into the constructor instead of the run method.
              Defaults to `False`.

        Returns:
            A `NamedTuple` containing information about the bot class to instantiate.

        Raises:
            RuntimeError: If none of the Python Discord libraries with built-in support
                are installed and/or recognized.
        """
        discord_libs = [
            lib_name
            for p, package_library_names in packages_distributions().items()
            if p in ("discord", "disnake", "hikari", "interactions", "naff", "nextcord")
            # Pycord is supported too - it's included under the "discord" namespace.
            for lib_name in package_library_names
            if not ((p == "discord") and (lib_name == "nextcord"))  # False positive.
        ]
        try:
            return cls.BotClassInfo(
                *{  # type: ignore[arg-type]
                    "discord.py": ("discord.Client",),
                    "py-cord": ("discord.Bot",),
                    "disnake": ("disnake.ext.commands.InteractionBot",),
                    "hikari": ("hikari.GatewayBot", "run", True),
                    "discord-py-interactions": ("interactions.Client", "start", True),
                    "naff": ("naff.Client", "start"),
                    "nextcord": ("nextcord.ext.commands.Bot",),
                }[discord_libs[0]]
            )
        except (IndexError, KeyError):
            raise RuntimeError(
                "Cannot automatically determine the class to use for the Discord bot."
            ) from None

    @classmethod
    def get_default_keys_dir(cls) -> Path:
        """Returns the path of the default key storage directory for the current script.

        By default, Botstrap [`.key`](../secret#key-files) files are stored in a
        directory named `.botstrap_keys`. This directory is usually placed in the
        same location as the file containing the
        [`"__main__"`][botstrap.internal.Metadata.get_main_file_path] module for the
        executing script. If the main module cannot be found, `.botstrap_keys` will
        be located in the current working directory.

        The path returned by this function is **not** guaranteed to point to an
        already-existing directory.

        [1]: https://docs.python.org/3/library/pathlib.html#concrete-paths

        Returns:
            The `Path` of the default key storage directory for the current script.
        """
        parent_dir = main.parent if (main := cls.get_main_file_path()) else _CURRENT_DIR
        return parent_dir / ".botstrap_keys"

    @classmethod
    def get_main_file_path(cls) -> Path | None:
        """Returns the path of the file containing the main module, if it can be found.

        The **main module** (a.k.a. [`"__main__"`][1]) is essentially the top-level
        environment of the currently executing script. In most applications, it can be
        accessed through `sys.modules["__main__"]`, and therefore this function is
        able to return a valid path most of the time.

        However, in niche cases (such as when a "script" is run using Python's [`-c`][2]
        command-line option), this function will be unable to find the main module and
        will therefore return `None`.

        [1]: https://docs.python.org/3/library/__main__.html#module-__main__
        [2]: https://docs.python.org/3/using/cmdline.html#cmdoption-c

        Returns:
            The `Path` of the `"__main__"` module if it can be found, otherwise `None`.
        """
        main_file = getattr(_MAIN_MODULE, "__file__", "") or (sys.argv and sys.argv[0])
        if main_file and (main_path := Path(main_file).resolve()).exists():
            return main_path
        else:
            return None

    @classmethod
    def get_package_info(cls, package_name: str = "") -> dict[str, str | list[str]]:
        """Returns a dictionary containing any available metadata about the package.

        This function uses the `metadata()` function from [`importlib.metadata`][1]
        to retrieve information about the specified package. If successful, it will
        return a dictionary in which the keys are strings corresponding to the fields
        defined by Python's [core metadata][2]. As detailed in that specification, each
        value (if present) will either be a `str` or a `list[str]`.

        If `package_name` belongs to a package that cannot be found or whose metadata
        is otherwise unavailable, this function will simply return an empty `dict`.

        [1]: https://docs.python.org/3/library/importlib.metadata.html
        [2]: https://packaging.python.org/en/latest/specifications/core-metadata/

        Args:
            package_name:
                The name of the package to fetch metadata for.

        Returns:
            A dictionary containing the available metadata for the specified package.
        """
        if (not package_name) and not (package_name := _MAIN_MODULE.__package__ or ""):
            package_name = vars(_MAIN_MODULE).get("__requires__", "")
        try:
            return (package_name and metadata(package_name).json) or {}
        except (MessageError, PackageNotFoundError):
            return {}

    @classmethod
    def get_program_command(cls, program_name: str) -> list[str]:
        """Returns a list of strings mirroring a command for running the current script.

        If the given program name matches the name of a console script returned
        by [`entry_points()`][1], this function will simply return a single-item
        `list` consisting of the `program_name` string.

        Otherwise, this function will iterate through [`sys.orig_argv`][2] in order
        to approximate a "minimum viable command" for running the current script.
        The resulting `list` will include everything from the name of the
        [`sys.executable`][3] up to (and including) the first string that is either
        **a)** the name of an existing file, or **b)** a non-optional argument.

        [1]: https://docs.python.org/3/library/importlib.metadata.html#entry-points
        [2]: https://docs.python.org/3/library/sys.html#sys.orig_argv
        [3]: https://docs.python.org/3/library/sys.html#sys.executable

        Args:
            program_name:
                The name of the currently executing program. This may be user-provided,
                and thus does not necessarily match any of the strings actually used in
                the command to run the script.

        Returns:
            A `list` where each `str` is part of the command to run the current script.
        """
        if program_name in entry_points(group="console_scripts").names:
            return [program_name]

        def get_top_level_args() -> Iterator[str]:
            """Yields strings from `orig_argv` up to/including a non-option arg/file."""
            for arg in sys.orig_argv:
                arg_as_path = Path(arg)
                if arg == sys.executable:  # The Python executable (e.g. "python").
                    yield arg_as_path.stem
                elif arg_as_path.exists():
                    try:
                        yield str(arg_as_path.relative_to("."))
                    except ValueError:
                        yield arg_as_path.name
                    return  # Stop iteration upon encountering the name of a valid file.
                else:
                    yield arg
                    if not arg.startswith("-"):
                        return  # Stop iteration upon encountering a "non-option" arg.

        return list(get_top_level_args())

    @classmethod
    def guess_program_name(cls) -> str | None:
        """Returns a possible name for the current program/script, if one can be found.

        When the name of the current program needs to be displayed but its owner hasn't
        explicitly specified that name, this function may be used to obtain an "educated
        guess". :disguised_face:

        The first source of a possible name is
        [`get_package_info()`][botstrap.internal.Metadata.get_package_info], called
        without a `package_name` (which doesn't necessarily result in well-defined
        behavior). Failing that, this function will try to pick a relevant name out of
        the path of the [`"__main__"`][botstrap.internal.Metadata.get_main_file_path]
        module (if it's available) or the current working directory. If neither source
        yields a viable name, this function will return `None`.

        Returns:
            A name for the program if a reasonable guess can be made, otherwise `None`.
        """
        if isinstance(package_name := cls.get_package_info().get("name"), str):
            return package_name

        def is_relevant_name(path_name: str) -> bool:
            """Returns `True` if no "indicators of irrelevance" appear in the path."""
            return not any(name in path_name.lower() for name in ("main", "src"))

        dirs_to_climb = 2  # Climbing too far up will also yield irrelevant names.
        relevant_path = cls.get_main_file_path() or _CURRENT_DIR

        for path in [relevant_path, *relevant_path.parents[:dirs_to_climb]]:
            if path.exists() and is_relevant_name(path.name):
                return path.resolve().name

        return None

    @classmethod
    def import_class(cls, qualified_class_name: str) -> type:
        """Returns the class if it can be imported. If unsuccessful, raises an error.

        This function uses [`import_module()`][1] to dynamically import the specified
        class. Note that the class name **must be fully-qualified** (i.e. include its
        module name, *à la* `module_name.ClassName`) in order for the import to be
        successful. If for any reason the import is unsuccessful, this function will
        raise an `ImportError` or a subclass thereof.

        [1]: https://docs.python.org/3/library/importlib.html#importlib.import_module

        Args:
            qualified_class_name:
                The fully-qualified name of the class to import.

        Returns:
            The `type` of the specified class, if it was imported successfully.

        Raises:
            ImportError: If the class cannot be imported successfully in the current
                environment. This may be caused by missing dependencies and/or a mistake
                in the provided `qualified_class_name`.
        """
        module_name, _, class_name = qualified_class_name.rpartition(".")
        result = getattr(import_module(module_name), class_name, None)
        if isinstance(result, type):
            return result
        else:
            raise ImportError(f"Failed to import '{qualified_class_name}'.")
