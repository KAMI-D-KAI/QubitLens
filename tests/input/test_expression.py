import cmath
import math

import pytest

from qubitlens.input.errors import (
    InvalidParameterNameError,
)
from qubitlens.input.expression import evaluate
from qubitlens.input.parameters import (
    Parameter,
    extract_parameters,
)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("0", 0j),
        ("42", 42 + 0j),
        ("-3.5", -3.5 + 0j),
        ("2j", 2j),
        ("1 + 2j", 1 + 2j),
        ("1 + 2 * 3", 7 + 0j),
        ("(1 + 2) * 3", 9 + 0j),
        ("2 ** 3", 8 + 0j),
        ("+5", 5 + 0j),
        ("-5", -5 + 0j),
    ],
)
def test_evaluate_arithmetic(expression: str, expected: complex) -> None:
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("pi", complex(math.pi)),
        ("e", complex(math.e)),
        ("tau", complex(math.tau)),
        ("i", 1j),
        ("j", 1j),
    ],
)
def test_evaluate_allowed_constants(expression: str, expected: complex) -> None:
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sin(0)", 0j),
        ("cos(0)", 1 + 0j),
        ("tan(0)", 0j),
        ("exp(0)", 1 + 0j),
        ("log(1)", 0j),
        ("sqrt(4)", 2 + 0j),
        ("abs(3 + 4j)", 5 + 0j),
        ("real(3 + 4j)", 3 + 0j),
        ("imag(3 + 4j)", 4 + 0j),
        ("conj(3 + 4j)", 3 - 4j),
        ("arg(1j)", complex(math.pi / 2)),
    ],
)
def test_evaluate_allowed_functions(expression: str, expected: complex) -> None:
    assert evaluate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sin(pi / 2)", 1 + 0j),
        ("sqrt(-1)", 1j),
        ("exp(i * pi)", -1 + 0j),
        ("conj(exp(i * pi / 4))", cmath.exp(-1j * math.pi / 4)),
        ("sqrt(2) / 2", complex(math.sqrt(2) / 2)),
    ],
)
def test_evaluate_nested_scientific_expressions(
    expression: str,
    expected: complex,
) -> None:
    assert evaluate(expression) == pytest.approx(expected)


def test_evaluate_always_returns_complex() -> None:
    result = evaluate("abs(3 + 4j)")

    assert isinstance(result, complex)
    assert result == 5 + 0j


def test_parameter_binding() -> None:
    assert evaluate("theta + 1", {"theta": 2}) == pytest.approx(3 + 0j)


def test_multiple_parameter_bindings() -> None:
    assert evaluate(
        "theta + phi",
        {"theta": 2, "phi": 3},
    ) == pytest.approx(5 + 0j)


def test_extract_parameters() -> None:
    assert extract_parameters("theta + phi + sin(alpha)") == frozenset(
        {"theta", "phi", "alpha"}
    )


@pytest.mark.parametrize(
    "name",
    ["pi", "e", "tau", "sin", "sqrt"],
)
def test_invalid_parameter_names(name: str) -> None:
    with pytest.raises(InvalidParameterNameError):
        Parameter(name)


def test_valid_parameter() -> None:
    assert Parameter("theta").name == "theta"
