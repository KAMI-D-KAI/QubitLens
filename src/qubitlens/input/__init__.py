"""QubitLens mathematical input subsystem.

Validates and parses human-typed mathematical input into QubitLens
domain values, so downstream layers never touch raw user text.
"""

from qubitlens.input.errors import InputError
from qubitlens.input.expression import evaluate

__all__ = ["InputError", "evaluate"]
