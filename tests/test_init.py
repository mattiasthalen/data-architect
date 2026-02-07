"""Tests for data_architect package initialization."""

import data_architect


def test_package_is_importable() -> None:
    """Verify the package can be imported."""
    assert data_architect is not None


def test_version_is_string() -> None:
    """Verify __version__ is a non-empty string."""
    assert isinstance(data_architect.__version__, str)
    assert len(data_architect.__version__) > 0


def test_version_not_unknown() -> None:
    """Verify version is not the fallback (package is installed)."""
    assert "+unknown" not in data_architect.__version__
