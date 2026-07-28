"""Invalid-input tests. These lock down the *rejected* surface: any
input listed here must raise a subclass of ``InputError``. This is how
the engine's security posture is enforced.
"""

import pytest

from qubitlens.input.errors import (
    DisallowedNameError,
    DisallowedNodeError,
    ExpressionSyntaxError,
    InputError,
    NonFiniteResultError,
)
from qubitlens.input.expression import evaluate


class TestSyntaxErrors:
    """Test that malformed expression strings raise ExpressionSyntaxError."""

    @pytest.mark.parametrize("expr", ["", " ", "1 +", "(1+2", "1**", "1 2", "@"])
    def test_syntax_errors_raise(self, expr):
        with pytest.raises(ExpressionSyntaxError):
            evaluate(expr)


class TestDisallowedNames:
    """Test that whitelist-excluded names (builtins, modules, dunders) are rejected."""

    @pytest.mark.parametrize(
        "expr",
        [
            "__import__('os')",
            "open('x')",
            "eval('1')",
            "exec('1')",
            "os",
            "sys",
            "print(1)",
            "help",
        ],
    )
    def test_disallowed_names_raise(self, expr):
        with pytest.raises(
            (DisallowedNameError, DisallowedNodeError, ExpressionSyntaxError)
        ):
            evaluate(expr)


class TestDisallowedNodes:
    """Test that non-whitelisted AST nodes (subscripts, lambdas, etc.) are rejected."""

    @pytest.mark.parametrize(
        "expr",
        [
            "(1).bit_length()",
            "a[0]",
            "lambda x: x",
            "[x for x in [1]]",
            "1 if True else 0",
            "1 < 2",
            "True and False",
            "f'{1}'",
            "1, 2",
        ],
    )
    def test_disallowed_nodes_raise(self, expr):
        with pytest.raises(
            (DisallowedNodeError, DisallowedNameError, ExpressionSyntaxError)
        ):
            evaluate(expr)


class TestFunctionCallShape:
    """Test that calling a non-function name (constant, unknown) is rejected."""

    def test_calling_a_constant_is_rejected(self):
        with pytest.raises(InputError):
            evaluate("pi(1)")

    def test_calling_unknown_function(self):
        with pytest.raises(InputError):
            evaluate("foo(1)")


class TestNonFinite:
    """Test that div-by-zero and log(0) raise NonFiniteResultError."""

    def test_division_by_zero(self):
        with pytest.raises(NonFiniteResultError):
            evaluate("1/0")

    def test_log_of_zero(self):
        with pytest.raises(NonFiniteResultError):
            evaluate("log(0)")
