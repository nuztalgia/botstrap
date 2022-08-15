"""This module contains a class that defines all the strings used by Botstrap's CLI."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from string import Template
from typing import Any, Callable, Iterable, overload


@dataclass(eq=False, frozen=True, kw_only=True)
class CliStrings:
    """A model for the strings used by the Botstrap-provided CLI.

    The fields of this class are strings,
    [`Template`](https://docs.python.org/3/library/string.html#template-strings)
    strings, and tuples of strings. Collectively, they determine the text that is
    displayed in the console when you run a script that utilizes Botstrap.

    Preconfigured strings are provided by the [`default()`][botstrap.CliStrings.default]
    and [`compact()`][botstrap.CliStrings.compact] class methods. If you desire further
    customization, you can create a new instance of this class and specify any values
    you'd like to change. All constructor arguments correspond to field names and are
    keyword-only.

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
        ```py title="bot.py" hl_lines="5-6"
        from botstrap import BotstrapFlow, CliStrings
        from string import Template

        bot_strings = CliStrings(
            m_login=Template("Logging in with '$token' bot token."),
            m_login_success=Template("$bot_id reporting for duty in $token mode!"),
        )
        BotstrapFlow(strings=bot_strings).run_bot()
        ```

        ```console title="Console Session"
        $ python bot.py

        bot: Logging in with 'default' bot token.
        bot: BasicBot#1234 reporting for duty in default mode!
        ```

        **Note:** The strings customized in this example belong to the fields named
        `m_login` and `m_login_success`. <br> See the info box above for an explanation
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

    """ NOTE: This class defines **a lot** of fields.
    To keep things organized, they're split up according to the following categories:

    1. Basic `#!py str` values (a.k.a. string literals)
    2. `Template` strings with only a `${token}` placeholder
    3. `Template` strings with assorted placeholders
    4. `tuple` objects containing any number of strings

    Within each of these sections, fields are sorted alphabetically, with an extra
    newline separating each prefix group. See the info box in the class description
    for an explanation of field name prefixes.
    """

    # region FIELDS

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Section #1  -  Basic `str` values (a.k.a. string literals)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    h_help: str = "Display this help message."
    h_tokens: str = "View/manage your saved Discord bot tokens."
    h_version: str = "Display the current bot version."

    m_affirm_cue: str = "If so, type"
    m_conj_or: str = "or"
    m_exit_by_choice: str = "\nReceived a non-affirmative response."
    m_exit_by_interrupt: str = "\n\nReceived a keyboard interrupt."
    m_exiting: str = "Exiting process.\n"
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
    t_delete_cue: str = "Please enter the ID of the token to delete:"
    t_delete_mismatch: str = "\nThat doesn't match any of your saved tokens."
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
        'Run "${program_name}" with no parameters to start the bot${mode_addendum}.'
    )
    h_token_id: Template = Template(
        "The ID of the token to use to run the bot: ${token_ids}"
    )

    m_login_success: Template = Template(
        '${token}: Successfully logged in as "${bot_id}".\n'
    )
    m_prefix: Template = Template("\n${program_name}:")

    p_create_hint: Template = Template(
        "\nYour password must be at least ${min_length} characters long."
    )

    t_delete_hint: Template = Template("Expected one of: ${token_ids}")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #   Section #4  -  `tuple` objects containing any number of strings
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    m_affirm_responses: tuple[str, ...] = ("yes", "y")

    # endregion FIELDS

    def get_affirmation_prompt(
        self,
        format_response: Callable[[str], str] | None = None,
        quote_responses: bool = True,
    ) -> str:
        """Returns a string prompting the user for an affirmative response.

        Responses considered "affirmative" are defined by the `m_affirm_responses`
        field, which is a tuple that consists of the strings "yes" and "y" by default.

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
                This may be set to one of the class methods of [`Color`][botstrap.Color]
                for a simple way to emphasize the valid responses to the prompt.
            quote_responses:
                Whether to wrap each possible affirmative response in double quotes
                (`"`). These quotes are added after `format_response` is invoked on
                the response (if it was provided).

        Returns:
            A string prompting the user for an affirmative response.
        """

        def get_display_response(response: str):
            if format_response:
                response = format_response(response)
            if quote_responses:
                response = f'"{response.strip()}"'
            return response

        responses = [get_display_response(resp) for resp in self.m_affirm_responses]
        conj, sep = self.m_conj_or.strip(), ", "

        return f"{self.m_affirm_cue.strip()} " + (
            f" {conj} ".join(responses)
            if len(responses) < 3
            else f"{sep.join(responses[:-1])}{sep}{conj} {responses[-1]}"
        )


@overload
def _get_compact_value(value: str) -> str:  # type: ignore[misc]
    ...


@overload
def _get_compact_value(value: Iterable[str]) -> tuple[str, ...]:
    ...


@overload
def _get_compact_value(value: Template) -> Template:
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
    elif isinstance(value, Iterable):
        # Recursively call this function on each item in the iterable, and use
        # tuple comprehension to assemble the results into an immutable object.
        return tuple(_get_compact_value(item) for item in value)
    elif isinstance(value, Template):
        # Construct a new Template in which the template string is produced by
        # recursively calling this function on the original template string.
        return Template(_get_compact_value(value.template))
    else:
        # In theory, there shouldn't be any other value types, but just in case...
        return _get_compact_value(str(value))
