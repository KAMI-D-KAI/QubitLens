"""Domain models for representing quantum circuits."""

from dataclasses import dataclass

from qubitlens.domain.initial_state import InitialState


@dataclass(frozen=True)
class GateOperation:
    """A gate application within a quantum circuit."""

    gate: str
    targets: tuple[int, ...]
    controls: tuple[int, ...] = ()
    parameters: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        """Validate the gate operation."""
        if not self.gate.strip():
            raise ValueError("gate must not be empty")

        if not self.targets:
            raise ValueError("gate operation must have at least one target")

        if any(t < 0 for t in self.targets):
            raise ValueError("target qubits must be non-negative")

        if any(c < 0 for c in self.controls):
            raise ValueError("control qubits must be non-negative")

        if len(set(self.targets)) != len(self.targets):
            raise ValueError("targets must not contain duplicates")

        if len(set(self.controls)) != len(self.controls):
            raise ValueError("controls must not contain duplicates")

        if set(self.targets) & set(self.controls):
            raise ValueError("target and control qubits must be disjoint")


@dataclass(frozen=True)
class Measurement:
    """A measurement from a qubit into a classical bit."""

    qubit: int
    classical_bit: int

    def __post_init__(self) -> None:
        """Validate the measurement."""
        if self.qubit < 0:
            raise ValueError("qubit must be non-negative")

        if self.classical_bit < 0:
            raise ValueError("classical_bit must be non-negative")


CircuitOperation = GateOperation | Measurement


@dataclass(frozen=True)
class Circuit:
    """A quantum circuit and its ordered operations."""

    num_qubits: int
    operations: tuple[CircuitOperation, ...] = ()
    initial_state: InitialState | None = None

    def __post_init__(self) -> None:
        """Validate the circuit configuration."""
        if self.num_qubits < 1:
            raise ValueError("num_qubits must be at least 1")

        initial_state = self.initial_state

        if initial_state is None:
            initial_state = InitialState.zero(self.num_qubits)
            object.__setattr__(self, "initial_state", initial_state)

        if initial_state.num_qubits != self.num_qubits:
            raise ValueError("initial_state qubit count must match circuit num_qubits")

        for operation in self.operations:
            if isinstance(operation, GateOperation):
                for qubit in operation.targets + operation.controls:
                    if not 0 <= qubit < self.num_qubits:
                        raise ValueError(
                            "operation references a qubit outside the circuit"
                        )

            elif isinstance(operation, Measurement):
                if not 0 <= operation.qubit < self.num_qubits:
                    raise ValueError("operation references a qubit outside the circuit")
