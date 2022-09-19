from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

if __name__ == "__main__":
    install_location = Path(__file__).resolve().parent
    try:
        print(f"Botstrap v{version('botstrap')} is installed at '{install_location}'.")
    except PackageNotFoundError:
        print("Botstrap is not installed in the current environment.")
