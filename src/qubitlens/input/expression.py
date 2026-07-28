"""Safe expression engine.

Safely parses and evaluates a restricted math expression string into
a finite complex number, without ever calling eval/exec on raw input.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from typing import Any

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
MAX_ABS_EXPONENT = 1024.0


def evaluate(
    expression: str,
    bindings: Mapping[str, complex] | None = None,
) -> complex:
    """Evaluate a whitelisted mathematical expression and return a complex.
    Raises a subclass of :class:`InputError` on any failure.
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
    _validate_nodes(tree)
    _validate_exponents(tree)

    namespace = _build_namespace(bindings)
    _validate_names(tree, namespace)

    try:
        # We *only* eval an AST that has been fully validated. Not user text.
        code = compile(tree, filename="<qubitlens-expression>", mode="eval")
        raw = eval(code, {"__builtins__": {}}, namespace)

    except (ZeroDivisionError, ValueError, OverflowError) as exc:
        raise NonFiniteResultError(str(exc)) from exc

    result = complex(raw)
    return result


def _parse(expression: str) -> ast.Expression:
    """Parse the expression string into an AST.Expression."""
    try:
        return ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ExpressionSyntaxError(str(exc)) from exc


def _validate_depth(tree: ast.AST) -> None:
    def depth(node: ast.AST) -> int:
        children = list(ast.iter_child_nodes(node))
        return 1 + (max((depth(c) for c in children), default=0))

    if depth(tree) > MAX_AST_DEPTH:
        raise ResourceLimitError(f"AST depth exceeds {MAX_AST_DEPTH}.")


def _validate_nodes(tree: ast.AST) -> None:
    """Validate that all AST nodes are in the whitelist."""
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_AST_NODES:
            raise DisallowedNodeError(f"AST node {type(node).__name__} is not allowed.")


def _validate_names(tree: ast.AST, namespace: Mapping[str, Any]) -> None:
    """Validate that all names in the AST are in the whitelist or bound parameters."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id not in namespace:
                if (
                    node.id.isidentifier()
                    and node.id not in ALLOWED_CONSTANTS
                    and node.id not in ALLOWED_FUNCTIONS
                ):
                    pass
                raise DisallowedNameError(f"name {node.id} is not allowed.")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise DisallowedNodeError("only direct function calls are allowed.")
            if node.func.id not in ALLOWED_FUNCTIONS:
                raise DisallowedNameError(f"function {node.func.id} is not allowed.")


def _validate_exponents(tree: ast.AST) -> None:
    """Validate that all exponent values are within the allowed range."""
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            if isinstance(node.right, ast.Constant) and isinstance(
                node.right.value, (int, float)
            ):
                if abs(node.right.value) > MAX_ABS_EXPONENT:
                    raise ResourceLimitError(
                        f"exponent {node.right.value} exceeds {MAX_ABS_EXPONENT}"
                    )
            elif isinstance(node.right, ast.BinOp) and isinstance(
                node.right.op, ast.Pow
            ):
                raise ResourceLimitError("stacked exponents are not allowed.")


def _build_namespace(bindings: Mapping[str, complex] | None) -> dict[str, Any]:
    """Build the evaluation namespace from the allowed constants and bindings."""
    ns: dict[str, Any] = {}
    ns.update(ALLOWED_CONSTANTS)
    ns.update(ALLOWED_FUNCTIONS)
    if bindings:
        for name, value in bindings.items():
            if name in ALLOWED_CONSTANTS or name in ALLOWED_FUNCTIONS:
                continue
            ns[name] = complex(value)
    return ns
