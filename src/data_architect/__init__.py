"""Data Architect: Scaffold OpenCode AI agents for data warehouse design."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("data-architect")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
