from __future__ import annotations

from dataclasses import asdict, dataclass
from string import Template
from typing import Any, Callable, Iterable, overload


@dataclass(eq=False, frozen=True, kw_only=True)
class Strings:
    """A `dataclass` specifying the strings to be used by the Botstrap-provided CLI.

    The attributes of this class are strings, `string.Template` objects, and tuples of
    strings. Collectively, they determine the text that is displayed in the console when
    you run a script that utilizes Botstrap.

    Preconfigured string setups are provided by this class's `default()` and `compact()`
    methods. If you desire further customization, you can create a new instance of this
    class and specify any strings you'd like to change. All constructor arguments are
    keyword-only.

    Example:
        >>> from botstrap import Botstrap, Strings
        >>> from string import Template
        >>>
        >>> bot_strings = Strings(
        >>>     discord_login_attempt=Template("Logging in with '$token_label' token."),
        >>>     discord_login_success=Template(
        >>>         "$bot_identifier reporting for duty in $token_label mode!"
        >>>     ),
        >>> )
        >>> Botstrap(strings=bot_strings).run_bot()

        $ python bot.py

        bot: Logging in with 'default' token.
        bot: BasicBot#1234 reporting for duty in default mode!
    """

    @classmethod
    def default(cls) -> Strings:
        """Returns an instance of this class with default values for all attributes.

        The default strings are all in English and include ample vertical spacing (e.g.
        extra newlines between sections of text) for ease of reading.
        """
        return cls()

    @classmethod
    def compact(cls) -> Strings:
        """Returns an instance of this class with vertical spacing minimized.

        In other words, the semantic contents of all attributes are the same as they are
        in the `default()` collection of strings, but any newline characters are either
        removed (for newlines at the beginning and end of a string) or replaced by a
        space (for newlines in the middle of a string).
        """
        default_items = asdict(cls.default()).items()
        return cls(**{key: _get_compact_value(value) for key, value in default_items})

    bot_token_prompt: str = "BOT TOKEN"
    bot_token_mismatch: Template = Template(
        "Decrypted keyfile data for $token_label doesn't look like a bot token.\n"
    )
    bot_token_missing: Template = Template(
        "Keyfile for $token_label bot token doesn't exist.\n"
    )
    bot_token_missing_add: Template = Template(
        "You currently don't have a saved $token_label bot token."
        "\nWould you like to add one now?"
    )
    bot_token_creation_cue: str = (
        "\nPlease enter your bot token now. It'll be invisible for security reasons."
    )
    bot_token_creation_hint: str = (
        "\nThat doesn't seem like a valid bot token. It should look like this:"
    )
    bot_token_creation_mismatch: str = (
        "\nPlease make sure you have the correct token, then try again."
    )
    bot_token_creation_success: str = (
        "\nYour token has been successfully encrypted and saved."
    )
    bot_token_creation_run: str = "\nDo you want to use this token to run your bot now?"
    bot_token_mgmt_none: str = "You currently don't have any saved bot tokens.\n"
    bot_token_mgmt_list: str = "You currently have the following bot tokens saved:"
    bot_token_mgmt_delete: str = (
        "\nWould you like to permanently delete any of these tokens?"
    )
    bot_token_deletion_cue: str = "Please enter the ID of the token to delete:"
    bot_token_deletion_mismatch: str = "\nThat doesn't match any of your saved tokens."
    bot_token_deletion_hint: Template = Template("Expected one of: $examples")
    bot_token_deletion_retry: str = "\nWould you like to try again?"
    bot_token_deletion_success: str = "\nToken successfully deleted."
    password_prompt: str = "PASSWORD"
    password_cue: Template = Template(
        "Please enter the password to decrypt your $token_label bot token."
    )
    password_mismatch: str = (
        "Please make sure you have the correct password, then try again.\n"
    )
    password_creation_info: Template = Template(
        "\nTo keep your bot token extra safe, it must be encrypted with a password."
        "\nThis password won't be stored anywhere. It will only be used as a key to"
        "\ndecrypt your token every time you run your bot in $token_label mode."
    )
    password_creation_cue: Template = Template(
        "\nPlease enter a password for your $token_label token."
    )
    password_creation_hint: Template = Template(
        "\nYour password must be at least $min_length characters long."
    )
    password_creation_retry: str = "Would you like to try a different one?"
    password_confirmation_cue: str = (
        "\nPlease re-enter the same password again to confirm."
    )
    password_confirmation_hint: str = (
        "\nThat password doesn't match your original password."
    )
    password_confirmation_retry: str = "Would you like to try again?"
    affirmation_instruction: str = "If so, type"
    affirmation_conjunction: str = "or"
    affirmation_responses: tuple[str, ...] = ("yes", "y")
    cli_prefix_main: Template = Template("\n$program_name:")
    cli_prefix_error: str = "error:"
    cli_desc_info: Template = Template(
        'Run "$program_name" with no parameters to start the bot$token_specifier.'
    )
    cli_desc_info_specifier: Template = Template("in $token_label mode")
    cli_desc_token_id: Template = Template(
        "The ID of the token to use to run the bot ($token_ids)."
    )
    cli_desc_manage_tokens: str = "View/manage your saved Discord bot tokens."
    cli_desc_version: str = "Display the currently installed version."
    cli_desc_help: str = "Display this help message."
    discord_login_attempt: Template = Template(
        "$token_label: Attempting to log in to Discord..."
    )
    discord_login_success: Template = Template(
        '$token_label: Successfully logged in as "$bot_identifier".\n'
    )
    discord_login_failure: str = (
        "Failed to log in. Make sure your bot token is configured properly."
    )
    exit_keyboard_interrupt: str = "\n\nReceived a keyboard interrupt."
    exit_user_choice: str = "\nReceived a non-affirmative response."
    exit_notice: str = "Exiting process.\n"

    def get_affirmation_prompt(
        self,
        format_response: Callable[[str], str] | None = None,
        quote_responses: bool = True,
    ) -> str:
        """Returns a string prompting the user for an affirmative response.

        Responses considered "affirmative" are defined by the `affirmation_responses`
        attribute of an instance of this class, which is a tuple that consists of the
        strings "yes" and "y" by default.

        Example:
            >>> from botstrap import Strings
            >>> pig_latin = lambda text: f"{text[1:]}{text[0]}ay"
            >>> Strings.default().get_affirmation_prompt(format_response=pig_latin)
            'If so, type "esyay" or "yay"'

        Args:
            format_response:
                A function that takes an affirmative response string and returns a
                version of that string with any desired custom formatting applied. This
                may be set to one of the class methods of `Color`, as a simple way to
                emphasize the valid responses to the prompt.
            quote_responses:
                Whether to wrap each possible affirmative response in double quotes.
                These quotes are added after `format_response()` is invoked on the
                response (if provided). Defaults to `True`.

        Returns:
            A string prompting the user for an affirmative response.
        """

        def get_display_response(response: str):
            if format_response:
                response = format_response(response)
            if quote_responses:
                response = f'"{response.strip()}"'
            return response

        responses = [get_display_response(resp) for resp in self.affirmation_responses]
        conj, sep = self.affirmation_conjunction.strip(), ", "

        return f"{self.affirmation_instruction.strip()} " + (
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
