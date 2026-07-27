"""Quantum state representation used by QubitLens."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

ComplexVector = NDArray[np.complex128]


@dataclass(frozen=True)
class QuantumState:
    """Immutable representation of a pure quantum statevector."""

    amplitudes: ComplexVector

    def __post_init__(self) -> None:
        """Validate and normalize the stored representation."""
        amplitudes = np.asarray(self.amplitudes, dtype=np.complex128)

        if amplitudes.ndim != 1:
            raise ValueError("Statevector must be one-dimensional.")

        dimension = amplitudes.size

        if dimension == 0 or dimension & (dimension - 1):
            raise ValueError("Statevector length must be a non-zero power of two.")

        norm = np.linalg.norm(amplitudes)

        if not np.isclose(norm, 1.0):
            raise ValueError("Statevector must be normalized.")

        object.__setattr__(self, "amplitudes", amplitudes.copy())

    @property
    def num_qubits(self) -> int:
        """Return the number of qubits represented by the state."""
        return self.amplitudes.size.bit_length() - 1

    @property
    def probabilities(self) -> NDArray[np.float64]:
        """Return computational-basis measurement probabilities."""
        return np.abs(self.amplitudes) ** 2

    def probability(self, basis_index: int) -> float:
        """Return the probability of a computational-basis outcome."""
        if not 0 <= basis_index < self.amplitudes.size:
            raise IndexError("Basis index is outside the statevector.")

        return float(self.probabilities[basis_index])
