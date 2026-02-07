"""Allow running data_architect as a module: python -m data_architect."""

from data_architect.cli import app

if __name__ == "__main__":  # pragma: no cover
    app()
