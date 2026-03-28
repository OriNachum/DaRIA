"""Shared test fixtures for DaRIA."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_log_dir(tmp_path: Path) -> Path:
    """Temporary directory for log files."""
    return tmp_path / "logs"
