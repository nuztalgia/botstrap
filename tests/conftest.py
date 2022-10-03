from typing import Final, Iterable

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
