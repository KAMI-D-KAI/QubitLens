"""Resource-limit tests. These prove the engine resists abusive inputs
without depending on wall-clock timing (which is flaky in CI).
"""

import pytest

from qubitlens.input.errors import ResourceLimitError
from qubitlens.input.expression import (
    MAX_ABS_EXPONENT,
    MAX_AST_DEPTH,
    MAX_EXPRESSION_LENGTH,
    evaluate,
)


class TestLength:
    """Test that expression length is enforced against MAX_EXPRESSION_LENGTH."""

    def test_length_at_limit_is_ok(self):
        expr = "1" + " " * (MAX_EXPRESSION_LENGTH - 1)

        assert len(expr) == MAX_EXPRESSION_LENGTH
        assert evaluate(expr) == 1

    def test_length_over_limit_raises(self):
        expr = "1" + " " * MAX_EXPRESSION_LENGTH

        assert len(expr) == MAX_EXPRESSION_LENGTH + 1

        with pytest.raises(ResourceLimitError):
            evaluate(expr)


class TestDepth:
    """Test that expressions exceeding MAX_AST_DEPTH raise ResourceLimitError."""

    def test_depth_over_limit_raises(self):
        expr = "-" * (MAX_AST_DEPTH + 5) + "1"
        with pytest.raises(ResourceLimitError):
            evaluate(expr)


class TestExponent:
    """Test that exponents over MAX_ABS_EXPONENT, including stacked, are rejected."""

    def test_huge_exponent_literal_raises(self):
        with pytest.raises(ResourceLimitError):
            evaluate(f"2**{int(MAX_ABS_EXPONENT) + 1}")

    def test_stacked_exponents_are_capped(self):
        # 2 ** (10 ** 10) would be catastrophic if evaluated.
        with pytest.raises(ResourceLimitError):
            evaluate("2**10**10")
