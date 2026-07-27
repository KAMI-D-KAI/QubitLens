import pytest

from qubitlens.domain.circuit import GateOperation
from qubitlens.domain.gates import (
    STANDARD_GATES,
    GateDefinition,
    get_gate,
    validate_gate_operation,
)


def test_gate_definition_stores_metadata() -> None:
    gate = GateDefinition(
        name="rx",
        display_name="RX",
        num_targets=1,
        num_parameters=1,
    )

    assert gate.name == "rx"
    assert gate.display_name == "RX"
    assert gate.num_targets == 1
    assert gate.num_controls == 0
    assert gate.num_parameters == 1


@pytest.mark.parametrize("name", ["", "   "])
def test_gate_definition_rejects_empty_name(name: str) -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        GateDefinition(name=name, display_name="X", num_targets=1)


@pytest.mark.parametrize("display_name", ["", "   "])
def test_gate_definition_rejects_empty_display_name(display_name: str) -> None:
    with pytest.raises(ValueError, match="display_name must not be empty"):
        GateDefinition(name="x", display_name=display_name, num_targets=1)


@pytest.mark.parametrize("num_targets", [0, -1])
def test_gate_definition_requires_at_least_one_target(num_targets: int) -> None:
    with pytest.raises(ValueError, match="num_targets must be at least 1"):
        GateDefinition(name="x", display_name="X", num_targets=num_targets)


def test_gate_definition_rejects_negative_control_count() -> None:
    with pytest.raises(ValueError, match="num_controls must be non-negative"):
        GateDefinition(
            name="cx",
            display_name="CX",
            num_targets=1,
            num_controls=-1,
        )


def test_gate_definition_rejects_negative_parameter_count() -> None:
    with pytest.raises(ValueError, match="num_parameters must be non-negative"):
        GateDefinition(
            name="rx",
            display_name="RX",
            num_targets=1,
            num_parameters=-1,
        )


def test_gate_definition_is_immutable() -> None:
    gate = GateDefinition(name="x", display_name="X", num_targets=1)

    with pytest.raises(AttributeError):
        gate.name = "y"


def test_standard_gates_contains_expected_gates() -> None:
    assert tuple(gate.name for gate in STANDARD_GATES) == (
        "i",
        "x",
        "y",
        "z",
        "h",
        "s",
        "sdg",
        "t",
        "tdg",
        "p",
        "cx",
        "cy",
        "cz",
        "ccx",
        "ccz",
        "swap",
        "cswap",
    )


def test_standard_gate_names_are_unique() -> None:
    names = [gate.name for gate in STANDARD_GATES]

    assert len(names) == len(set(names))


def test_phase_gate_metadata() -> None:
    phase = next(gate for gate in STANDARD_GATES if gate.name == "p")

    assert phase.num_targets == 1
    assert phase.num_controls == 0
    assert phase.num_parameters == 1


@pytest.mark.parametrize("name", ["cx", "cy", "cz"])
def test_controlled_single_qubit_gate_metadata(name: str) -> None:
    gate = next(gate for gate in STANDARD_GATES if gate.name == name)

    assert gate.num_targets == 1
    assert gate.num_controls == 1
    assert gate.num_parameters == 0


@pytest.mark.parametrize("name", ["ccx", "ccz"])
def test_doubly_controlled_gate_metadata(name: str) -> None:
    gate = next(gate for gate in STANDARD_GATES if gate.name == name)

    assert gate.num_targets == 1
    assert gate.num_controls == 2
    assert gate.num_parameters == 0


def test_swap_gate_metadata() -> None:
    swap = next(gate for gate in STANDARD_GATES if gate.name == "swap")

    assert swap.num_targets == 2
    assert swap.num_controls == 0
    assert swap.num_parameters == 0


def test_controlled_swap_gate_metadata() -> None:
    cswap = next(gate for gate in STANDARD_GATES if gate.name == "cswap")

    assert cswap.num_targets == 2
    assert cswap.num_controls == 1
    assert cswap.num_parameters == 0


def test_get_gate_returns_supported_gate() -> None:
    gate = get_gate("cx")

    assert gate.name == "cx"
    assert gate.display_name == "CX"
    assert gate.num_targets == 1
    assert gate.num_controls == 1
    assert gate.num_parameters == 0


def test_get_gate_returns_catalogue_definition() -> None:
    gate = get_gate("p")
    catalogue_gate = next(gate for gate in STANDARD_GATES if gate.name == "p")

    assert gate is catalogue_gate


@pytest.mark.parametrize("name", ["CX", " cx ", "banana"])
def test_get_gate_rejects_noncanonical_or_unsupported_name(name: str) -> None:
    with pytest.raises(ValueError, match=f"unsupported gate: {name}"):
        get_gate(name)


@pytest.mark.parametrize(
    "operation",
    [
        GateOperation(gate="h", targets=(0,)),
        GateOperation(gate="p", targets=(0,), parameters=(0.5,)),
        GateOperation(gate="cx", targets=(1,), controls=(0,)),
        GateOperation(gate="ccx", targets=(2,), controls=(0, 1)),
        GateOperation(gate="swap", targets=(0, 1)),
        GateOperation(gate="cswap", targets=(1, 2), controls=(0,)),
    ],
)
def test_validate_gate_operation_accepts_valid_operations(
    operation: GateOperation,
) -> None:
    assert validate_gate_operation(operation) is None


def test_validate_gate_operation_rejects_unsupported_gate() -> None:
    operation = GateOperation(gate="banana", targets=(0,))

    with pytest.raises(ValueError, match="unsupported gate: banana"):
        validate_gate_operation(operation)


def test_validate_gate_operation_rejects_wrong_target_count() -> None:
    operation = GateOperation(gate="h", targets=(0, 1))

    with pytest.raises(
        ValueError,
        match=r"gate h requires 1 target\(s\), but got 2",
    ):
        validate_gate_operation(operation)


def test_validate_gate_operation_rejects_wrong_control_count() -> None:
    operation = GateOperation(gate="cx", targets=(1,))

    with pytest.raises(
        ValueError,
        match=r"gate cx requires 1 control\(s\), but got 0",
    ):
        validate_gate_operation(operation)


def test_validate_gate_operation_rejects_wrong_parameter_count() -> None:
    operation = GateOperation(gate="p", targets=(0,))

    with pytest.raises(
        ValueError,
        match=r"gate p requires 1 parameter\(s\), but got 0",
    ):
        validate_gate_operation(operation)
