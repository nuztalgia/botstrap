from __future__ import annotations

from pathlib import Path
from typing import Final

from botstrap.cli import Manager
from botstrap.colors import Colors
from botstrap.strings import Strings
from botstrap.tokens import Token


class Botstrap(Manager):
    def __init__(
        self,
        colors: Colors = Colors.default(),
        strings: Strings = Strings.default(),
    ) -> None:
        super().__init__(colors, strings)
        self._tokens_by_uid: Final[dict[str, Token]] = {}

    def register_token(
        self,
        uid: str,
        requires_password: bool = False,
        display_name: str | None = None,
        storage_directory: str | Path | None = None,
        silent: bool = False,
    ) -> Botstrap:
        token = Token(self, uid, requires_password, display_name, storage_directory)
        if (not silent) and (token.uid in self._tokens_by_uid):
            raise ValueError(f'A token with unique ID "{token.uid}" already exists.')
        self._tokens_by_uid[token.uid] = token
        return self
