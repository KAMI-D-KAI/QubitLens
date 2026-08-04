from __future__ import annotations

import pytest

from qubitlens.input.errors import (
    ExpressionSyntaxError,
    InvalidParameterNameError,
)
from qubitlens.input.parameters import (
    Parameter,
    extract_parameters,
    is_valid_parameter_name,
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("theta", True),
        ("phi", True),
        ("alpha_1", True),
        ("pi", False),
        ("e", False),
        ("tau", False),
        ("sin", False),
        ("sqrt", False),
        ("1theta", False),
        ("", False),
    ],
)
def test_is_valid_parameter_name(name: str, expected: bool) -> None:
    assert is_valid_parameter_name(name) is expected


def test_parameter_accepts_valid_name() -> None:
    parameter = Parameter("theta")

    assert parameter.name == "theta"


@pytest.mark.parametrize(
    "name",
    [
        "pi",
        "e",
        "tau",
        "sin",
        "sqrt",
        "",
        "1theta",
    ],
)
def test_parameter_rejects_invalid_name(name: str) -> None:
    with pytest.raises(InvalidParameterNameError):
        Parameter(name)


def test_extract_parameters() -> None:
    assert extract_parameters("theta + phi + sin(alpha)") == frozenset(
        {"theta", "phi", "alpha"}
    )


def test_extract_parameters_empty() -> None:
    assert extract_parameters("sin(pi)") == frozenset()


def test_extract_parameters_invalid_expression() -> None:
    with pytest.raises(ExpressionSyntaxError):
        extract_parameters("(")
