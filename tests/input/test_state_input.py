from __future__ import annotations

import pytest

from qubitlens.input.errors import InputError, UnboundParameterError
from qubitlens.input.state_input import (
    from_basis_dict,
    from_sparse_dict,
    from_vector,
)


def test_from_vector() -> None:
    state = from_vector(["1", "0"], 1)

    assert state.num_qubits == 1


def test_from_vector_with_bindings() -> None:
    state = from_vector(
        ["theta", "0"],
        1,
        {"theta": 1},
    )

    assert state.num_qubits == 1


def test_from_vector_unbound_parameter() -> None:
    with pytest.raises(UnboundParameterError):
        from_vector(["theta", "0"], 1)


def test_from_vector_wrong_length() -> None:
    with pytest.raises(InputError):
        from_vector(["1"], 2)


def test_from_basis_dict() -> None:
    state = from_basis_dict(
        {
            "0": "1",
            "1": "0",
        },
        1,
    )

    assert state.num_qubits == 1


def test_from_basis_dict_invalid_bitstring() -> None:
    with pytest.raises(InputError):
        from_basis_dict({"2": "1"}, 1)


def test_from_sparse_dict() -> None:
    state = from_sparse_dict(
        {
            0: "1",
            1: "0",
        },
        1,
    )

    assert state.num_qubits == 1


def test_from_sparse_dict_invalid_index() -> None:
    with pytest.raises(InputError):
        from_sparse_dict({2: "1"}, 1)


def test_from_sparse_dict_negative_index() -> None:
    with pytest.raises(InputError):
        from_sparse_dict({-1: "1"}, 1)
