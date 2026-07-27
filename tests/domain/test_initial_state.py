"""Tests for the initial-state domain model."""

import math

import pytest

from qubitlens.domain import Circuit, GateOperation, InitialState


def test_initial_state_accepts_normalized_one_qubit_state() -> None:
    """Accept a valid normalized one-qubit statevector."""
    state = InitialState((1 + 0j, 0j))

    assert state.amplitudes == (1 + 0j, 0j)
    assert state.num_qubits == 1


def test_initial_state_accepts_complex_superposition() -> None:
    """Accept a normalized statevector with complex amplitudes."""
    amplitude = 1 / math.sqrt(2)
    state = InitialState((amplitude + 0j, amplitude * 1j))

    assert state.num_qubits == 1


def test_initial_state_accepts_entangled_statevector() -> None:
    """Accept a normalized multi-qubit entangled statevector."""
    amplitude = 1 / math.sqrt(2)
    state = InitialState((amplitude + 0j, 0j, 0j, amplitude + 0j))

    assert state.num_qubits == 2


def test_initial_state_rejects_empty_amplitudes() -> None:
    """Reject an empty statevector."""
    with pytest.raises(ValueError, match="at least two values"):
        InitialState(())


def test_initial_state_rejects_zero_qubit_statevector() -> None:
    """Reject a statevector representing zero qubits."""
    with pytest.raises(ValueError, match="at least two values"):
        InitialState((1 + 0j,))


def test_initial_state_rejects_non_power_of_two_length() -> None:
    """Reject a statevector whose dimension is not a power of two."""
    with pytest.raises(ValueError, match="length must be a power of two"):
        InitialState((1 + 0j, 0j, 0j))


@pytest.mark.parametrize(
    "amplitude",
    [
        complex(float("nan"), 0.0),
        complex(float("inf"), 0.0),
        complex(float("-inf"), 0.0),
        complex(0.0, float("nan")),
        complex(0.0, float("inf")),
        complex(0.0, float("-inf")),
    ],
)
def test_initial_state_rejects_non_finite_amplitudes(amplitude: complex) -> None:
    """Reject statevectors containing non-finite amplitudes."""
    with pytest.raises(ValueError, match="only finite values"):
        InitialState((1 + 0j, amplitude))


def test_initial_state_rejects_non_normalized_statevector() -> None:
    """Reject a statevector that does not have unit norm."""
    with pytest.raises(ValueError, match="normalized to unit length"):
        InitialState((1 + 0j, 1 + 0j))


def test_initial_state_derives_qubit_count_from_dimension() -> None:
    """Derive the qubit count from the statevector dimension."""
    state = InitialState((1 + 0j,) + (0j,) * 7)

    assert state.num_qubits == 3


def test_zero_constructs_all_zero_basis_state() -> None:
    """Construct the all-zero computational basis state."""
    state = InitialState.zero(3)

    assert state.amplitudes == (1 + 0j,) + (0j,) * 7
    assert state.num_qubits == 3


def test_zero_rejects_invalid_qubit_count() -> None:
    """Reject a non-positive qubit count for the zero state."""
    with pytest.raises(ValueError, match="num_qubits must be at least 1"):
        InitialState.zero(0)


@pytest.mark.parametrize(
    ("basis_index", "expected"),
    [
        (0, (1 + 0j, 0j, 0j, 0j)),
        (1, (0j, 1 + 0j, 0j, 0j)),
        (2, (0j, 0j, 1 + 0j, 0j)),
        (3, (0j, 0j, 0j, 1 + 0j)),
    ],
)
def test_basis_constructs_computational_basis_state(
    basis_index: int,
    expected: tuple[complex, ...],
) -> None:
    """Construct the requested computational basis state."""
    state = InitialState.basis(2, basis_index)

    assert state.amplitudes == expected
    assert state.num_qubits == 2


def test_basis_rejects_invalid_qubit_count() -> None:
    """Reject a non-positive qubit count for a basis state."""
    with pytest.raises(ValueError, match="num_qubits must be at least 1"):
        InitialState.basis(0, 0)


@pytest.mark.parametrize("basis_index", [-1, 4])
def test_basis_rejects_out_of_range_index(basis_index: int) -> None:
    """Reject a computational basis index outside the statevector."""
    with pytest.raises(ValueError, match="basis_index must reference"):
        InitialState.basis(2, basis_index)


def test_circuit_defaults_to_all_zero_initial_state() -> None:
    """Give a circuit the all-zero state when no initial state is supplied."""
    circuit = Circuit(num_qubits=3)

    assert circuit.initial_state == InitialState.zero(3)


def test_circuit_accepts_matching_initial_state() -> None:
    """Accept an explicit initial state matching the circuit size."""
    state = InitialState.basis(3, 5)
    circuit = Circuit(num_qubits=3, initial_state=state)

    assert circuit.initial_state == state


def test_circuit_rejects_mismatched_initial_state() -> None:
    """Reject an initial state whose qubit count differs from the circuit."""
    with pytest.raises(ValueError, match="initial_state qubit count must match"):
        Circuit(
            num_qubits=3,
            initial_state=InitialState.zero(2),
        )


def test_circuit_preserves_existing_positional_operations_api() -> None:
    """Preserve positional construction of circuit operations."""
    operation = GateOperation(gate="h", targets=(0,))
    circuit = Circuit(2, (operation,))

    assert circuit.operations == (operation,)
    assert circuit.initial_state == InitialState.zero(2)
