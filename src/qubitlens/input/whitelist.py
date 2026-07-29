"""Expression whitelist.

Defines the allowlist of names, functions, operators, and AST nodes
permitted in QubitLens expressions anything not listed here is
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
    """Return the complex natural logarithm of a value."""
    return cmath.log(z)


def _absolute(z: complex) -> complex:
    """Return the absolute magnitude of a value."""
    return complex(abs(z))


def _real(z: complex) -> complex:
    """Return the real component of a value."""
    return complex(z.real)


def _imag(z: complex) -> complex:
    """Return the imaginary component of a value."""
    return complex(z.imag)


def _conjugate(z: complex) -> complex:
    """Return the complex conjugate of a value."""
    return z.conjugate()


ALLOWED_FUNCTIONS: Mapping[str, Callable[..., complex]] = {
    "sin": cmath.sin,
    "cos": cmath.cos,
    "tan": cmath.tan,
    "exp": cmath.exp,
    "log": _safe_log,
    "sqrt": cmath.sqrt,
    "abs": _absolute,
    "real": _real,
    "imag": _imag,
    "conj": _conjugate,
    "arg": cmath.phase,
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
