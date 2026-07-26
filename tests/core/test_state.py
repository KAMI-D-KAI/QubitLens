"""Tests for the QubitLens quantum state representation."""

import numpy as np
import pytest

from qubitlens.core.state import QuantumState


def test_zero_state() -> None:
    """|0> should represent a valid single-qubit state."""
    state = QuantumState(np.array([1, 0]))

    assert state.num_qubits == 1
    assert np.allclose(state.amplitudes, [1, 0])


def test_one_state() -> None:
    """|1> should represent a valid single-qubit state."""
    state = QuantumState(np.array([0, 1]))

    assert state.num_qubits == 1
    assert np.allclose(state.amplitudes, [0, 1])


def test_two_qubit_state() -> None:
    """A four-dimensional statevector should represent two qubits."""
    state = QuantumState(np.array([1, 0, 0, 0]))

    assert state.num_qubits == 2


def test_zero_qubit_state() -> None:
    """A one-dimensional statevector should represent zero qubits."""
    state = QuantumState(np.array([1]))

    assert state.num_qubits == 0
    assert np.allclose(state.probabilities, [1.0])


def test_superposition_probabilities() -> None:
    """An equal superposition should produce equal probabilities."""
    state = QuantumState(
        np.array([1, 1], dtype=np.complex128) / np.sqrt(2)
    )

    assert np.allclose(state.probabilities, [0.5, 0.5])


def test_complex_amplitude_probabilities() -> None:
    """Measurement probabilities should use amplitude magnitudes."""
    state = QuantumState(
        np.array([1, 1j], dtype=np.complex128) / np.sqrt(2)
    )

    assert np.allclose(state.probabilities, [0.5, 0.5])


def test_probability_by_basis_index() -> None:
    """A basis probability should be accessible by index."""
    state = QuantumState(
        np.array([np.sqrt(0.25), np.sqrt(0.75)])
    )

    assert np.isclose(state.probability(0), 0.25)
    assert np.isclose(state.probability(1), 0.75)


def test_invalid_basis_index_raises() -> None:
    """Out-of-range basis indices should be rejected."""
    state = QuantumState(np.array([1, 0]))

    with pytest.raises(IndexError):
        state.probability(2)

    with pytest.raises(IndexError):
        state.probability(-1)


def test_non_normalized_state_raises() -> None:
    """Non-normalized statevectors should be rejected."""
    with pytest.raises(ValueError, match="normalized"):
        QuantumState(np.array([1, 1]))


def test_invalid_dimension_raises() -> None:
    """Statevector dimensions must be powers of two."""
    amplitudes = np.ones(3, dtype=np.complex128) / np.sqrt(3)

    with pytest.raises(ValueError, match="power of two"):
        QuantumState(amplitudes)


def test_multidimensional_array_raises() -> None:
    """Statevectors must be one-dimensional."""
    with pytest.raises(ValueError, match="one-dimensional"):
        QuantumState(
            np.array(
                [
                    [1, 0],
                    [0, 0],
                ]
            )
        )


def test_input_is_copied() -> None:
    """Mutating the source array should not change the state."""
    amplitudes = np.array([1, 0], dtype=np.complex128)

    state = QuantumState(amplitudes)
    amplitudes[0] = 0

    assert np.allclose(state.amplitudes, [1, 0])