import sys
from email.errors import MessageError
from importlib import import_module
from importlib.metadata import metadata
from pathlib import Path
from typing import Optional


class Metadata:
    @classmethod
    def get_main_file_path(cls) -> Path:
        main_file = sys.modules["__main__"].__file__ or (sys.argv and sys.argv[0])
        if main_file and (main_path := Path(main_file).resolve()).exists():
            return main_path
        else:
            raise OSError("Could not locate main module file.")

    @classmethod
    def get_package_info(cls, package_name: str = "") -> dict[str, str | list[str]]:
        try:
            # noinspection PyUnresolvedReferences
            return metadata(package_name).json
        except MessageError:
            return {}

    @classmethod
    def get_program_name(cls) -> Optional[str]:
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
        module_name, _, class_name = qualified_name.rpartition(".")
        result = getattr(import_module(module_name), class_name, None)
        return result if result and isinstance(result, type) else None
