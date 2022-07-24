from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from botstrap.secrets import Secret
from botstrap.utils import green, yellow

_LENGTHS: Final[tuple[int, ...]] = (24, 6, 27)
_PATTERN: Final[re.Pattern] = re.compile(r"\.".join(r"[\w-]{%i}" % i for i in _LENGTHS))
_PLACEHOLDER: Final[str] = ".".join("*" * i for i in _LENGTHS)


class Token(Secret):
    def __init__(
        self,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
    ) -> None:
        super().__init__(
            uid, requires_password, display_name, storage_directory, _PATTERN.fullmatch
        )

    @classmethod
    def default_dev(cls) -> Token:
        return cls("dev", requires_password=False, display_name=yellow("development"))

    @classmethod
    def default_prod(cls) -> Token:
        return cls("prod", requires_password=True, display_name=green("production"))
