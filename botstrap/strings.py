"""This module contains the `CliStrings` class, which defines text shown in the CLI."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from string import Template
from typing import Any, Callable, Iterable, overload


@dataclass(frozen=True, kw_only=True)
class CliStrings:
    """A model for the strings used by the Botstrap-provided CLI.

    The fields of this class are strings, [`Template`][1] strings, and tuples of
    strings. Collectively, they determine the text that is displayed in the console
    when you run a script that utilizes Botstrap.

    Preconfigured strings are provided by the [`default()`][botstrap.CliStrings.default]
    and [`compact()`][botstrap.CliStrings.compact] class methods. If you desire further
    customization, you can create a new instance of this class and specify any values
    you'd like to change. All constructor arguments correspond to field names and are
    keyword-only.

    [1]: https://docs.python.org/3/library/string.html#template-strings

    ??? info "Info - Field name prefixes"
        Each field name begins with a **single-letter prefix** that indicates the
        subject of the string, defined as follows:

        | Prefix | Description                                                         |
        | ------ | ------------------------------------------------------------------- |
        |`t_`| Token-related strings regarding bot token creation/management/deletion. |
        |`p_`| Password-related strings, displayed for password-protected bot tokens.  |
        |`h_`| Help strings, printed when the `-h` argument is given to the bot script.|
        |`m_`| Miscellaneous strings that don't fall under any of the other categories.|

        These prefixes allow for better code organization and are a concise way to
        indicate the context in which a string should be used. More prefixes may be
        added as Botstrap grows and acquires new features. :person_juggling:

    ??? example "Example - Customizing the Discord login text"
        ```py title="bot.py"
        from botstrap import Botstrap, CliStrings
        from string import Template

        bot_strings = CliStrings(
            m_login=Template("Logging in with '$token' bot token."),
            m_login_success=Template("$bot_id reporting for duty in $token mode!"),
        )
        Botstrap(strings=bot_strings).run_bot()
        ```

        ```console title="Console Session"
        $ python bot.py

        bot.py: Logging in with 'default' bot token.
        bot.py: BotstrapBot#1234 reporting for duty in default mode!
        ```

        **Note:** The strings customized in this example belong to the fields named
        `m_login` and `m_login_success`.<br>See the info box above for an explanation
        of `m_` and other prefixes used in the naming of this class's fields.
    """

    @classmethod
    def default(cls) -> CliStrings:
        """Returns an instance of this class with default values for all strings.

        The default strings are all in English and include ample vertical spacing (e.g.
        additional newlines between distinct sections of text) for ease of reading.
        """
        return cls()

    @classmethod
    def compact(cls) -> CliStrings:
        """Returns an instance of this class with minimal vertical space in all strings.

        In other words, the semantic contents of all strings are unchanged from their
        [`default()`][botstrap.CliStrings.default] values, but any newline characters
        are either removed (for newlines at the beginning and end of a string) or
        replaced by a single space (for newlines in the middle of a string).
        """
        default_items = asdict(cls.default()).items()
        return cls(**{key: _get_compact_value(value) for key, value in default_items})

    """
    NOTE: This class defines a lot of fields.
    To keep things organized, they're divided into the following groups:

    1. Basic `str` values (a.k.a. string literals)
    2. `Template` strings with only a `${token}` placeholder
    3. `Template` strings with assorted placeholders
    4. `tuple` objects containing any number of strings
    """

    # region FIELDS

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Section #1  -  Basic `str` values (a.k.a. string literals)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    h_help: str = "Display this help message."
    h_tokens: str = "View/manage your saved Discord bot tokens."
    h_version: str = "Display the current bot version."

    m_affirm_cue: str = "If so, type"
    m_conj_and: str = "and"
    m_conj_or: str = "or"
    m_exit_by_choice: str = "\nReceived a non-affirmative response."
    m_exit_by_interrupt: str = "\n\nReceived a keyboard interrupt."
    m_exiting: str = "Exiting process.\n"
    m_list_sep: str = ", "
    m_login_failure: str = (
        "Failed to log in. Make sure your bot token is configured properly."
    )
    m_prefix_error: str = "error:"

    p_confirm_cue: str = "\nPlease re-enter the same password again to confirm."
    p_confirm_hint: str = "\nThat password doesn't match your original password."
    p_confirm_retry: str = "Would you like to try again?"
    p_create_retry: str = "Would you like to try a different one?"
    p_mismatch: str = (
        "Please make sure you have the correct password, then try again.\n"
    )
    p_prompt: str = "PASSWORD"

    t_create_cue: str = (
        "\nPlease enter your bot token now. It'll be invisible for security reasons."
    )
    t_create_hint: str = (
        "\nThat doesn't seem like a valid bot token. It should look like this:"
    )
    t_create_mismatch: str = (
        "\nPlease make sure you have the correct token, then try again."
    )
    t_create_success: str = "\nYour token has been successfully encrypted and saved."
    t_create_use: str = "\nDo you want to use this token to run your bot now?"
    t_delete: str = "\nWould you like to permanently delete any of these tokens?"
    t_delete_cue: str = "Please enter the number next to the token you want to delete:"
    t_delete_mismatch: str = "\nThat number doesn't match any of the above tokens."
    t_delete_retry: str = "\nWould you like to try again?"
    t_delete_success: str = "\nToken successfully deleted."
    t_manage_list: str = "You currently have the following bot tokens saved:"
    t_manage_none: str = "You currently don't have any saved bot tokens.\n"
    t_prompt: str = "BOT TOKEN"

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Section #2  -  `Template` strings with only a `${token}` placeholder
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    h_desc_mode: Template = Template("in ${token} mode")

    m_login: Template = Template("${token}: Attempting to log in to Discord...")

    p_create_cue: Template = Template(
        "\nPlease enter a password for your ${token} bot token."
    )
    p_create_info: Template = Template(
        "\nTo keep your bot token extra safe, it must be encrypted with a password."
        "\nThis password won't be stored anywhere. It will only be used as a key to"
        "\ndecrypt your token every time you run your bot in ${token} mode."
    )
    p_cue: Template = Template(
        "Please enter the password to decrypt your ${token} bot token."
    )

    t_create: Template = Template(
        "You currently don't have a saved ${token} bot token."
        "\nWould you like to add one now?"
    )
    t_mismatch: Template = Template(
        "Decrypted keyfile data for ${token} doesn't look like a bot token.\n"
    )
    t_missing: Template = Template("Keyfile for ${token} bot token doesn't exist.\n")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Section #3  -  `Template` strings with assorted placeholders
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    h_desc: Template = Template(
        'Run "${program_command}" with no parameters to start the bot${mode_addendum}.'
    )
    h_token_id: Template = Template(
        "The ID of the token to use to run the bot.\nValid options are ${token_ids}."
    )

    m_login_success: Template = Template(
        '${token}: Successfully logged in as "${bot_id}".\n'
    )
    m_prefix: Template = Template("\n${program_name}:")

    p_create_hint: Template = Template(
        "\nYour password must be at least ${min_length} characters long."
    )

    t_delete_hint: Template = Template("(Expected ${token_nums}.)")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Section #4  -  `tuple` objects containing any number of strings
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    m_affirm_responses: tuple[str, ...] = ("yes", "y")

    # endregion FIELDS

    def join_choices(
        self,
        choices: Iterable[str],
        format_choice: Callable[[str], str] | None = None,
        quote_choices: bool = True,
        conjunction: str | None = None,
        separator: str | None = None,
    ) -> str:
        """Returns a string containing the choices joined together in natural language.

        ??? example "Example - Joining lists of varying length"
            ```pycon
            >>> from botstrap import CliStrings
            >>> strings = CliStrings.default()
            >>> strings.join_choices(["head"])
            '"head"'
            >>> strings.join_choices(["head", "shoulders"])
            '"head" or "shoulders"'
            >>> strings.join_choices(["head", "shoulders", "knees"])
            '"head", "shoulders", or "knees"'
            >>> strings.join_choices(parts := ["head", "shoulders", "knees", "toes"])
            '"head", "shoulders", "knees", or "toes"'
            >>> strings.join_choices(parts, quote_choices=False)
            'head, shoulders, knees, or toes'

            ```

        Args:
            choices:
                The strings to be joined together, representing the valid choices for
                a given situation.
            format_choice:
                A function that accepts a string containing a single choice, and returns
                a version of that string with any desired custom formatting applied.
            quote_choices:
                Whether to wrap each possible choice in double quotes (`"`) after
                formatting it.
            conjunction:
                The string to insert between the last two choices, for lists of length
                `2` or more. If omitted, will default to `m_conj_or`, whose default
                value is `"or"`.
            separator:
                The string to insert between each choice, for lists of length `3` or
                more. If omitted, will default to `m_list_sep`, whose default value
                is `", "`.

        Returns:
            A string containing the choices joined together in natural language.
        """

        def get_display_choice(choice: str):
            if format_choice:
                choice = format_choice(choice)
            if quote_choices:
                choice = f'"{choice.strip()}"'
            return choice

        choices = [get_display_choice(choice) for choice in choices]
        conjunction = conjunction if (conjunction is not None) else self.m_conj_or
        separator = separator if (separator is not None) else self.m_list_sep

        if separator.endswith(" ") and conjunction and not conjunction.endswith(" "):
            conjunction += " "

        return (
            f"{' ' if conjunction.endswith(' ') else ''}{conjunction}".join(choices)
            if len(choices) < 3
            else f"{separator.join(choices[:-1])}{separator}{conjunction}{choices[-1]}"
        )

    def get_affirmation_prompt(
        self, format_response: Callable[[str], str] | None = None
    ) -> str:
        """Returns a string prompting the user for an affirmative response.

        Responses considered "affirmative" are defined by the `m_affirm_responses`
        field, which is a `tuple` that consists of the strings "yes" and "y" by default.
        Under the hood, this method simply calls `join_choices()` with the appropriate
        parameters, and then prepends `m_affirm_cue` to create an affirmation prompt.

        ??? example "Example - Using a custom response formatter"
            ```pycon
            >>> from botstrap import CliStrings
            >>> pig_latin = lambda text: f"{text[1:]}{text[0]}ay"
            >>> CliStrings.default().get_affirmation_prompt(format_response=pig_latin)
            'If so, type "esyay" or "yay"'

            ```

        Args:
            format_response:
                A function that accepts an affirmative response string and returns a
                version of that string with any desired custom formatting applied.

        Returns:
            A string prompting the user for an affirmative response.
        """
        return f"{self.m_affirm_cue.strip()} " + self.join_choices(
            choices=self.m_affirm_responses, format_choice=format_response
        )


@overload
def _get_compact_value(value: str) -> str:
    ...


@overload
def _get_compact_value(value: Template) -> Template:
    ...


@overload
def _get_compact_value(value: tuple[str]) -> tuple[str, ...]:
    ...


def _get_compact_value(value: Any) -> str | Template | tuple[str, ...]:
    """Returns a version of the input value with all newlines removed.

    This function may recursively call itself, depending on the type of the input. The
    return value will always match the type of the input value (unless an unsupported
    type was passed in, in which case a string will be returned).

    Args:
        value:
            A string, `Template` object, or tuple of strings to be "compacted".

    Returns:
        An object matching the type of the input `value`, but with all newlines removed.
    """
    if isinstance(value, str):
        value = value.strip("\n")  # First, strip any leading and/or trailing newlines.
        return value.replace("\n", " ")  # Then, replace remaining newlines with spaces.
    elif isinstance(value, Template):
        # Construct a new Template in which the template string is produced by
        # recursively calling this function on the original template string.
        return Template(_get_compact_value(value.template))
    else:  # The value is a tuple.
        # Recursively call this function on each item in the tuple, and then use
        # tuple comprehension to assemble the results into an immutable object.
        return tuple(_get_compact_value(item) for item in value)
