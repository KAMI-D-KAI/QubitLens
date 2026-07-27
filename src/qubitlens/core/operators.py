"""Operator construction utilities used by QubitLens."""

import numpy as np
from numpy.typing import NDArray

ComplexMatrix = NDArray[np.complex128]


def build_single_qubit_operator(
    gate: ComplexMatrix,
    target: int,
    num_qubits: int,
) -> ComplexMatrix:
    """Embed a single-qubit gate into an n-qubit operator.

    Qubit indices follow Qiskit's little-endian convention, where qubit 0
    corresponds to the least-significant bit of a computational-basis index.
    """
    gate = np.asarray(gate, dtype=np.complex128)

    if gate.shape != (2, 2):
        raise ValueError("Single-qubit gate must have shape (2, 2).")

    if num_qubits < 1:
        raise ValueError("Number of qubits must be at least one.")

    if not 0 <= target < num_qubits:
        raise ValueError("Target qubit is outside the register.")

    factors: list[ComplexMatrix] = []

    for qubit in reversed(range(num_qubits)):
        if qubit == target:
            factors.append(gate)
        else:
            factors.append(np.eye(2, dtype=np.complex128))

    operator = factors[0]

    for factor in factors[1:]:
        operator = np.asarray(
            np.kron(operator, factor),
            dtype=np.complex128,
        )

    return operator
