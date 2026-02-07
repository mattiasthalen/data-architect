"""Tests for data_architect.cli module."""

import pytest

from data_architect.cli import app


def test_cli_module_is_importable() -> None:
    """Verify the CLI module can be imported."""
    assert app is not None


def test_cli_stub_exits() -> None:
    """Verify the CLI stub exits with a message."""
    with pytest.raises(SystemExit):
        app()
