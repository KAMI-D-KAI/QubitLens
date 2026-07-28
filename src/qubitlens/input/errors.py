"""Input-subsystem exception hierarchy.

Defines the InputError hierarchy so all input-subsystem failures can
be caught with a single except clause.
"""

from __future__ import annotations


class InputError(Exception):
    """Base class for all input-subsystem failures."""


class ExpressionSyntaxError(InputError):
    """The expression string is not syntactically valid."""


class DisallowedNameError(InputError):
    """An identifier is not in the whitelist and is not a bound parameter."""


class DisallowedNodeError(InputError):
    """An AST node type is not in the whitelist."""


class ResourceLimitError(InputError):
    """A resource limit (length, depth, exponent size) was exceeded."""


class NonFiniteResultError(InputError):
    """Evaluation produced NaN or infinity."""
