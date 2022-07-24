from __future__ import annotations

from dataclasses import asdict, dataclass
from string import Template


@dataclass(eq=False, frozen=True, kw_only=True)
class Strings:
    bot_token_prompt: str = "BOT TOKEN"
    bot_token_mismatch: Template = Template(
        "Decrypted keyfile data for $token_label doesn't look like a bot token.\n"
    )
    bot_token_missing: Template = Template(
        "Keyfile for $token_label token doesn't exist.\n"
    )
    bot_token_missing_add: Template = Template(
        "You currently don't have a saved bot token for $token_label."
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
    exit_user_choice: str = "Received a non-affirmative response."
    exit_notice: str = "Exiting process.\n"

    @classmethod
    def default(cls) -> Strings:
        return cls()

    @classmethod
    def compact(cls) -> Strings:
        return cls(
            **{
                key: type(value)(  # Maintain the type of the field.
                    (value.template if isinstance(value, Template) else value)
                    .strip("\n")  # First, strip any leading/trailing newlines.
                    .replace("\n", " ")  # Then, replace remaining newlines with spaces.
                )
                for key, value in asdict(cls.default()).items()
            }
        )
