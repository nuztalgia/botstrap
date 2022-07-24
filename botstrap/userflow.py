from getpass import getpass
from typing import Callable, Final, Optional

from botstrap.strings import Strings
from botstrap.utils import cyan, grey, red

_YES_RESPONSES: Final[tuple[str, str]] = ("yes", "y")


def confirm_or_exit(question: str, strs: Strings) -> None:
    if not get_bool_input(question):
        exit_process(strs.exit_user_choice, is_error=False)


def exit_process(reason: str, is_error: bool = True) -> None:
    colored_reason = red(reason) if is_error else grey(reason)
    print(f"\n{colored_reason} {grey('Exiting process.')}\n")
    raise SystemExit(1 if is_error else 0)


def get_bool_input(question: str) -> bool:
    colored_prompt = '" or "'.join(cyan(response) for response in _YES_RESPONSES)
    result = get_input(f'{question} If so, type "{colored_prompt}":')
    return result.strip("'\"").lower() in _YES_RESPONSES


def get_hidden_input(
    prompt: str,
    format_text: Optional[Callable[[str], str]] = None,
) -> str:
    result = get_input(colored_prompt := cyan(f"{prompt}:"), hidden=True)
    output = grey((format_text and format_text(result)) or "*" * len(result))
    print(f"\033[F\033[1A{colored_prompt} {output}")  # Overwrites the previous line.
    return result


def get_input(prompt: str, hidden: bool = False) -> str:
    # Use `print` for the prompt to ensure that any escape codes are formatted properly.
    # However, override the default `end` with " " to keep user input on the same line.
    print(prompt, end=" ")
    # Leading and trailing whitespace is stripped from the result before it's returned.
    return (getpass(prompt="") if hidden else input()).strip()
