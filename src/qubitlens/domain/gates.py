"""Domain models for representing supported quantum gates."""

from dataclasses import dataclass

from qubitlens.domain.circuit import GateOperation


@dataclass(frozen=True)
class GateDefinition:
    """An immutable definition of a supported quantum gate."""

    name: str
    display_name: str
    num_targets: int
    num_controls: int = 0
    num_parameters: int = 0

    def __post_init__(self) -> None:
        """Validate the gate definition."""

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.display_name.strip():
            raise ValueError("display_name must not be empty")

        if self.num_targets < 1:
            raise ValueError("num_targets must be at least 1")

        if self.num_controls < 0:
            raise ValueError("num_controls must be non-negative")

        if self.num_parameters < 0:
            raise ValueError("num_parameters must be non-negative")


STANDARD_GATES: tuple[GateDefinition, ...] = (
    GateDefinition(name="i", display_name="I", num_targets=1),
    GateDefinition(name="x", display_name="X", num_targets=1),
    GateDefinition(name="y", display_name="Y", num_targets=1),
    GateDefinition(name="z", display_name="Z", num_targets=1),
    GateDefinition(name="h", display_name="H", num_targets=1),
    GateDefinition(name="s", display_name="S", num_targets=1),
    GateDefinition(name="sdg", display_name="S†", num_targets=1),
    GateDefinition(name="t", display_name="T", num_targets=1),
    GateDefinition(name="tdg", display_name="T†", num_targets=1),
    GateDefinition(name="p", display_name="P", num_targets=1, num_parameters=1),
    GateDefinition(name="cx", display_name="CX", num_targets=1, num_controls=1),
    GateDefinition(name="cy", display_name="CY", num_targets=1, num_controls=1),
    GateDefinition(name="cz", display_name="CZ", num_targets=1, num_controls=1),
    GateDefinition(name="ccx", display_name="CCX", num_targets=1, num_controls=2),
    GateDefinition(name="ccz", display_name="CCZ", num_targets=1, num_controls=2),
    GateDefinition(name="swap", display_name="SWAP", num_targets=2),
    GateDefinition(name="cswap", display_name="CSWAP", num_targets=2, num_controls=1),
)

_GATE_BY_NAME: dict[str, GateDefinition] = {gate.name: gate for gate in STANDARD_GATES}


def get_gate(name: str) -> GateDefinition:
    """Return the supported gate definition for a canonical name."""
    try:
        return _GATE_BY_NAME[name]
    except KeyError:
        raise ValueError(f"unsupported gate: {name}") from None


def validate_gate_operation(operation: GateOperation) -> None:
    """Validate a gate operation against the supported gate catalogue."""
    definition = get_gate(operation.gate)

    if len(operation.targets) != definition.num_targets:
        raise ValueError(
            f"gate {operation.gate} requires {definition.num_targets} target(s), "
            f"but got {len(operation.targets)}"
        )

    if len(operation.controls) != definition.num_controls:
        raise ValueError(
            f"gate {operation.gate} requires {definition.num_controls} control(s), "
            f"but got {len(operation.controls)}"
        )

    if len(operation.parameters) != definition.num_parameters:
        raise ValueError(
            f"gate {operation.gate} requires {definition.num_parameters} parameter(s), "
            f"but got {len(operation.parameters)}"
        )
