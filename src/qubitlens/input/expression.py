"""Safe expression engine.

Safely parses and evaluates a restricted math expression string into
a finite complex number, without ever calling eval/exec on raw input.
"""

from __future__ import annotations

import ast
import math

from qubitlens.input.errors import (
    DisallowedNameError,
    DisallowedNodeError,
    ExpressionSyntaxError,
    NonFiniteResultError,
    ResourceLimitError,
)
from qubitlens.input.whitelist import (
    ALLOWED_AST_NODES,
    ALLOWED_CONSTANTS,
    ALLOWED_FUNCTIONS,
)

MAX_EXPRESSION_LENGTH = 512
MAX_AST_DEPTH = 32
MAX_AST_NODES = 128
MAX_ABS_EXPONENT = 1024.0


def evaluate(expression: str) -> complex:
    """Evaluate a restricted mathematical expression as a finite complex value.

    Raises:
        InputError: If the expression is invalid, disallowed, exceeds a resource
            limit, or produces a non-finite result.
    """
    if not isinstance(expression, str):
        raise ExpressionSyntaxError("expression must be a string")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ResourceLimitError(
            f"expression length {len(expression)} exceeds {MAX_EXPRESSION_LENGTH}"
        )
    if expression.strip() == "":
        raise ExpressionSyntaxError("expression must not be empty")

    tree = _parse(expression)
    _validate_depth(tree)
    _validate_node_count(tree)
    _validate_nodes(tree)
    _validate_constants(tree)
    _validate_exponents(tree)
    _validate_names(tree)

    try:
        result = _evaluate_node(tree.body)
    except (ZeroDivisionError, ValueError, OverflowError) as exc:
        raise NonFiniteResultError(str(exc)) from exc

    result = complex(result)
    _validate_finite_result(result)
    return result


def _parse(expression: str) -> ast.Expression:
    """Parse the expression string into an AST.Expression."""
    try:
        return ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ExpressionSyntaxError(str(exc)) from exc


def _evaluate_node(node: ast.AST) -> complex | int | float:
    """Evaluate one validated expression AST node."""
    if isinstance(node, ast.Constant):
        value = node.value

        if isinstance(value, bool) or not isinstance(value, (int, float, complex)):
            raise DisallowedNodeError(
                f"constant type {type(value).__name__} is not allowed."
            )

        return value

    if isinstance(node, ast.Name):
        if node.id in ALLOWED_CONSTANTS:
            return ALLOWED_CONSTANTS[node.id]
        raise DisallowedNameError(f"name {node.id} is not a numeric constant.")

    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)

        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right

        raise DisallowedNodeError(
            f"binary operator {type(node.op).__name__} is not allowed."
        )

    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_node(node.operand)

        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand

        raise DisallowedNodeError(
            f"unary operator {type(node.op).__name__} is not allowed."
        )

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise DisallowedNodeError("only direct function calls are allowed.")

        if node.func.id not in ALLOWED_FUNCTIONS:
            raise DisallowedNameError(f"function {node.func.id} is not allowed.")

        function = ALLOWED_FUNCTIONS[node.func.id]
        arguments = tuple(_evaluate_node(argument) for argument in node.args)

        return complex(function(*arguments))

    raise DisallowedNodeError(f"AST node {type(node).__name__} is not allowed.")


def _validate_depth(tree: ast.AST) -> None:
    def depth(node: ast.AST) -> int:
        children = list(ast.iter_child_nodes(node))
        return 1 + (max((depth(c) for c in children), default=0))

    if depth(tree) > MAX_AST_DEPTH:
        raise ResourceLimitError(f"AST depth exceeds {MAX_AST_DEPTH}.")


def _validate_node_count(tree: ast.AST) -> None:
    """Validate that the AST does not exceed the node-count limit."""
    node_count = sum(1 for _ in ast.walk(tree))

    if node_count > MAX_AST_NODES:
        raise ResourceLimitError(
            f"AST node count {node_count} exceeds {MAX_AST_NODES}."
        )


def _validate_nodes(tree: ast.AST) -> None:
    """Validate that all AST nodes are in the whitelist."""
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_AST_NODES:
            raise DisallowedNodeError(f"AST node {type(node).__name__} is not allowed.")


def _validate_constants(tree: ast.AST) -> None:
    """Validate that literal constants are numeric and not booleans."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(
                node.value, (int, float, complex)
            ):
                raise DisallowedNodeError(
                    f"constant type {type(node.value).__name__} is not allowed."
                )


def _validate_names(tree: ast.AST) -> None:
    """Validate that all names in the AST are in the expression whitelist."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id not in ALLOWED_CONSTANTS and node.id not in ALLOWED_FUNCTIONS:
                raise DisallowedNameError(f"name {node.id} is not allowed.")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise DisallowedNodeError("only direct function calls are allowed.")

            if node.func.id not in ALLOWED_FUNCTIONS:
                raise DisallowedNameError(f"function {node.func.id} is not allowed.")

            if node.keywords:
                raise DisallowedNodeError("keyword arguments are not allowed.")

            if len(node.args) != 1:
                raise DisallowedNodeError(
                    f"function {node.func.id} requires exactly one argument."
                )


def _validate_exponents(tree: ast.AST) -> None:
    """Validate exponent expressions against the resource limits."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Pow):
            continue

        exponent = node.right

        if isinstance(exponent, ast.BinOp) and isinstance(exponent.op, ast.Pow):
            raise ResourceLimitError("stacked exponents are not allowed.")

        if isinstance(exponent, ast.Constant):
            value = exponent.value

        elif (
            isinstance(exponent, ast.UnaryOp)
            and isinstance(exponent.op, (ast.UAdd, ast.USub))
            and isinstance(exponent.operand, ast.Constant)
        ):
            value = exponent.operand.value

        else:
            continue

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ResourceLimitError("exponent must be a finite real number.")

        if not math.isfinite(value):
            raise ResourceLimitError("exponent must be a finite real number.")

        if abs(value) > MAX_ABS_EXPONENT:
            raise ResourceLimitError(f"exponent {value} exceeds {MAX_ABS_EXPONENT}.")


def _validate_finite_result(result: complex) -> None:
    """Validate that an evaluated result has finite components."""
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise NonFiniteResultError("expression result must be finite.")
