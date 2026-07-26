"""Integration tests comparing QubitLens operator ordering with Qiskit."""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qubitlens.core.gates import H, X
from qubitlens.core.operators import build_single_qubit_operator


def test_x_on_q0_matches_qiskit() -> None:
    """QubitLens and Qiskit should agree when X targets q0."""
    initial = np.array([1, 0, 0, 0], dtype=np.complex128)

    operator = build_single_qubit_operator(
        X,
        target=0,
        num_qubits=2,
    )
    qubitlens_state = operator @ initial

    circuit = QuantumCircuit(2)
    circuit.x(0)

    qiskit_state = Statevector.from_instruction(circuit)

    assert np.allclose(qubitlens_state, qiskit_state.data)


def test_x_on_q1_matches_qiskit() -> None:
    """QubitLens and Qiskit should agree when X targets q1."""
    initial = np.array([1, 0, 0, 0], dtype=np.complex128)

    operator = build_single_qubit_operator(
        X,
        target=1,
        num_qubits=2,
    )
    qubitlens_state = operator @ initial

    circuit = QuantumCircuit(2)
    circuit.x(1)

    qiskit_state = Statevector.from_instruction(circuit)

    assert np.allclose(qubitlens_state, qiskit_state.data)


def test_h_on_q0_matches_qiskit() -> None:
    """QubitLens and Qiskit should agree when H targets q0."""
    initial = np.array([1, 0, 0, 0], dtype=np.complex128)

    operator = build_single_qubit_operator(
        H,
        target=0,
        num_qubits=2,
    )
    qubitlens_state = operator @ initial

    circuit = QuantumCircuit(2)
    circuit.h(0)

    qiskit_state = Statevector.from_instruction(circuit)

    assert np.allclose(qubitlens_state, qiskit_state.data)


def test_h_on_q1_matches_qiskit() -> None:
    """QubitLens and Qiskit should agree when H targets q1."""
    initial = np.array([1, 0, 0, 0], dtype=np.complex128)

    operator = build_single_qubit_operator(
        H,
        target=1,
        num_qubits=2,
    )
    qubitlens_state = operator @ initial

    circuit = QuantumCircuit(2)
    circuit.h(1)

    qiskit_state = Statevector.from_instruction(circuit)

    assert np.allclose(qubitlens_state, qiskit_state.data)


def test_three_qubit_target_ordering_matches_qiskit() -> None:
    """QubitLens and Qiskit should agree for an interior qubit."""
    initial = np.zeros(8, dtype=np.complex128)
    initial[0] = 1

    operator = build_single_qubit_operator(
        X,
        target=1,
        num_qubits=3,
    )
    qubitlens_state = operator @ initial

    circuit = QuantumCircuit(3)
    circuit.x(1)

    qiskit_state = Statevector.from_instruction(circuit)

    assert np.allclose(qubitlens_state, qiskit_state.data)