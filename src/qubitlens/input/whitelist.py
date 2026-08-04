"""Expression whitelist.

Defines the allowlist of names, functions, and AST nodes permitted in
QubitLens mathematical expressions.
"""

from __future__ import annotations

import ast
import cmath
import math
from collections.abc import Callable, Mapping

ALLOWED_CONSTANTS: Mapping[str, complex] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "i": 1j,
    "j": 1j,
}


def _safe_log(z: complex) -> complex:
    """Return the natural logarithm of a complex value."""
    return cmath.log(z)


def _absolute(z: complex) -> complex:
    """Return the magnitude of a value."""
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


def _argument(z: complex) -> complex:
    """Return the phase angle of a complex value."""
    return complex(cmath.phase(z))


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
    "arg": _argument,
}


ALLOWED_AST_NODES: frozenset[type[ast.AST]] = frozenset(
    {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Name,
        ast.Call,
        ast.Load,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    }
)
