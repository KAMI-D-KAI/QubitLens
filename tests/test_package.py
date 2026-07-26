"""Tests for the top-level QubitLens package."""

import qubitlens


def test_package_version() -> None:
    """The package should expose its current version."""
    assert qubitlens.__version__ == "0.1.0"