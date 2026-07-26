"""Tests for QubitLens operator construction utilities."""

import numpy as np
import pytest

from qubitlens.core.gates import H, X
from qubitlens.core.operators import build_single_qubit_operator


def test_single_qubit_operator_is_gate_itself() -> None:
    """Embedding into a one-qubit register should return the gate."""
    operator = build_single_qubit_operator(
        X,
        target=0,
        num_qubits=1,
    )

    assert np.allclose(operator, X)


def test_target_zero_in_two_qubit_register() -> None:
    """Qubit 0 should occupy the right tensor factor."""
    operator = build_single_qubit_operator(
        X,
        target=0,
        num_qubits=2,
    )

    expected = np.kron(np.eye(2), X)

    assert np.allclose(operator, expected)


def test_target_one_in_two_qubit_register() -> None:
    """Qubit 1 should occupy the left tensor factor."""
    operator = build_single_qubit_operator(
        X,
        target=1,
        num_qubits=2,
    )

    expected = np.kron(X, np.eye(2))

    assert np.allclose(operator, expected)


def test_operator_dimension_for_three_qubits() -> None:
    """A three-qubit operator should have dimension 8x8."""
    operator = build_single_qubit_operator(
        H,
        target=1,
        num_qubits=3,
    )

    assert operator.shape == (8, 8)


def test_embedded_operator_is_unitary() -> None:
    """Embedding a unitary gate should preserve unitarity."""
    operator = build_single_qubit_operator(
        H,
        target=1,
        num_qubits=3,
    )

    identity = np.eye(8, dtype=np.complex128)

    assert np.allclose(
        operator.conj().T @ operator,
        identity,
    )


def test_target_zero_action_matches_qiskit_ordering() -> None:
    """X on q0 should map |00> to |01>."""
    state = np.array([1, 0, 0, 0], dtype=np.complex128)

    operator = build_single_qubit_operator(
        X,
        target=0,
        num_qubits=2,
    )

    expected = np.array([0, 1, 0, 0], dtype=np.complex128)

    assert np.allclose(operator @ state, expected)


def test_target_one_action_matches_qiskit_ordering() -> None:
    """X on q1 should map |00> to |10>."""
    state = np.array([1, 0, 0, 0], dtype=np.complex128)

    operator = build_single_qubit_operator(
        X,
        target=1,
        num_qubits=2,
    )

    expected = np.array([0, 0, 1, 0], dtype=np.complex128)

    assert np.allclose(operator @ state, expected)


def test_invalid_gate_shape_raises() -> None:
    """Only 2x2 single-qubit gates should be accepted."""
    with pytest.raises(ValueError, match="shape"):
        build_single_qubit_operator(
            np.eye(4),
            target=0,
            num_qubits=1,
        )


def test_zero_qubits_raises() -> None:
    """An operator cannot target an empty register."""
    with pytest.raises(ValueError, match="at least one"):
        build_single_qubit_operator(
            X,
            target=0,
            num_qubits=0,
        )


def test_negative_target_raises() -> None:
    """Negative target indices should be rejected."""
    with pytest.raises(ValueError, match="outside"):
        build_single_qubit_operator(
            X,
            target=-1,
            num_qubits=2,
        )


def test_target_beyond_register_raises() -> None:
    """Targets beyond the register should be rejected."""
    with pytest.raises(ValueError, match="outside"):
        build_single_qubit_operator(
            X,
            target=2,
            num_qubits=2,
        )