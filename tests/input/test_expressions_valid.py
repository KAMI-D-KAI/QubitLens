"""Valid-input tests for the safe expression engine.
These lock down the *supported* mathematical surface. Every accepted
capability must have at least one test here so future refactors cannot
silently drop support.
"""

import cmath
import math

from qubitlens.input.expression import evaluate


def _close(a: complex, b: complex, tol: float = 1e-12) -> bool:
    """Return True if a and b are close within tol."""
    return abs(a - b) < tol


class TestNumericLiterals:
    """Test that numeric literals are accepted and parsed correctly."""

    def test_positive_integer(self):
        assert evaluate("42") == 42

    def test_negative_integer(self):
        assert evaluate("-42") == -42

    def test_positive_float(self):
        assert _close(evaluate("3.14"), 3.14)

    def test_negative_float(self):
        assert _close(evaluate("-3.14"), -3.14)

    def test_scientific_notation(self):
        assert _close(evaluate("1e3"), 1000.0)
        assert _close(evaluate("-1e-3"), -0.001)


class TestArithmetic:
    """Test that basic arithmetic operations are accepted and evaluated correctly."""

    def test_add(self):
        assert evaluate("1 + 2") == 3

    def test_sub(self):
        assert evaluate("5 - 3") == 2

    def test_mul(self):
        assert evaluate("4 * 2") == 8

    def test_div(self):
        assert _close(evaluate("8 / 4"), 2.0)

    def test_pow(self):
        assert _close(evaluate("2 ** 3"), 8.0)

    def test_unary_minus(self):
        assert evaluate("-5") == -5

    def test_precedence(self):
        assert evaluate("1 + 2 * 3") == 7
        assert evaluate("( 1 + 2 ) * 3") == 9


class TestConstants:
    """Test that named constants (pi, e, tau, i, j) evaluate correctly."""

    def test_pi(self):
        assert _close(evaluate("pi"), math.pi)

    def test_e(self):
        assert _close(evaluate("e"), math.e)

    def test_tau(self):
        assert _close(evaluate("tau"), math.tau)

    def test_imaginary_i(self):
        assert evaluate("i") == 1j

    def test_imaginary_j(self):
        assert evaluate("j") == 1j


class TestFunctions:
    """Test that whitelisted math functions evaluate correctly."""

    def test_sin(self):
        assert _close(evaluate("sin(0)"), 0)

    def test_cos(self):
        assert _close(evaluate("cos(0)"), 1)

    def test_sqrt(self):
        assert _close(evaluate("sqrt(2)"), math.sqrt(2))

    def test_sqrt_of_negative_is_complex(self):
        assert _close(evaluate("sqrt(-1)"), 1j)

    def test_exp_of_i_pi(self):
        assert _close(evaluate("exp(i*pi)"), -1, tol=1e-12)

    def test_conj(self):
        assert _close(evaluate("conj(1+2*i)"), 1 - 2j)

    def test_abs(self):
        assert _close(evaluate("abs(3+4*i)"), 5)

    def test_real(self):
        assert _close(evaluate("real(2+3*i)"), 2)

    def test_imag(self):
        assert _close(evaluate("imag(2+3*i)"), 3)


class TestComplexExpressions:
    """Test composite expressions combining constants, functions, operators."""

    def test_amplitude_form(self):
        assert _close(evaluate("1/sqrt(2)"), 1 / math.sqrt(2))

    def test_phase_form(self):
        assert _close(evaluate("exp(i*pi/4)"), cmath.exp(1j * math.pi / 4))

    def test_nested_functions(self):
        assert _close(evaluate("sqrt(abs(-4))"), 2)
