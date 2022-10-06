from __future__ import annotations

import re
from pathlib import Path
from typing import Final, Iterable, NamedTuple

import pytest

_SLOW: Final[str] = "slow"
_SKIP_SLOW: Final[str] = "--skip-slow"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "-S", _SKIP_SLOW, action="store_true", help="Skip tests that are slow to run."
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", f"{_SLOW}: marks a test as slow to run.")


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Iterable[pytest.Item],
) -> None:
    if config.getoption(_SKIP_SLOW):
        skip_slow_marker = pytest.mark.skip(f"Running with {_SKIP_SLOW} option.")
        for item in items:
            if _SLOW in item.keywords:
                item.add_marker(skip_slow_marker)


class CliAction(NamedTuple):
    output_pattern: str
    input_response: str
    echo_input: bool = True

    @classmethod
    def list(cls, *args: tuple[str, str] | tuple[str, str, bool]) -> list[CliAction]:
        return [cls(*arg) for arg in args]


@pytest.fixture
def mock_get_input(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    cli_actions: list[CliAction],
) -> None:
    output_patterns = (re.compile(ca.output_pattern, re.DOTALL) for ca in cli_actions)
    echoed_inputs = (ca.input_response for ca in cli_actions if ca.echo_input)
    hidden_inputs = (ca.input_response for ca in cli_actions if not ca.echo_input)

    def get_input(_, prompt: str, *, echo_input: bool = True) -> str:
        stdout = f"{capsys.readouterr().out}{prompt} "
        print(stdout, end="")  # Put that thing back where it came from or so help me!
        assert next(output_patterns).search(stdout) is not None

        if echo_input:
            response = next(echoed_inputs)
            print(response)
        else:
            response = next(hidden_inputs)
            print()

        return response

    monkeypatch.setattr("botstrap.internal.clisession.CliSession.get_input", get_input)


@pytest.fixture(autouse=True)
def mock_get_default_keys_dir(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    if "get_default_keys_dir" not in request.function.__name__:
        monkeypatch.setattr(
            "botstrap.internal.metadata.Metadata.get_default_keys_dir",
            lambda: tmp_path / ".botstrap_keys",
        )


@pytest.fixture
def mock_get_metadata(monkeypatch, meta_prog: list[str], meta_desc: str | None) -> None:
    monkeypatch.setattr(
        "botstrap.internal.metadata.Metadata.get_program_command", lambda _: meta_prog
    )
    monkeypatch.setattr(
        "botstrap.internal.metadata.Metadata.get_package_info",
        lambda *_: {"summary": meta_desc},
    )


@pytest.fixture
def meta_prog() -> list[str]:
    return ["python", "bot.py"]
