from getpass import getpass
from typing import Callable, Final, Optional

from botstrap.colors import _colors as _c
from botstrap.strings import _strings as _s

_YES_RESPONSES: Final[tuple[str, str]] = ("yes", "y")


def confirm_or_exit(question: str) -> None:
    if not get_bool_input(question):
        exit_process(_s.exit_user_choice, is_error=False)


def exit_process(reason: str, is_error: bool = True) -> None:
    colored_reason = _c.error(reason) if is_error else _c.lowlight(reason)
    print(f"{colored_reason} {_c.lowlight(_s.exit_notice)}")
    raise SystemExit(1 if is_error else 0)


def get_bool_input(question: str) -> bool:
    colored_prompt = '" or "'.join(_c.highlight(resp) for resp in _YES_RESPONSES)
    result = get_input(f'{question} If so, type "{colored_prompt}":')
    return result.strip("'\"").lower() in _YES_RESPONSES


def get_hidden_input(
    prompt: str,
    format_text: Optional[Callable[[str], str]] = None,
) -> str:
    result = get_input(colored_prompt := _c.highlight(f"{prompt}:"), hidden=True)
    output = (format_text and format_text(result)) or _c.lowlight("*" * len(result))
    print(f"\033[F\033[1A{colored_prompt} {output}")  # Overwrites the previous line.
    return result


def get_input(prompt: str, hidden: bool = False) -> str:
    # Use `print` for the prompt to ensure that any escape codes are formatted properly.
    # However, override the default `end` with " " to keep user input on the same line.
    print(prompt, end=" ")
    # Leading and trailing whitespace is stripped from the result before it's returned.
    return (getpass(prompt="") if hidden else input()).strip()
