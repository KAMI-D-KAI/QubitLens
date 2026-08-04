"""QubitLens mathematical input subsystem.

Sole boundary between human-typed mathematical text and validated
QubitLens domain values. Contains the safe expression engine,
parameter-variable handling, and scientific state input parsers.
"""

from qubitlens.input.errors import (
    DisallowedNameError,
    DisallowedNodeError,
    ExpressionSyntaxError,
    InputError,
    InvalidParameterNameError,
    NonFiniteResultError,
    ResourceLimitError,
    UnboundParameterError,
)
from qubitlens.input.expression import evaluate
from qubitlens.input.parameters import (
    Bindings,
    Parameter,
    extract_parameters,
    is_valid_parameter_name,
)
from qubitlens.input.state_input import (
    from_basis_dict,
    from_sparse_dict,
    from_vector,
)

__all__ = [
    "Bindings",
    "DisallowedNameError",
    "DisallowedNodeError",
    "ExpressionSyntaxError",
    "InputError",
    "InvalidParameterNameError",
    "NonFiniteResultError",
    "Parameter",
    "ResourceLimitError",
    "UnboundParameterError",
    "evaluate",
    "extract_parameters",
    "from_basis_dict",
    "from_sparse_dict",
    "from_vector",
    "is_valid_parameter_name",
]
