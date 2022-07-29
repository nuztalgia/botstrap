from __future__ import annotations

from getpass import getpass
from typing import Callable, Final

from botstrap.colors import Colors
from botstrap.strings import Strings


class Manager:
    def __init__(self, colors: Colors, strings: Strings) -> None:
        self._colors: Final[Colors] = colors
        self._strings: Final[Strings] = strings
        self._cli: Final[CLI] = CLI(self)

    @property
    def cli(self) -> CLI:
        return self._cli

    @property
    def colors(self) -> Colors:
        return self._colors

    @property
    def strings(self) -> Strings:
        return self._strings


class CLI:
    def __init__(self, manager: Manager) -> None:
        self.manager: Final[Manager] = manager

    def confirm_or_exit(self, question: str) -> None:
        if not self.get_bool_input(question):
            self.exit_process(self.manager.strings.exit_user_choice, is_error=False)

    def exit_process(self, reason: str, is_error: bool = True) -> None:
        colors = self.manager.colors
        colored_reason = colors.error(reason) if is_error else colors.lowlight(reason)
        print(f"{colored_reason} {colors.lowlight(self.manager.strings.exit_notice)}")
        raise SystemExit(1 if is_error else 0)

    def get_bool_input(self, question: str) -> bool:
        colored_prompt = self.manager.strings.get_affirmation_prompt(
            format_response=self.manager.colors.highlight, quote_responses=True
        )
        result = self.get_input(f"{question} {colored_prompt}:").strip("'\"").lower()
        return result in self.manager.strings.affirmation_responses

    def get_hidden_input(
        self,
        prompt: str,
        format_text: Callable[[str], str] | None = None,
    ) -> str:
        colored_prompt = self.manager.colors.highlight(f"{prompt}:")
        result = self.get_input(colored_prompt, hidden=True)
        if not (output := format_text and format_text(result)):
            output = self.manager.colors.lowlight("*" * len(result))
        print(f"\033[F\033[1A{colored_prompt} {output}")  # Overwrite the previous line.
        return result

    # noinspection PyMethodMayBeStatic
    def get_input(self, prompt: str, hidden: bool = False) -> str:
        # Use `print` for the prompt to ensure any escape codes are formatted properly,
        # but override the default `end` with " " to keep user input on the same line.
        print(prompt, end=" ")
        # Strip all leading and trailing whitespace from the input before returning it.
        return (getpass(prompt="") if hidden else input()).strip()
