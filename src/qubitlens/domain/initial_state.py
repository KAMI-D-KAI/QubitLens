"""Domain model for representing a quantum circuit's initial state."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class InitialState:
    """An immutable pure statevector used as a quantum circuit's initial state."""

    amplitudes: tuple[complex, ...]

    def __post_init__(self) -> None:
        """Validate the initial state."""
        if len(self.amplitudes) < 2:
            raise ValueError("amplitudes must contain at least two values")

        if len(self.amplitudes) & (len(self.amplitudes) - 1):
            raise ValueError("amplitudes length must be a power of two")

        if any(
            not math.isfinite(amplitude.real) or not math.isfinite(amplitude.imag)
            for amplitude in self.amplitudes
        ):
            raise ValueError("amplitudes must contain only finite values")

        norm_squared = sum(abs(amplitude) ** 2 for amplitude in self.amplitudes)

        if not math.isclose(norm_squared, 1.0):
            raise ValueError("amplitudes must be normalized to unit length")

    @property
    def num_qubits(self) -> int:
        """Return the number of qubits represented by the statevector."""
        return len(self.amplitudes).bit_length() - 1

    @classmethod
    def zero(cls, num_qubits: int) -> "InitialState":
        """Return the all-zero computational basis state."""

        return cls.basis(num_qubits=num_qubits, basis_index=0)

    @classmethod
    def basis(cls, num_qubits: int, basis_index: int) -> "InitialState":
        """Return a computational basis state for the given basis index."""
        if num_qubits < 1:
            raise ValueError("num_qubits must be at least 1")

        if not 0 <= basis_index < (1 << num_qubits):
            raise ValueError(
                "basis_index must reference a valid computational basis state"
            )

        amplitudes = tuple(
            1 + 0j if i == basis_index else 0j for i in range(1 << num_qubits)
        )
        return cls(amplitudes=amplitudes)
