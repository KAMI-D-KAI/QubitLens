"""Expression whitelist.

Defines the allowlist of names, functions, operators, and AST nodes
permitted in QubitLens expressions — anything not listed here is
rejected.
"""

from __future__ import annotations

import ast
import cmath
from collections.abc import Callable, Mapping

ALLOWED_CONSTANTS: Mapping[str, complex] = {
    "pi": cmath.pi,
    "e": cmath.e,
    "tau": cmath.tau,
    "i": 1j,
    "j": 1j,
}


def _safe_log(z: complex) -> complex:
    """Build the evaluation namespace from the allowed constants and bindings."""
    return cmath.log(z)


ALLOWED_FUNCTIONS: Mapping[str, Callable[..., complex]] = {
    "sin": cmath.sin,
    "cos": cmath.cos,
    "tan": cmath.tan,
    "exp": cmath.exp,
    "log": _safe_log,
    "sqrt": cmath.sqrt,
    "abs": lambda z: abs(z),
    "real": lambda z: complex(z).real,
    "imag": lambda z: complex(z).imag,
    "conj": lambda z: complex(z).conjugate(),
    "arg": cmath.phase,
    "pow": lambda x, y: x**y,
}

ALLOWED_AST_NODES: frozenset[type[ast.AST]] = frozenset(
    {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
    }
)
