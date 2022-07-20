import colorama


def main() -> int:
    colorama.init(autoreset=True)
    try:
        _main()
    finally:
        colorama.deinit()
    return 0


def _main() -> None:
    raise NotImplementedError
