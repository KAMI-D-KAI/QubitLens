"""Tests for common QubitLens gate matrices."""

import numpy as np

from qubitlens.core.gates import H, I, S, T, X, Y, Z


def test_gate_shapes() -> None:
    """Every single-qubit gate should be a 2x2 matrix."""
    for gate in (I, X, Y, Z, H, S, T):
        assert gate.shape == (2, 2)


def test_gate_dtypes_are_complex() -> None:
    """Gate matrices should use a complex-valued dtype."""
    for gate in (I, X, Y, Z, H, S, T):
        assert np.issubdtype(gate.dtype, np.complexfloating)


def test_identity_gate() -> None:
    """The identity gate should leave basis states unchanged."""
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    assert np.allclose(I @ zero, zero)
    assert np.allclose(I @ one, one)


def test_pauli_x_swaps_basis_states() -> None:
    """Pauli-X should map |0> to |1> and |1> to |0>."""
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    assert np.allclose(X @ zero, one)
    assert np.allclose(X @ one, zero)


def test_pauli_y_action() -> None:
    """Pauli-Y should introduce the expected complex phases."""
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    assert np.allclose(Y @ zero, 1j * one)
    assert np.allclose(Y @ one, -1j * zero)


def test_pauli_z_action() -> None:
    """Pauli-Z should preserve |0> and negate |1>."""
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    assert np.allclose(Z @ zero, zero)
    assert np.allclose(Z @ one, -one)


def test_hadamard_creates_expected_superpositions() -> None:
    """Hadamard should map basis states to |+> and |->."""
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    plus = np.array([1, 1], dtype=np.complex128) / np.sqrt(2)
    minus = np.array([1, -1], dtype=np.complex128) / np.sqrt(2)

    assert np.allclose(H @ zero, plus)
    assert np.allclose(H @ one, minus)


def test_s_gate_phase() -> None:
    """S should multiply the |1> amplitude by i."""
    one = np.array([0, 1], dtype=np.complex128)
    expected = np.array([0, 1j], dtype=np.complex128)

    assert np.allclose(S @ one, expected)


def test_t_gate_phase() -> None:
    """T should multiply the |1> amplitude by exp(i*pi/4)."""
    one = np.array([0, 1], dtype=np.complex128)
    expected = np.array(
        [0, np.exp(1j * np.pi / 4)],
        dtype=np.complex128,
    )

    assert np.allclose(T @ one, expected)


def test_all_gates_are_unitary() -> None:
    """Every declared quantum gate should satisfy U†U = I."""
    identity = np.eye(2, dtype=np.complex128)

    for gate in (I, X, Y, Z, H, S, T):
        assert np.allclose(gate.conj().T @ gate, identity)
