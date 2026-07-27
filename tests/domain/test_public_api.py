from qubitlens.domain import (
    STANDARD_GATES,
    Circuit,
    GateDefinition,
    GateOperation,
    Measurement,
    get_gate,
    validate_gate_operation,
)


def test_domain_public_api_exposes_circuit_models() -> None:
    assert Circuit.__name__ == "Circuit"
    assert GateOperation.__name__ == "GateOperation"
    assert Measurement.__name__ == "Measurement"


def test_domain_public_api_exposes_gate_catalogue() -> None:
    assert GateDefinition.__name__ == "GateDefinition"
    assert len(STANDARD_GATES) == 17
    assert get_gate("h").display_name == "H"


def test_domain_public_api_exposes_gate_validation() -> None:
    operation = GateOperation(gate="h", targets=(0,))

    assert validate_gate_operation(operation) is None
