# QubitLens  Public Python API Reference

*Reference for the intended public interface of the `qubitlens` package. Internal helpers (any name starting with `_`) are documented only in their source docstrings and are not covered here.*

**Scope of this document:** everything shipped through the completion of the Safe Expression Engine. Subsequent capabilities (parameter variables, scientific state input, execution, tracing, explanation, analysis, export, animation) will be added to this file as they land.

**Conventions used throughout:**

- Qubit ordering is **little-endian**: qubit 0 is the least-significant bit of a computational-basis index. On two qubits, the basis-state index `1` corresponds to `|01⟩` where qubit 0 is `|1⟩` and qubit 1 is `|0⟩`.
- Statevectors are `numpy.ndarray` of dtype `complex128`, length `2**num_qubits`, ℓ²-normalised.
- All domain objects are immutable frozen dataclasses; instances cannot be mutated after construction.
- Exceptions raised by user-facing constructors and functions are documented explicitly per entry.

---

## `qubitlens.core`

Low-level numerical primitives. Users rarely import from here directly, but they are the foundation everything else uses.

### `qubitlens.core.gates`

Immutable single- and two-qubit gate matrices as `numpy.ndarray` of dtype `complex128`.

| Name | Shape | Description |
|---|---|---|
| `I` | `(2, 2)` | Identity |
| `H` | `(2, 2)` | Hadamard |
| `X`, `Y`, `Z` | `(2, 2)` | Pauli gates |
| `S`, `T` | `(2, 2)` | π/2 and π/4 phase gates |
| `CX` | `(4, 4)` | Controlled-NOT with control = qubit 0, target = qubit 1 in little-endian |
| `CZ` | `(4, 4)` | Controlled-Z |
| `SWAP` | `(4, 4)` | Swap gate |

**Example**

```python
from qubitlens.core.gates import H
import numpy as np

state = H @ np.array([1, 0], dtype=complex)
```

### `qubitlens.core.state.PureState`

Immutable wrapper around a normalised complex amplitude vector.

**Constructor**

```
PureState(amplitudes: numpy.ndarray)
```

- **`amplitudes`**   1-D complex array of length `2**num_qubits`. Must be finite and ℓ²-normalised.

**Raises**

- `ValueError`   length is not a power of two, contains `NaN`/`inf`, or is not normalised within numerical tolerance.

**Properties**

- **`amplitudes`**   the underlying `numpy.ndarray` (read-only view).
- **`num_qubits`**   `int`, inferred from the length of `amplitudes`.
- **`probabilities`**   `numpy.ndarray` of `float`, the per-basis-state probabilities.

**Example**

```python
import numpy as np
from qubitlens.core.state import PureState

state = PureState(np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2))
assert state.num_qubits == 2
```

### `qubitlens.core.operators.embed_single_qubit`

Lift a `2 × 2` single-qubit unitary into the full `2ⁿ × 2ⁿ` operator that acts on qubit `q` of an `n`-qubit system with **explicit little-endian ordering**.

```
embed_single_qubit(gate: numpy.ndarray, qubit: int, num_qubits: int) -> numpy.ndarray
```

- **`gate`**   a `(2, 2)` complex array.
- **`qubit`**   target qubit index in `[0, num_qubits)`.
- **`num_qubits`**   total qubit count.

**Returns**   a `(2**num_qubits, 2**num_qubits)` complex array.

**Raises**   `ValueError` if `gate` is not `(2, 2)`, if `qubit` is out of range, or if `num_qubits` is not a positive integer.

---

## `qubitlens.domain`

Semantic QubitLens objects. Everything downstream (execution, trace, explanation, visualisation) consumes these   never raw numpy.

### `qubitlens.domain.Circuit`

Immutable, ordered collection of operations over a fixed number of qubits.

**Constructor**

```
Circuit(num_qubits: int)
```

- **`num_qubits`**   total number of qubits, `1 ≤ num_qubits ≤ 10`.

**Raises**   `ValueError` if `num_qubits` is outside the allowed range.

**Properties**

- **`num_qubits`**   `int`, the qubit count.
- **`operations`**   `tuple[Operation, ...]`, ordered operations applied to the circuit.

**Methods**

```
append_gate(
    name: str,
    *,
    targets: tuple[int, ...] = (),
    controls: tuple[int, ...] = (),
    parameters: tuple[str, ...] = (),
) -> Circuit
```

Returns a **new** `Circuit` with the operation appended. The receiver is not mutated.

- **`name`**   must be a key in `qubitlens.domain.gates.CATALOGUE`.
- **`targets` / `controls`**   qubit indices in `[0, num_qubits)`. Must have the arity declared by the catalogue entry for `name`.
- **`parameters`**   string expressions (validated later by the execution layer against the parameter count declared in the catalogue).

**Raises**

- `ValueError`   unknown gate name, target/control arity mismatch, out-of-range qubit index, target/control overlap, wrong parameter count.

**Example**

```python
from qubitlens.domain.circuit import Circuit

bell = (
    Circuit(num_qubits=2)
    .append_gate("h", targets=(0,))
    .append_gate("cx", controls=(0,), targets=(1,))
)
```

### `qubitlens.domain.Operation`

Immutable record describing a single gate application inside a `Circuit`.

**Fields**

- **`gate_name`**   `str`, catalogue key.
- **`targets`**   `tuple[int, ...]`.
- **`controls`**   `tuple[int, ...]`.
- **`parameters`**   `tuple[str, ...]`.

Users generally do not construct `Operation` directly; use `Circuit.append_gate(...)`.

### `qubitlens.domain.Measurement`

Reserved measurement record. Currently a placeholder for the Measurement Laboratory milestone; a future release will document its full interface here.

### `qubitlens.domain.gates`

The gate catalogue.

#### `qubitlens.domain.gates.GateDefinition`

Immutable metadata about a supported gate.

**Fields**

- **`name`**   canonical, lowercase catalogue key (e.g. `"h"`, `"cx"`, `"rx"`).
- **`display_name`**   human-readable name (e.g. `"Hadamard"`, `"CNOT"`).
- **`num_targets`**, **`num_controls`**, **`num_parameters`**   arity declarations.

#### `qubitlens.domain.gates.CATALOGUE`

`Mapping[str, GateDefinition]`. The read-only lookup table used for every operation-validation step.

**Example**

```python
from qubitlens.domain.gates import CATALOGUE

assert "h" in CATALOGUE
assert CATALOGUE["cx"].num_controls == 1
```

### `qubitlens.domain.initial_state.InitialState`

Immutable pure initial state used as the starting point of a `Circuit`.

**Constructor**

```
InitialState(amplitudes: numpy.ndarray)
```

- **`amplitudes`**   complex 1-D array of length `2**num_qubits`. Must be finite and ℓ²-normalised.

**Raises**   `ValueError` if length is not a power of two, or the vector is not finite/normalised.

**Class methods**

```
InitialState.zero(num_qubits: int) -> InitialState
```

Convenience constructor for the canonical `|0…0⟩` state on `num_qubits` qubits.

**Properties**

- **`amplitudes`**   the underlying `numpy.ndarray` (read-only view).
- **`num_qubits`**   inferred from the amplitude vector.

**Example**

```python
import numpy as np
from qubitlens.domain.initial_state import InitialState

zero_two = InitialState.zero(2)  # |00⟩
bell = InitialState(
    np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
)  # (|00⟩ + |11⟩)/√2
```

---

## `qubitlens.input`

The sole boundary between human-typed mathematical text and validated QubitLens values. All parsing and evaluation of user-written mathematics happens here, and nowhere else in the codebase.

### `qubitlens.input.evaluate`

Safely evaluate a restricted real/complex mathematical expression.

```
evaluate(expression: str) -> complex
```

- **`expression`**   a string in the QubitLens expression mini-language (see the surface summary below).

**Returns**   a `complex` result.

**Raises**

- `ExpressionSyntaxError`   the string is not syntactically valid, is empty, or is not a string.
- `DisallowedNameError`   the expression references a name that is neither a whitelisted constant nor a whitelisted function.
- `DisallowedNodeError`   the expression uses an AST construct not on the whitelist (e.g. attribute access, subscript, lambda, comprehension, conditional expression, comparison, boolean operator, formatted string, tuple).
- `ResourceLimitError`  the expression exceeds a length, AST-depth, AST-node-count, or exponent-magnitude limit.
- `NonFiniteResultError`   evaluation produced `NaN` or an infinity (e.g. `1/0`, `log(0)`).

All of the above inherit from `InputError`, so callers who only need coarse-grained handling can write `except InputError`.

**Supported constants**

| Symbol | Value |
|---|---|
| `pi` | `math.pi` |
| `e` | `math.e` |
| `tau` | `math.tau` |
| `i`, `j` | `1j` |

**Supported functions**

`sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`, `conj`, `real`, `imag`, `arg`.

**Supported operators**

`+`, `-`, `*`, `/`, `**`, unary `+` and `-`, and parentheses for grouping.

**Resource limits**

- Maximum expression length: `MAX_EXPRESSION_LENGTH` (default `512` characters).
- Maximum AST depth: `MAX_AST_DEPTH` (default `32`).
- Maximum AST node count: `MAX_AST_NODES` (default `128`).
- Maximum exponent magnitude for numeric-literal exponents: `MAX_ABS_EXPONENT` (default `1024`). Stacked exponents (`a ** b ** c`) are refused outright.

**Examples**

```python
from qubitlens.input import evaluate

evaluate("1/sqrt(2)")  # 0.7071067811865476+0j
evaluate("exp(i*pi)")  # ~ -1+0j
evaluate("cos(pi/4) + i*sin(pi/4)")

# Every rejection is a specific subclass:
from qubitlens.input.errors import DisallowedNameError, ResourceLimitError

try:
    evaluate("__import__('os')")
except DisallowedNameError:
    ...

try:
    evaluate("2**10**10")
except ResourceLimitError:
    ...
```

### `qubitlens.input.errors`

Public exception hierarchy for the input subsystem. All members inherit from `InputError`.

| Class | Raised when |
|---|---|
| `InputError` | Base class for every failure in `qubitlens.input`. Catch this for generic handling. |
| `ExpressionSyntaxError` | The expression is not syntactically valid Python-compatible mathematics, is empty, or is not a string. |
| `DisallowedNameError` | An identifier is neither a whitelisted constant nor a whitelisted function. |
| `DisallowedNodeError` | An AST construct outside the whitelist appears in the expression. |
| `ResourceLimitError` | An expression length, AST depth, AST node-count, or exponent-magnitude limit was exceeded. |
| `NonFiniteResultError` | Evaluation produced a `NaN` or infinity. |

All exceptions can be caught individually for precise error messages, or collectively via `InputError` for coarse handling.

---

## Input package exports

The Safe Expression Engine is available through the `qubitlens.input` package:

```python
from qubitlens.input import InputError, evaluate
```

Additional public input capabilities will be exposed here as parameter variables and scientific state input land.
