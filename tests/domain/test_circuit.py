"""Tests for the quantum circuit domain models."""

from dataclasses import FrozenInstanceError

import pytest

from qubitlens.domain import Circuit, GateOperation, Measurement


def test_gate_operation_stores_configuration() -> None:
    operation = GateOperation(
        gate="rx",
        targets=(1,),
        controls=(0,),
        parameters=(0.5,),
    )

    assert operation.gate == "rx"
    assert operation.targets == (1,)
    assert operation.controls == (0,)
    assert operation.parameters == (0.5,)


def test_gate_operation_defaults_optional_fields() -> None:
    operation = GateOperation(gate="x", targets=(0,))

    assert operation.controls == ()
    assert operation.parameters == ()


def test_gate_operation_rejects_empty_gate() -> None:
    with pytest.raises(ValueError, match="gate must not be empty"):
        GateOperation(gate="", targets=(0,))


def test_gate_operation_rejects_whitespace_only_gate() -> None:
    with pytest.raises(ValueError, match="gate must not be empty"):
        GateOperation(gate="   ", targets=(0,))


def test_gate_operation_requires_target() -> None:
    with pytest.raises(
        ValueError,
        match="gate operation must have at least one target",
    ):
        GateOperation(gate="x", targets=())


def test_gate_operation_rejects_negative_target() -> None:
    with pytest.raises(ValueError, match="target qubits must be non-negative"):
        GateOperation(gate="x", targets=(-1,))


def test_gate_operation_rejects_negative_control() -> None:
    with pytest.raises(ValueError, match="control qubits must be non-negative"):
        GateOperation(gate="cx", targets=(1,), controls=(-1,))


def test_gate_operation_rejects_duplicate_targets() -> None:
    with pytest.raises(ValueError, match="targets must not contain duplicates"):
        GateOperation(gate="swap", targets=(0, 0))


def test_gate_operation_rejects_duplicate_controls() -> None:
    with pytest.raises(ValueError, match="controls must not contain duplicates"):
        GateOperation(gate="custom", targets=(2,), controls=(0, 0))


def test_gate_operation_rejects_target_control_overlap() -> None:
    with pytest.raises(
        ValueError,
        match="target and control qubits must be disjoint",
    ):
        GateOperation(gate="cx", targets=(1,), controls=(1,))


def test_measurement_stores_configuration() -> None:
    measurement = Measurement(qubit=2, classical_bit=1)

    assert measurement.qubit == 2
    assert measurement.classical_bit == 1


def test_measurement_rejects_negative_qubit() -> None:
    with pytest.raises(ValueError, match="qubit must be non-negative"):
        Measurement(qubit=-1, classical_bit=0)


def test_measurement_rejects_negative_classical_bit() -> None:
    with pytest.raises(ValueError, match="classical_bit must be non-negative"):
        Measurement(qubit=0, classical_bit=-1)


def test_circuit_allows_no_operations() -> None:
    circuit = Circuit(num_qubits=3)

    assert circuit.num_qubits == 3
    assert circuit.operations == ()


def test_circuit_preserves_ordered_operations() -> None:
    first = GateOperation(gate="h", targets=(0,))
    second = GateOperation(gate="cx", targets=(1,), controls=(0,))
    third = Measurement(qubit=1, classical_bit=0)

    circuit = Circuit(
        num_qubits=2,
        operations=(first, second, third),
    )

    assert circuit.operations == (first, second, third)


def test_circuit_rejects_zero_qubits() -> None:
    with pytest.raises(ValueError, match="num_qubits must be at least 1"):
        Circuit(num_qubits=0)


def test_circuit_rejects_negative_qubits() -> None:
    with pytest.raises(ValueError, match="num_qubits must be at least 1"):
        Circuit(num_qubits=-1)


def test_circuit_rejects_target_outside_circuit() -> None:
    operation = GateOperation(gate="x", targets=(2,))

    with pytest.raises(
        ValueError,
        match="operation references a qubit outside the circuit",
    ):
        Circuit(num_qubits=2, operations=(operation,))


def test_circuit_rejects_control_outside_circuit() -> None:
    operation = GateOperation(gate="cx", targets=(0,), controls=(2,))

    with pytest.raises(
        ValueError,
        match="operation references a qubit outside the circuit",
    ):
        Circuit(num_qubits=2, operations=(operation,))


def test_circuit_rejects_measurement_outside_circuit() -> None:
    measurement = Measurement(qubit=2, classical_bit=0)

    with pytest.raises(
        ValueError,
        match="operation references a qubit outside the circuit",
    ):
        Circuit(num_qubits=2, operations=(measurement,))


def test_gate_operation_is_immutable() -> None:
    operation = GateOperation(gate="x", targets=(0,))

    with pytest.raises(FrozenInstanceError):
        operation.gate = "h"


def test_measurement_is_immutable() -> None:
    measurement = Measurement(qubit=0, classical_bit=0)

    with pytest.raises(FrozenInstanceError):
        measurement.qubit = 1


def test_circuit_is_immutable() -> None:
    circuit = Circuit(num_qubits=2)

    with pytest.raises(FrozenInstanceError):
        circuit.num_qubits = 3
