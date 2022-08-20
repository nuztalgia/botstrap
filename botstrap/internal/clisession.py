"""This module contains the `CliSession` class, which facilitates command-line I/O."""
from __future__ import annotations

from getpass import getpass
from typing import Callable, Final

from botstrap.colors import CliColors
from botstrap.strings import CliStrings


class CliSession:
    """Defines UX state for a program, to ensure a consistent look and feel for its CLI.

    **UX state** consists of a combination of [`CliColors`][botstrap.CliColors] and
    [`CliStrings`][botstrap.CliStrings]. These are set by the constructor arguments upon
    creating an instance of this class, and can subsequently be accessed through the
    instance's read-only properties.

    This class also provides a number of helper functions for CLI input and output. In
    order to maintain a consistent UX for your program, these functions should be used
    for all interactions that require anything beyond a simple `#!py print()` statement.

    ??? info "Info - Prerequisite for the examples"
        All of the examples in this class reference a `CliSession` variable named `cli`,
        which may be created as follows:

        ```pycon
        >>> from botstrap.internal import CliSession
        >>> cli = CliSession(name="cli-demo")
        ```

        To keep the examples focused and brief, the above definition is only explicitly
        written out once in this section. However, <u>**all**</u> of the examples will
        fail with a `#!py NameError` if the `cli` variable is not defined.
    """

    def __init__(
        self,
        name: str,
        colors: CliColors = CliColors.default(),
        strings: CliStrings = CliStrings.default(),
    ) -> None:
        """Initializes a new `CliSession` instance.

        Args:
            name:
                The name of your program. Will be displayed in some CLI messages and may
                be used to look up package metadata.
            colors:
                The colors to be used by the CLI.
            strings:
                The strings to be used by the CLI.
        """
        self._name: Final[str] = name
        self._colors: Final[CliColors] = colors
        self._strings: Final[CliStrings] = strings

    @property
    def name(self) -> str:
        """The name of the program that owns this `CliSession`."""
        return self._name

    @property
    def colors(self) -> CliColors:
        """The [`CliColors`][botstrap.CliColors] used by this instance."""
        return self._colors

    @property
    def strings(self) -> CliStrings:
        """The [`CliStrings`][botstrap.CliStrings] used by this instance."""
        return self._strings

    def confirm_or_exit(self, question: str) -> None:
        # noinspection PyUnresolvedReferences
        """Exits the program if the user responds non-affirmatively to a prompt.

        If the user responds affirmatively, this function will return without raising
        any errors, allowing program execution to continue normally.

        ??? example colored-output ends-with-input
            ```pycon
            >>> cli.confirm_or_exit("Would you like to continue?")
            Would you like to continue? If so, type "yes" or "y":
            ```

        Args:
            question:
                The first part of the prompt. Should be phrased as a question that can
                be meaningfully answered by a "yes" or "no" response.

        Raises:
            SystemExit: If the user responds non-affirmatively. Will be raised with
                exit code `#!py 0`.
        """
        if not self.get_bool_input(question):
            self.exit_process(self.strings.m_exit_by_choice, is_error=False)

    def exit_process(self, reason: str, is_error: bool = True) -> None:
        # noinspection PyUnresolvedReferences
        """Exits the program in a user-friendly manner.

        By default, the provided `reason` will be colored either `red`{.red} or
        `grey`{.grey} (depending on the value of `is_error`) when it is displayed
        in the console.

        ??? example
            ```{.pycon .colored-output}
            >>> cli.exit_process("Just testing the 'exit_process()' function!")
            Just testing the 'exit_process()' function! Exiting process.
            ```

            ```console title="Console Session"
            Process finished with exit code 0
            ```

            **Note:** Depending on your shell settings, the text in the second code
            block (titled "Console Session") may or may not be displayed. This does not
            change the behavior of this function, which is unaffected by what gets
            printed after its process is terminated.

        Args:
            reason:
                A simple explanation for why the program is ending.
            is_error:
                Whether the program is ending due to an error. Determines its exit code
                and the color of the displayed `reason` text.

        Raises:
            SystemExit: If `is_error` is `True`, this will be raised with exit code
                `#!py 1` to indicate an "abnormal" exit. Otherwise, it will be raised
                with exit code `#!py 0` to indicate a "successful" exit.
        """
        reason = self.colors.error(reason) if is_error else self.colors.lowlight(reason)
        print(f"{reason} {self.colors.lowlight(self.strings.m_exiting)}")
        raise SystemExit(1 if is_error else 0)

    def get_bool_input(self, question: str) -> bool:
        # noinspection PyUnresolvedReferences
        """Returns a boolean value corresponding to the user's response to a prompt.

        ??? example colored-output
            ```pycon
            >>> if cli.get_bool_input("Do you believe in life after love?"):
            ...     print("I can feel something inside me say...")
            ... else:
            ...     print("I really don't think you're strong enough, no!")
            ...
            Do you believe in life after love? If so, type "yes" or "y": umm...
            I really don't think you're strong enough, no!
            ```

            **Note:** You might have to hit the "Enter" or "Return" key an additional
            time after pasting this example into the console, to force the interpreter
            to recognize the end of the `#!py if` statement.

        Args:
            question:
                The first part of the prompt. Should be phrased as a question that can
                be meaningfully answered by a "yes" or "no" response.

        Returns:
            `True` if the user responds affirmatively, otherwise `False`.
        """
        colored_prompt = self.strings.get_affirmation_prompt(
            format_response=self.colors.highlight, quote_responses=True
        )
        result = self.get_input(f"{question} {colored_prompt}:").strip("'\"").lower()
        return result in self.strings.m_affirm_responses

    def get_hidden_input(
        self,
        prompt: str,
        format_input: Callable[[str], str] | None = None,
    ) -> str:
        # noinspection PyUnresolvedReferences
        """Returns the user's input without echoing. Prints a safe representation of it.

        In this context, "echoing" is displaying the user's input on the screen as they
        type. For security reasons, it's undesirable when dealing with sensitive data.

        This function tries to provide a user-friendly experience without leaking the
        resulting input. If the descriptions in the "Parameters" section below are
        undesirable for your use case, consider using
        [`get_input()`][botstrap.internal.CliSession.get_input]
        (with the keyword argument `#!py echo_input=False`) instead of this function.

        ??? example colored-output
            ```pycon
            >>> very_secure_password = cli.get_hidden_input("Enter your password")
            Enter your password: *******
            >>> print(very_secure_password)  # NEVER do this with a real password!
            hunter2
            ```

        Args:
            prompt:
                A short human-readable prompt for the user. Will always be followed by a
                colon (`:`) and a space, and will be highlighted if colors are enabled.
            format_input:
                A function that accepts the raw input and returns a string that can be
                safely displayed. If omitted, the input will be displayed as a sequence
                of asterisks (one `*` for each character in the input).

        Returns:
            The user's response as a string, stripped of leading & trailing whitespace.
        """
        colored_prompt = self.colors.highlight(f"{prompt}:")
        result = self.get_input(colored_prompt, echo_input=False)
        if not (output := format_input and format_input(result)):
            output = self.colors.lowlight("*" * len(result))
        print(f"\033[F\033[1A{colored_prompt} {output}")  # Overwrite the previous line.
        return result

    # noinspection PyMethodMayBeStatic
    def get_input(self, prompt: str, *, echo_input: bool = True) -> str:
        # noinspection PyUnresolvedReferences
        """Returns the user's input, with the option to turn off echoing.

        In this context, "echoing" is displaying the user's input on the screen as they
        type. For security reasons, it's undesirable when dealing with sensitive data.

        This function does not do anything special to format its console output. If you
        require sensitive user input with more nuanced console output, consider using
        [`get_hidden_input()`][botstrap.internal.CliSession.get_hidden_input] instead.

        ??? example
            ```pycon
            >>> print(cli.get_input("Baby shark,"))
            Baby shark, doo doo doo
            doo doo doo
            ```

        Args:
            prompt:
                A short human-readable prompt for the user. Will be followed by a space.
            echo_input:
                Whether the user's input should be displayed on the screen. Set this to
                `False` for sensitive input.

        Returns:
            The user's response as a string, stripped of leading & trailing whitespace.
        """
        # Use `print` for the prompt to ensure any escape codes are formatted properly,
        # but override the default `end` with " " to keep user input on the same line.
        print(prompt, end=" ")
        # Strip all leading and trailing whitespace from the input before returning it.
        return (input() if echo_input else getpass(prompt="")).strip()

    def print_prefixed(
        self,
        message: str = "",
        is_error: bool = False,
        suppress_newline: bool = False,
    ) -> None:
        # noinspection PyUnresolvedReferences
        """Prints a message prefixed by the program name, and optionally an error label.

        ??? example
            ```pycon
            >>> cli.print_prefixed("What does the fox say?")
            cli-demo: What does the fox say?
            >>> cli.print_prefixed("Ring-ding-ding-ding-dingeringeding!", is_error=True)
            cli-demo: error: Ring-ding-ding-ding-dingeringeding!
            ```

        Args:
            message:
                A human-readable string to display. If omitted, only the prefix will be
                printed, followed by a space instead of the usual newline. This allows
                subsequent text to be printed on the same line (after the prefix).
            is_error:
                Whether an error label should be included in the prefix.
            suppress_newline:
                Whether to end the printed message with a space instead of a newline,
                even if `message` is non-empty.
        """
        program_name = self.colors.primary(self.name)
        program_prefix = self.strings.m_prefix.substitute(program_name=program_name)
        error_text = self.strings.m_prefix_error.strip() if is_error else None
        end = "\n" if (message and not suppress_newline) else " "
        print(" ".join(s for s in (program_prefix, error_text, message) if s), end=end)
