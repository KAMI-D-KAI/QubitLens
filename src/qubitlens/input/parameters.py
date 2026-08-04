"""Named parameter variables for QubitLens expressions."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass

from qubitlens.input.errors import (
    ExpressionSyntaxError,
    InvalidParameterNameError,
)
from qubitlens.input.whitelist import (
    ALLOWED_CONSTANTS,
    ALLOWED_FUNCTIONS,
)

Bindings = Mapping[str, complex]


def is_valid_parameter_name(name: str) -> bool:
    """Return True iff *name* is a valid parameter identifier."""
    if not isinstance(name, str) or not name.isidentifier():
        return False

    if name in ALLOWED_CONSTANTS or name in ALLOWED_FUNCTIONS:
        return False

    return True


@dataclass(frozen=True, slots=True)
class Parameter:
    """Symbolic placeholder for a value supplied at evaluation time."""

    name: str

    def __post_init__(self) -> None:
        if not is_valid_parameter_name(self.name):
            raise InvalidParameterNameError(
                f"{self.name!r} is not a valid parameter name."
            )


def extract_parameters(expression: str) -> frozenset[str]:
    """Return parameter names referenced in an expression."""

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ExpressionSyntaxError(str(exc)) from exc

    called: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called.add(node.func.id)

    names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            name = node.id

            if name in ALLOWED_CONSTANTS or name in ALLOWED_FUNCTIONS:
                continue

            if name in called:
                continue

            names.add(name)

    return frozenset(names)
