import sys
from email.errors import MessageError
from importlib import import_module
from importlib.metadata import PackageNotFoundError, entry_points, metadata
from pathlib import Path
from types import ModuleType
from typing import Final, Iterator, Optional

_MAIN_MODULE: Final[ModuleType] = sys.modules["__main__"]


class Metadata:
    """A collection of utilities related to file, package, and program metadata."""

    @classmethod
    def get_main_file_path(cls) -> Path:
        """Returns the `Path` containing the `__main__` module, if it can be found."""
        main_file = _MAIN_MODULE.__file__ or (sys.argv and sys.argv[0])
        if main_file and (main_path := Path(main_file).resolve()).exists():
            return main_path
        else:
            raise OSError("Could not locate main module file.")

    @classmethod
    def get_package_info(cls, package_name: str = "") -> dict[str, str | list[str]]:
        """Returns a dictionary containing any available metadata about the package."""
        if (not package_name) and not (package_name := _MAIN_MODULE.__package__ or ""):
            package_name = vars(_MAIN_MODULE).get("__requires__", "")
        try:
            # noinspection PyUnresolvedReferences
            return metadata(package_name).json
        except (MessageError, PackageNotFoundError):
            return {}

    @classmethod
    def get_program_command(cls, name: str) -> list[str]:
        """Returns a str list mirroring the command used to run the current script."""
        # noinspection PyArgumentList, PyUnresolvedReferences
        if name in entry_points(group="console_scripts").names:
            return [name]
        else:
            return list(cls._get_top_level_args())

    @classmethod
    def guess_program_name(cls) -> Optional[str]:
        """Returns a possible name for the current program, if one can be found."""
        if isinstance(package_name := cls.get_package_info().get("name"), str):
            return package_name

        irrelevant_names = ("main", "src")
        dirs_to_climb = 2  # Climbing too many dirs will also yield irrelevant names.

        def is_relevant_name(path_name: str) -> bool:
            return not any(name in path_name.lower() for name in irrelevant_names)

        for path in [main := cls.get_main_file_path(), *main.parents[:dirs_to_climb]]:
            if path.exists() and is_relevant_name(path.name):
                return path.name

        return None

    @classmethod
    def import_class(cls, qualified_name: str) -> Optional[type]:
        """Returns the class if it can be imported, otherwise raises `ImportError`."""
        module_name, _, class_name = qualified_name.rpartition(".")
        result = getattr(import_module(module_name), class_name, None)
        return result if result and isinstance(result, type) else None

    @classmethod
    def _get_top_level_args(cls) -> Iterator[str]:
        for arg in sys.orig_argv:
            arg_as_path = Path(arg)
            if arg == sys.executable:
                yield arg_as_path.stem
            elif arg_as_path.exists():
                try:
                    yield str(arg_as_path.relative_to("."))
                except ValueError:
                    yield arg_as_path.name
                return
            else:
                yield arg
                if not arg.startswith("-"):
                    return
