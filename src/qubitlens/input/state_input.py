"""Scientific state input.

Turns user-friendly state descriptions into validated
:class:`InitialState` objects by evaluating amplitude expressions
through the safe expression engine.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

from qubitlens.domain.initial_state import InitialState
from qubitlens.input.errors import InputError
from qubitlens.input.expression import evaluate
from qubitlens.input.parameters import Bindings


def _bitstring_to_index(bits: str, num_qubits: int) -> int:
    """Return the little-endian integer index for a bit-string.

    ``bits[0]`` is qubit 0 (the least-significant bit).
    """
    if not isinstance(bits, str) or len(bits) != num_qubits:
        raise InputError(f"Bit-string {bits!r} must have length {num_qubits}.")
    if any(c not in "01" for c in bits):
        raise InputError(f"Bit-string {bits!r} contains non-binary characters.")
    return sum((1 << i) for i, c in enumerate(bits) if c == "1")


def _evaluate_amp(expr: str, bindings: Bindings | None) -> complex:
    if not isinstance(expr, str):
        raise InputError(
            f"Amplitude must be a string expression, got {type(expr).__name__}."
        )
    return evaluate(expr, bindings=bindings)


def from_vector(
    amplitudes: Sequence[str],
    num_qubits: int,
    bindings: Bindings | None = None,
) -> InitialState:
    """Build an ``InitialState`` from a sequence of amplitude expressions."""
    expected = 2**num_qubits
    if len(amplitudes) != expected:
        raise InputError(
            f"Expected {expected} amplitudes for "
            f"{num_qubits} qubits, got {len(amplitudes)}."
        )
    vec = np.zeros(expected, dtype=complex)
    for i, expr in enumerate(amplitudes):
        vec[i] = _evaluate_amp(expr, bindings)
    return InitialState(amplitudes=tuple(complex(a) for a in vec))


def from_basis_dict(
    amplitudes: Mapping[str, str],
    num_qubits: int,
    bindings: Bindings | None = None,
) -> InitialState:
    """Build an ``InitialState`` from bit-string keys to amplitude expressions.

    Keys are bit-strings; values are amplitude expressions.
    """
    dim = 2**num_qubits
    vec = np.zeros(dim, dtype=complex)
    seen: set[int] = set()
    for bits, expr in amplitudes.items():
        idx = _bitstring_to_index(bits, num_qubits)
        if idx in seen:
            raise InputError(f"Duplicate basis state {bits!r}.")
        seen.add(idx)
        vec[idx] = _evaluate_amp(expr, bindings)
    return InitialState(amplitudes=tuple(complex(a) for a in vec))


def from_sparse_dict(
    amplitudes: Mapping[int, str],
    num_qubits: int,
    bindings: Bindings | None = None,
) -> InitialState:
    """Build an ``InitialState`` from integer indices to amplitude expressions.

    Keys are integer basis indices; values are amplitude expressions.
    """
    dim = 2**num_qubits
    vec = np.zeros(dim, dtype=complex)
    seen: set[int] = set()
    for idx, expr in amplitudes.items():
        if not isinstance(idx, int) or idx < 0 or idx >= dim:
            raise InputError(f"Basis index {idx} out of range [0, {dim}).")
        if idx in seen:
            raise InputError(f"Duplicate basis index {idx}.")
        seen.add(idx)
        vec[idx] = _evaluate_amp(expr, bindings)
    return InitialState(amplitudes=tuple(complex(a) for a in vec))
