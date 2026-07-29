import pytest

from qubitlens.input.errors import (
    DisallowedNameError,
    DisallowedNodeError,
    ExpressionSyntaxError,
    InputError,
    NonFiniteResultError,
)
from qubitlens.input.expression import evaluate


@pytest.mark.parametrize("expression", ["", "   ", "\t\n"])
def test_empty_expression_is_rejected(expression: str) -> None:
    with pytest.raises(ExpressionSyntaxError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "(",
        "1 +",
        "sin(",
        "1 2",
    ],
)
def test_invalid_python_syntax_is_rejected(expression: str) -> None:
    with pytest.raises(ExpressionSyntaxError):
        evaluate(expression)


@pytest.mark.parametrize("expression", [None, 1, 1.5, True, object()])
def test_non_string_input_is_rejected(expression: object) -> None:
    with pytest.raises(ExpressionSyntaxError):
        evaluate(expression)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "expression",
    [
        "theta",
        "unknown",
        "os",
        "eval",
    ],
)
def test_unknown_names_are_rejected(expression: str) -> None:
    with pytest.raises(DisallowedNameError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "True",
        "False",
        "'hello'",
        "None",
    ],
)
def test_non_numeric_constants_are_rejected(expression: str) -> None:
    with pytest.raises(DisallowedNodeError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "[1, 2]",
        "(1, 2)",
        "{1, 2}",
        "{'x': 1}",
        "1 < 2",
        "1 and 2",
        "lambda: 1",
        "pi.real",
        "pi[0]",
    ],
)
def test_disallowed_language_constructs_are_rejected(expression: str) -> None:
    with pytest.raises(DisallowedNodeError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "unknown(1)",
        "pow(2)",
    ],
)
def test_unknown_functions_are_rejected(expression: str) -> None:
    with pytest.raises(DisallowedNameError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "sin()",
        "sin(1, 2)",
        "sqrt()",
        "conj(1, 2)",
    ],
)
def test_functions_require_exactly_one_argument(expression: str) -> None:
    with pytest.raises(DisallowedNodeError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "sin(x=1)",
        "sqrt(x=4)",
    ],
)
def test_keyword_arguments_are_rejected(expression: str) -> None:
    with pytest.raises(DisallowedNodeError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "cmath.sin(0)",
    ],
)
def test_non_direct_function_calls_are_rejected(expression: str) -> None:
    with pytest.raises((DisallowedNodeError, DisallowedNameError)):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "1 / 0",
        "log(0)",
    ],
)
def test_invalid_numeric_evaluation_uses_input_error(
    expression: str,
) -> None:
    with pytest.raises(NonFiniteResultError):
        evaluate(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "__import__('os').system('echo unsafe')",
        "open('file')",
        "globals()",
        "locals()",
    ],
)
def test_python_execution_paths_are_rejected(expression: str) -> None:
    with pytest.raises(InputError):
        evaluate(expression)
