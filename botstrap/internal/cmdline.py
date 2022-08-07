from __future__ import annotations

from getpass import getpass
from typing import Callable, Final

from botstrap.internal.colors import ThemeColors
from botstrap.internal.strings import Strings


class CliManager:
    """Manages UX state to ensure a consistent look and feel for the CLI.

    Maintains state corresponding to the following constructor arguments, and allows
    subsequent read-only property access to their values.

    Args:
        name:
            The name of the bot or program. Printed as a prefix for high-level CLI
            messages, and may also be used to look up package metadata (if applicable).
        colors:
            A `ThemeColors` instance specifying the colors to be used by the CLI.
        strings:
            A `Strings` instance specifying the strings to be used by the CLI.
    """

    def __init__(self, name: str, colors: ThemeColors, strings: Strings) -> None:
        self._name: Final[str] = name
        self._colors: Final[ThemeColors] = colors
        self._strings: Final[Strings] = strings
        self._cli: Final[CliUtils] = CliUtils(self)

    @property
    def name(self) -> str:
        """The name of the bot/program that created this instance."""
        return self._name

    @property
    def colors(self) -> ThemeColors:
        """The `ThemeColors` used by the CLI for this instance."""
        return self._colors

    @property
    def strings(self) -> Strings:
        """The `Strings` used by the CLI for this instance."""
        return self._strings

    @property
    def cli(self) -> CliUtils:
        """A collection of CLI utility functions that adhere to this instance's UX."""
        return self._cli


# noinspection PyUnresolvedReferences
class CliUtils:
    """A collection of CLI utilities that adhere to the UX defined by a `CliManager`.

    Args:
        manager:
            A `CliManager` instance specifying the `ThemeColors` and `Strings` to be
            used by the CLI.
    """

    def __init__(self, manager: CliManager) -> None:
        self.manager: Final[CliManager] = manager

    def confirm_or_exit(self, question: str) -> None:
        """Exits the program if the user responds non-affirmatively to a prompt.

        If the user responds affirmatively, this method will return without raising an
        error, allowing program execution to continue normally.

        Example:
            >>> cli.confirm_or_exit("Would you like to continue?")
            Would you like to continue? If so, type "yes" or "y":

        Args:
            question:
                The text to display as part of the user prompt. Should be phrased as a
                yes/no question, because it will be followed by additional text telling
                the user how to proceed.

        Raises:
            SystemExit:
                If the user responds non-affirmatively.
        """
        if not self.get_bool_input(question):
            self.exit_process(self.manager.strings.x_reason_choice, is_error=False)

    def exit_process(self, reason: str, is_error: bool = True) -> None:
        """Exits the program in a user-friendly manner.

        Example:
            >>> cli.exit_process("Received a keyboard interrupt.", is_error=False)
            Received a keyboard interrupt. Exiting process.

        Args:
            reason:
                A brief human-readable explanation for why the program is ending.
            is_error:
                Whether the program is ending due to an error. Determines the exit
                status passed to `SystemExit()` and the color of the displayed `reason`
                text. Defaults to `False`.

        Raises:
            SystemExit:
                Will be called with exit status `0` (a "successful" exit) if `is_error`
                is `False`, or `1` (an "abnormal" exit) if `is_error` is `True`.
        """
        colors = self.manager.colors
        colored_reason = colors.error(reason) if is_error else colors.lowlight(reason)
        print(f"{colored_reason} {colors.lowlight(self.manager.strings.x_exiting)}")
        raise SystemExit(1 if is_error else 0)

    def get_bool_input(self, question: str) -> bool:
        """Returns a boolean value corresponding to the user's response to a prompt.

        Example:
            >>> if cli.get_bool_input(f"Does {member} like pineapple on pizza?"):
            >>>     member.ban(reason="Disgusting.")

        Args:
            question:
                The text to display as part of the user prompt. Should be phrased as a
                yes/no question, because it will be followed by additional text telling
                the user how to proceed.

        Returns:
            `True` if the user responds affirmatively, or `False` if the user responds
            non-affirmatively.
        """
        colored_prompt = self.manager.strings.get_affirmation_prompt(
            format_response=self.manager.colors.highlight, quote_responses=True
        )
        result = self.get_input(f"{question} {colored_prompt}:").strip("'\"").lower()
        return result in self.manager.strings.m_affirm_responses

    def get_hidden_input(
        self,
        prompt: str,
        format_text: Callable[[str], str] | None = None,
    ) -> str:
        """Returns the user's input without echoing (i.e. displaying it on the screen).

        This method automatically takes care of formatting the input/output according
        to the expected styles. If a more basic (but still hidden) input experience is
        desired, use the `get_input()` method with its `hidden` argument set to `True`.

        Example:
            >>> very_secure_password = cli.get_hidden_input("Enter your password")
            Enter your password: *******
            >>> print(very_secure_password)
            hunter2

        Args:
            prompt:
                A short human-readable prompt for the user. Will be automatically
                highlighted (if colors are enabled) and followed by a colon (":").
            format_text:
                An optional function that takes the raw user input string and returns
                a string that will be displayed on-screen in place of the user input.
                If omitted, the result will be displayed as a sequence of asterisks
                ("*") matching the length of the user input string.

        Returns:
            The user's response as a string, stripped of leading & trailing whitespace.
        """
        colored_prompt = self.manager.colors.highlight(f"{prompt}:")
        result = self.get_input(colored_prompt, hidden=True)
        if not (output := format_text and format_text(result)):
            output = self.manager.colors.lowlight("*" * len(result))
        print(f"\033[F\033[1A{colored_prompt} {output}")  # Overwrite the previous line.
        return result

    # noinspection PyMethodMayBeStatic
    def get_input(self, prompt: str, *, hidden: bool = False) -> str:
        """Returns the user's input as a string (optionally without echoing).

        This method does not do anything to format the input/output besides appending a
        space to the prompt (and hiding the user's input if `hidden` is set to `True`).
        For fancier formatting of sensitive input, use the `get_hidden_input()` method.

        Example:
            >>> print(cli.get_input("Baby shark"))
            Baby shark doo doo doo
            doo doo doo

        Args:
            prompt:
                A short human-readable prompt for the user.
            hidden:
                Whether the user's input should be concealed (i.e. not displayed on the
                screen). Set this to `True` for sensitive input. Defaults to `False`.

        Returns:
            The user's response as a string, stripped of leading & trailing whitespace.
        """
        # Use `print` for the prompt to ensure any escape codes are formatted properly,
        # but override the default `end` with " " to keep user input on the same line.
        print(prompt, end=" ")
        # Strip all leading and trailing whitespace from the input before returning it.
        return (getpass(prompt="") if hidden else input()).strip()

    def print_prefixed_message(
        self,
        message: str = "",
        is_error: bool = False,
        suppress_newline: bool = False,
    ) -> None:
        """Prints a message prefixed by the bot name (and optionally an error label).

        The bot name is automatically read from the `CliManager` that was provided to
        instantiate this class.

        Example:
            >>> cli.print_prefixed_message("What does the fox say?")
            bot: What does the fox say?
            >>> cli.print_prefixed_message("Wa-pa-pa-pa-pa-pa-pow!", is_error=True)
            bot: error: Wa-pa-pa-pa-pa-pa-pow!

        Args:
            message:
                A human-readable string to display. If omitted or empty, only the prefix
                will be printed, followed by a space instead of the usual newline.
                Subsequent messages/prompts may then be printed on the same line, after
                the prefix. Default value is the empty string.
            is_error:
                Whether an error label (e.g. "error:") should be included in the prefix.
                Defaults to `False`.
            suppress_newline:
                Whether to end the printed message with a space instead of a newline,
                even when `message` is non-empty. Defaults to `False`.

        Returns:
            Nothing.
        """
        name = self.manager.colors.primary(self.manager.name)
        prefix = self.manager.strings.m_prefix.substitute(program_name=name)
        error_text = self.manager.strings.m_prefix_error.strip() if is_error else None
        end = "\n" if (message and not suppress_newline) else " "
        print(" ".join(s for s in (prefix, error_text, message) if s), end=end)
