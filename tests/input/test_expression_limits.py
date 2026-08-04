import pytest

from qubitlens.input.errors import (
    DisallowedNodeError,
    NonFiniteResultError,
    ResourceLimitError,
)
from qubitlens.input.expression import (
    MAX_ABS_EXPONENT,
    MAX_AST_DEPTH,
    MAX_AST_NODES,
    MAX_EXPRESSION_LENGTH,
    evaluate,
)


def test_expression_length_limit_is_enforced() -> None:
    expression = "1" * (MAX_EXPRESSION_LENGTH + 1)

    with pytest.raises(ResourceLimitError):
        evaluate(expression)


def test_expression_at_length_limit_is_not_rejected_for_length() -> None:
    expression = "1" + " " * (MAX_EXPRESSION_LENGTH - 1)

    assert len(expression) == MAX_EXPRESSION_LENGTH
    assert evaluate(expression) == 1 + 0j


def test_ast_depth_limit_is_enforced() -> None:
    expression = "-" * (MAX_AST_DEPTH + 10) + "1"

    with pytest.raises(ResourceLimitError):
        evaluate(expression)


def test_ast_node_count_limit_is_enforced() -> None:
    expression = "+".join("1" for _ in range(MAX_AST_NODES))

    with pytest.raises(ResourceLimitError):
        evaluate(expression)


def test_large_literal_exponent_is_rejected() -> None:
    expression = f"2 ** {MAX_ABS_EXPONENT + 1}"

    with pytest.raises(ResourceLimitError):
        evaluate(expression)


def test_negative_large_literal_exponent_is_rejected() -> None:
    expression = f"2 ** -{MAX_ABS_EXPONENT + 1}"

    with pytest.raises(ResourceLimitError):
        evaluate(expression)


def test_stacked_exponent_is_rejected() -> None:
    with pytest.raises(ResourceLimitError):
        evaluate("2 ** (3 ** 4)")


@pytest.mark.parametrize(
    "expression",
    [
        "1e309",
        "-1e309",
        "1e309j",
    ],
)
def test_non_finite_results_are_rejected(expression: str) -> None:
    with pytest.raises(NonFiniteResultError):
        evaluate(expression)


def test_function_name_used_as_value() -> None:
    with pytest.raises(DisallowedNodeError):
        evaluate("sin + 1")
