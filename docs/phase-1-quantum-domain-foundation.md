# QubitLens Phase 1: Quantum Domain Foundation

**Author:** Vedank Srivastava
**Status:** Complete

## Objective

Phase 0 established the engineering, architectural, and mathematical foundation that QubitLens needs to grow reliably. Phase 1 builds on that foundation by introducing the project's own quantum-domain representations: the structures QubitLens can use to describe circuits, gates, and initial quantum states independently of how those objects are eventually executed, analyzed, explained, or visualized.

The goal is not to turn QubitLens into a separate quantum execution engine. Qiskit remains responsible for quantum execution and continues to provide an external reference for integration behavior. The domain layer instead gives QubitLens a representation designed around its own needs, so later analysis and explanation code can reason about quantum circuits without depending directly on Qiskit's internal object model.

Phase 1 is divided into three parts:

* **1.1 Circuit Domain Model** establishes the representation of circuits, gate applications, and measurements.
* **1.2 Gate Catalogue** defines the supported gates and the metadata needed to describe their structural requirements.
* **1.3 Initial-State Model** establishes how configurable initial quantum states are represented and associated with circuits before execution begins.

Together, these components form the quantum-domain vocabulary that later QubitLens features can build on.

## 1.1 Circuit Domain Model

### Goal

Before Phase 1.1, QubitLens had mathematical primitives for gates, quantum states, and multi-qubit operators, but it did not have its own representation of a quantum circuit.

The goal of 1.1 was to introduce that representation without mixing circuit structure with execution behavior. A QubitLens circuit now describes how many qubits it contains and which operations occur, in order, while individual operations describe their placement and configuration.

The resulting domain model consists of three public objects:

* `GateOperation` represents a gate application within a circuit.
* `Measurement` represents the measurement of a qubit into a classical bit.
* `Circuit` represents a quantum circuit and its ordered operations.

A `CircuitOperation` union type is used internally to express that a circuit operation can be either a gate application or a measurement.

### Gate Operations

`GateOperation` represents a particular use of a gate inside a circuit.

It stores:

* a gate identifier
* one or more target-qubit indices
* zero or more control-qubit indices
* zero or more numerical parameters

The distinction between a gate and a gate operation is important. A gate describes a quantum operation in general, while a gate operation describes where and how that gate is used in a particular circuit.

For example, the concept of a controlled-X gate and its requirements belong to the gate catalogue introduced in Phase 1.2. An application of that gate with qubit 0 as a control and qubit 1 as a target belongs to the circuit domain model.

This keeps Phase 1.1 independent of gate-specific knowledge. The circuit model can represent gate placement without deciding how many targets, controls, or parameters a particular named gate requires.

### Measurements

Measurements are represented separately from gate operations.

A `Measurement` stores:

* the qubit being measured
* the classical bit receiving the measurement result

I kept measurement separate rather than representing it as a gate with a special name such as `"measure"`.

Measurement is not simply another unitary gate application, and it introduces a classical destination that ordinary gate operations do not have. Representing it explicitly also means later code can distinguish measurements through the type system instead of inspecting special gate-name strings.

### Circuits and Operation Ordering

`Circuit` stores:

* the number of qubits in the circuit
* an ordered collection of circuit operations

Operation ordering is part of the domain model because quantum circuits are sequential structures. Two circuits containing the same operations in different orders can produce different quantum behavior.

The operations are therefore stored as a tuple, preserving their order while preventing the collection from being modified after the circuit has been constructed.

A circuit may contain no operations. This allows QubitLens to represent an empty circuit with a valid qubit register before the user places any gates or measurements.

### Immutability

The Phase 1.1 domain objects are implemented as frozen dataclasses.

This makes `GateOperation`, `Measurement`, and `Circuit` immutable after construction. Their collection fields also use tuples rather than mutable lists.

Immutability is useful for the QubitLens architecture because a circuit and its operations represent structured facts that later systems will consume. Analysis, explanation, visualization, and export code should be able to inspect the same circuit representation without one layer unexpectedly modifying it for another.

If a circuit configuration changes, a new or replaced domain object can represent that change rather than silently mutating an existing object.

### Validation Ownership

One of the main design decisions in 1.1 was separating **intrinsic validation** from **contextual validation**.

An intrinsic invariant can be checked using only the object itself.

For example, `GateOperation` rejects:

* empty or whitespace-only gate identifiers
* operations without targets
* negative target indices
* negative control indices
* duplicate targets
* duplicate controls
* qubits appearing as both targets and controls

`Measurement` similarly rejects negative qubit and classical-bit indices.

These conditions are invalid regardless of which circuit eventually contains the operation, so the operation objects own those checks.

Other validation depends on the surrounding circuit.

For example, a gate targeting qubit 7 is not inherently invalid. It is valid in a circuit containing at least eight qubits, but invalid in a circuit containing only three.

`Circuit` therefore owns validation that requires knowledge of `num_qubits`. It verifies that every target, control, and measured qubit referenced by its operations exists within the circuit.

This separation keeps validation close to the object that has enough information to make the decision.

### Gate-Specific Validation Boundary

Phase 1.1 deliberately does not validate gate-specific rules.

The circuit model does not currently decide that:

* a Hadamard gate requires exactly one target
* a controlled-X gate requires a particular combination of controls and targets
* a SWAP operation requires two targets
* a parameterized gate requires a particular number of parameters

Those rules require knowledge about individual gates and therefore belong to the Phase 1.2 gate catalogue.

Keeping that knowledge out of `GateOperation` prevents the circuit representation from becoming a second gate-definition system before the catalogue exists.

### Classical-Bit Boundary

Measurements store a non-negative classical-bit destination, but `Circuit` does not currently define a classical-register size.

As a result, Phase 1.1 can reject a negative classical-bit index but does not impose an upper bound on classical-bit destinations.

A complete classical-register model was not introduced as part of the Phase 1.1 circuit-domain objective, so the implementation does not expand the checkpoint by inventing one prematurely.

### Public Domain API

The public circuit-domain API is exposed through `qubitlens.domain`.

The intended imports are:

```python
from qubitlens.domain import Circuit, GateOperation, Measurement
```

The package declares these names through `__all__`, allowing consumers to depend on the domain package rather than the internal location of the implementation.

The `CircuitOperation` union remains an internal typing abstraction at this stage rather than being part of the public package API.

This gives later code a stable domain-facing import boundary while leaving the internal organization free to evolve.

### Python Concepts Used

Phase 1.1 introduced several Python features that are useful for domain modeling.

Frozen dataclasses provide concise immutable value-like objects while still allowing validation through `__post_init__`.

Variable-length tuple annotations such as `tuple[int, ...]` express immutable collections containing zero or more values of a particular type.

Union types using the `|` operator allow `CircuitOperation` to express that one operation may be either a `GateOperation` or a `Measurement`.

Generator expressions combined with `any()` provide a concise way to detect invalid values across collections, such as negative qubit indices.

Sets are used to reason about uniqueness and overlap. Comparing the length of a tuple with the length of its corresponding set detects duplicate qubits, while set intersection detects a qubit appearing in both the target and control collections.

The `__all__` module variable defines the intended public surface of the domain package rather than exposing every internal name as part of the API.

### Testing

The circuit domain model has a dedicated test package under:

```text
tests/domain/
```

The Phase 1.1 tests cover:

* complete gate-operation construction
* optional control and parameter defaults
* empty and whitespace-only gate identifiers
* missing targets
* negative target and control indices
* duplicate targets and controls
* target/control overlap
* measurement construction
* negative measurement indices
* empty circuits
* preservation of operation ordering
* invalid circuit qubit counts
* target, control, and measurement references outside the circuit
* immutability of gate operations, measurements, and circuits
* imports through the public `qubitlens.domain` package API

At the end of the implementation checkpoint, the domain test module contains 23 passing tests.

The complete project suite contains 63 passing tests, including the 40-test Phase 0 baseline and the 23 new circuit-domain tests.

The five Qiskit integration tests continue to pass independently, confirming that introducing the domain layer did not regress the execution-boundary behavior established during Phase 0.

### Quality Verification

Phase 1.1 was checked using the same quality gate established during Phase 0.

The final verification produced:

```text
full test suite:        63 passed
Qiskit integration:      5 passed
Ruff linting:            passed
Ruff formatting:         passed
mypy source checking:    passed
```

mypy successfully checked the complete `src` tree, including the new domain package.

While testing the new module, running mypy directly against the test file caused the installed `qubitlens` package to be treated as an external package without a `py.typed` marker. This was not a source typing failure: the project's established mypy configuration intentionally checks `src/qubitlens`, and the complete configured source check passed.

I kept the Phase 0 typing policy unchanged rather than modifying package metadata or suppressing the warning in response to an ad-hoc test-file invocation.

### 1.1 Result

Phase 1.1 establishes QubitLens's first circuit-domain representation.

QubitLens can now represent:

```text
Circuit
├── number of qubits
└── ordered operations
    ├── GateOperation
    │   ├── gate
    │   ├── targets
    │   ├── controls
    │   └── parameters
    │
    └── Measurement
        ├── qubit
        └── classical bit
```

The model is immutable, validates its gate-independent structural invariants, preserves circuit ordering, and exposes a small public API through `qubitlens.domain`.

It deliberately does not execute circuits or define the semantics of individual gates. Those responsibilities remain separated: Qiskit continues to handle quantum execution, while gate-specific definitions and metadata are the responsibility of Phase 1.2.


## 1.2 Gate Catalogue

### Goal

Phase 1.1 established how gate applications are represented inside a circuit, but it deliberately left the meaning and structural requirements of individual gates undefined.

The goal of Phase 1.2 is to establish the QubitLens gate catalogue: a consistent domain representation of the gates currently supported by QubitLens and the metadata required to validate their use.

The catalogue remains separate from quantum execution. It describes supported gates and their structural requirements, while Qiskit remains responsible for executing their quantum behavior.

### Gate Definitions

A supported gate is represented by the immutable `GateDefinition` domain model.

Each definition stores:

* a canonical gate name
* a display name
* the required number of target qubits
* the required number of control qubits
* the required number of parameters

Gate definitions validate their own intrinsic metadata. Names and display names cannot be empty, every gate requires at least one target, and control and parameter counts cannot be negative.

The definitions are immutable so gate metadata can be shared safely across later circuit, analysis, visualization, and execution-boundary code.

### Standard Gate Catalogue

The current catalogue contains 17 supported gate definitions:

* `I`
* `X`
* `Y`
* `Z`
* `H`
* `S`
* `S†`
* `T`
* `T†`
* `P`
* `CX`
* `CY`
* `CZ`
* `CCX`
* `CCZ`
* `SWAP`
* `CSWAP`

Canonical identifiers use lowercase names such as `"h"`, `"cx"`, and `"cswap"`, while display names remain presentation-oriented.

The catalogue is intentionally limited to the gates currently supported by QubitLens. Its representation allows additional gate definitions to be introduced later without changing the circuit-domain representation established in Phase 1.1.

Measurement is not part of the gate catalogue. It remains represented separately by the `Measurement` domain model because measurement is not an ordinary unitary gate application and includes a classical-bit destination.

### Catalogue Metadata

The catalogue captures structural gate requirements rather than gate matrices or execution implementations.

Examples include:

```text
H
targets:     1
controls:    0
parameters:  0

P
targets:     1
controls:    0
parameters:  1

CX
targets:     1
controls:    1
parameters:  0

CCX
targets:     1
controls:    2
parameters:  0

SWAP
targets:     2
controls:    0
parameters:  0

CSWAP
targets:     2
controls:    1
parameters:  0
```

This keeps the catalogue concerned with QubitLens domain semantics rather than duplicating the mathematical gate primitives in `qubitlens.core` or the execution behavior provided by Qiskit.

### Catalogue Lookup

Supported gate definitions can be retrieved by canonical identifier through `get_gate()`.

The catalogue tuple remains the source of gate definitions, while an internal name-to-definition mapping provides efficient lookup without requiring callers to depend on the catalogue's storage details.

Lookup is exact and does not normalize aliases, whitespace, or capitalization.

For example:

```python
get_gate("cx")
```

retrieves the supported controlled-X definition, while identifiers such as `"CX"`, `" cx "`, or an unsupported gate name are rejected rather than silently transformed.

This gives QubitLens stable canonical identifiers without coupling callers to the catalogue's internal representation.

### Gate-Specific Validation

Phase 1.2 implements the gate-specific validation boundary reserved during Phase 1.1.

`validate_gate_operation()` validates a `GateOperation` against its corresponding `GateDefinition`.

The validator checks:

* whether the gate is supported
* target count
* control count
* parameter count

For example, the catalogue can distinguish between the structural requirements of:

```text
H       → one target
CX      → one control and one target
CCX     → two controls and one target
SWAP    → two targets
CSWAP   → one control and two targets
P       → one target and one parameter
```

This validation remains separate from `GateOperation` itself.

`GateOperation` continues to represent structurally valid gate applications without being permanently restricted to the current catalogue. Catalogue-aware code can explicitly validate whether an operation satisfies the requirements of a gate currently supported by QubitLens.

This preserves three distinct validation responsibilities:

```text
GateOperation
    ↓
intrinsic structural validity

Gate catalogue
    ↓
supported-gate and gate-specific validity

Circuit
    ↓
circuit-relative qubit validity
```

Parameter values are not interpreted by the gate catalogue. Phase 1.2 validates parameter count only. Mathematical expression parsing, variables, and scientific input belong to Phase 2.

### Relationship to Core Gates

The Phase 0 `qubitlens.core` gate primitives and the Phase 1.2 domain catalogue have different responsibilities.

The core gate module represents mathematical gate behavior through matrices and other reusable mathematical foundations.

The domain gate catalogue represents which gates QubitLens currently supports and the structural metadata needed to describe and validate their use in circuit operations.

The domain catalogue does not import gate matrices from `core`, and it does not implement quantum execution.

This keeps the architectural distinction explicit:

```text
core.gates
    ↓
mathematical gate behavior

domain.gates
    ↓
gate definitions and domain requirements

Qiskit
    ↓
quantum execution
```

### Measurement Boundary

Measurement remains outside the gate catalogue.

Although measurement is an operation that can appear in a circuit, it is represented by the dedicated `Measurement` domain model introduced in Phase 1.1.

This avoids treating a non-unitary operation with a classical destination as though it were an ordinary quantum gate and preserves the type-level distinction already established by the circuit domain model.

### Public Domain API

The Phase 1.2 gate catalogue extends the existing `qubitlens.domain` public API.

The domain package now exposes:

```python
from qubitlens.domain import (
    STANDARD_GATES,
    Circuit,
    GateDefinition,
    GateOperation,
    Measurement,
    get_gate,
    validate_gate_operation,
)
```

`GateDefinition` provides the gate metadata representation.

`STANDARD_GATES` provides the current supported catalogue.

`get_gate()` provides canonical lookup.

`validate_gate_operation()` provides explicit catalogue-aware validation.

The internal name-to-definition lookup mapping remains private.

This keeps consumers dependent on the stable domain package boundary rather than the internal organization of the catalogue implementation.

### Python Concepts Used

Phase 1.2 extends the domain layer using several Python features and patterns.

Frozen dataclasses continue to provide immutable domain representations.

A tuple of `GateDefinition` objects provides a deterministic immutable catalogue collection.

A dictionary comprehension derives the internal canonical-name lookup mapping from the catalogue, keeping the tuple as the single source of gate definitions rather than manually maintaining duplicate collections.

Dictionary lookup provides direct retrieval by canonical identifier.

Exception translation converts an internal missing-key condition into a domain-facing `ValueError` for unsupported gates without exposing the catalogue's internal dictionary behavior.

Parameterized pytest tests allow related gate families and validation cases to share a single test contract while still producing independent test cases.

### Testing

The gate catalogue has dedicated coverage under:

```text
tests/domain/
```

The Phase 1.2 tests cover:

* gate-definition construction and defaults
* empty and whitespace-only gate names
* empty and whitespace-only display names
* invalid target counts
* invalid control counts
* invalid parameter counts
* gate-definition immutability
* the exact supported catalogue inventory
* uniqueness of canonical gate identifiers
* parameterized gate metadata
* controlled single-target gate metadata
* doubly controlled gate metadata
* multi-target gate metadata
* controlled multi-target gate metadata
* canonical gate lookup
* identity of retrieved catalogue definitions
* rejection of unsupported and noncanonical identifiers
* valid catalogue-aware gate operations
* unsupported gates during catalogue-aware validation
* invalid target counts during catalogue-aware validation
* invalid control counts during catalogue-aware validation
* invalid parameter counts during catalogue-aware validation
* public exposure of the gate catalogue and validation API
* regression coverage for the Phase 1.1 public circuit-domain API

The complete domain suite currently contains 61 passing tests, covering both the Phase 1.1 circuit-domain model and the Phase 1.2 gate catalogue.

### Quality Verification

Phase 1.2 was checked using the project quality gate established during Phase 0 and continued throughout Phase 1.

The final local verification produced:

```text
full test suite:        101 passed
Qiskit integration:      5 passed
Ruff linting:            passed
Ruff formatting:         passed
mypy source checking:    passed
git diff check:           passed
```

The full test suite includes the existing core, circuit-domain, Qiskit integration, and package tests together with the new gate catalogue, catalogue-aware validation, and public domain API coverage.

The five Qiskit integration tests continue to pass independently, confirming that the Phase 1.2 domain changes did not regress the execution-boundary assumptions established during Phase 0.

Ruff reports the complete project clean, all 23 tracked Python files checked by the formatter are already formatted, and mypy successfully checks all 10 source files.

Clean-environment verification through GitHub Actions remains part of the Git checkpoint and will be confirmed after the Phase 1.2 commit is pushed.


### 1.2 Result

Phase 1.2 establishes the gate catalogue and the gate-specific semantic validation boundary for the QubitLens domain.

QubitLens can now:

* represent immutable gate definitions
* enumerate the current supported gate catalogue
* retrieve gate definitions through canonical identifiers
* distinguish presentation names from stable internal identifiers
* describe target, control, and parameter requirements
* validate gate operations against supported gate definitions
* keep gate-specific semantics separate from the generic circuit representation
* expose the catalogue through the public `qubitlens.domain` API

The circuit model remains independent of the current catalogue, and Qiskit remains responsible for quantum execution.

The catalogue also remains independent of Phase 2 mathematical-input concerns: it records how many parameters a gate requires without deciding how mathematical expressions, variables, or scientific input are represented.

With circuit structure and gate definitions established, the final Phase 1 checkpoint is **1.3 Initial-State Model**.

## 1.3 Initial-State Model

### Goal

Phase 1.1 established how circuits and their ordered operations are represented, while Phase 1.2 established the supported gate catalogue and gate-specific structural requirements.

The goal of Phase 1.3 is to establish how the quantum state that exists before circuit execution begins is represented within the QubitLens domain.

The initial-state model remains a representation rather than an execution mechanism. It describes the state from which execution begins, while Qiskit remains responsible for evolving that state through the circuit.

### Initial-State Representation

An initial quantum state is represented by the immutable `InitialState` domain model.

`InitialState` stores the complete pure statevector as a tuple of complex amplitudes:

```python
InitialState(
    amplitudes=(
        1 + 0j,
        0j,
    )
)
```

The complete statevector is stored rather than separate per-qubit states.

This is important because a general multi-qubit pure state cannot always be decomposed into independent states for each qubit. Representing the complete statevector allows the domain model to describe superposition and entangled initial states without introducing a second representation later.

For example, a two-qubit Bell state can be represented directly:

```python
import math

from qubitlens.domain import InitialState

amplitude = 1 / math.sqrt(2)

state = InitialState(
    amplitudes=(
        amplitude + 0j,
        0j,
        0j,
        amplitude + 0j,
    )
)
```

### Statevector Validation

`InitialState` validates the mathematical invariants required by the domain representation.

A valid statevector must:

* contain at least two amplitudes
* have a dimension that is a power of two
* contain only finite real and imaginary components
* be normalized to unit length

For a statevector with amplitudes \(\alpha_i\), normalization requires:

\[
\sum_i |\alpha_i|^2 = 1
\]

Floating-point comparison is used when validating normalization rather than requiring exact equality.

The number of qubits is derived from the statevector dimension rather than stored separately. For a valid statevector of dimension \(2^n\), `num_qubits` returns \(n\).

This prevents the state from carrying duplicated dimensional information that could become inconsistent.

### Computational-Basis Constructors

`InitialState` provides convenience constructors for common computational-basis states.

The all-zero state can be created with:

```python
from qubitlens.domain import InitialState

state = InitialState.zero(3)
```

which represents:

```text
|000⟩
```

A particular computational-basis state can be created with:

```python
state = InitialState.basis(3, 5)
```

which represents basis index 5:

```text
|101⟩
```

The basis-state constructor validates that at least one qubit is requested and that the basis index lies within the corresponding statevector.

`zero()` delegates to the general computational-basis constructor with basis index 0, keeping computational-basis construction on a single implementation path.

### Circuit Integration

`Circuit` now supports an initial state in addition to its qubit count and ordered operations.

A circuit can be constructed without explicitly providing one:

```python
from qubitlens.domain import Circuit

circuit = Circuit(num_qubits=3)
```

In this case, the circuit canonicalizes the omitted initial state to:

```text
|000⟩
```

through `InitialState.zero(3)`.

This preserves the conventional all-zero starting state and keeps the existing circuit-construction API convenient.

A custom state can also be supplied explicitly:

```python
from qubitlens.domain import Circuit, InitialState

circuit = Circuit(
    num_qubits=3,
    initial_state=InitialState.basis(3, 5),
)
```

The initial state must describe the same number of qubits as the circuit.

For example, a three-qubit circuit cannot be constructed with a two-qubit initial state.

This compatibility check belongs to `Circuit` because it depends on the relationship between two otherwise valid domain objects.

### Default-State Canonicalization

The constructor accepts `None` as the default value for `initial_state`, but a missing state is resolved during circuit construction to the corresponding all-zero `InitialState`.

This means the domain establishes one canonical representation for the actual starting state rather than requiring later execution or analysis code to independently decide what an omitted initial state means.

Because `Circuit` is a frozen dataclass, the default state is assigned during `__post_init__` using the construction-time mechanism needed to establish the validated immutable object.

### Immutability

`InitialState` is a frozen dataclass and stores its amplitudes as a tuple.

Using an immutable Python collection is intentional. A frozen dataclass containing a mutable numerical array would still allow the array contents to change even if the field itself could not be reassigned.

The tuple representation keeps the initial-state value stable after construction and matches the immutable domain-model approach established by the circuit and gate representations.

### Public Domain API

`InitialState` is exposed through `qubitlens.domain`.

The Phase 1 public domain API now includes:

```python
from qubitlens.domain import (
    STANDARD_GATES,
    Circuit,
    GateDefinition,
    GateOperation,
    InitialState,
    Measurement,
    get_gate,
    validate_gate_operation,
)
```

Consumers therefore do not need to depend on the internal module location of the initial-state implementation.

### Python Concepts Used

Phase 1.3 uses several Python features and patterns that support the domain design.

Frozen dataclasses continue to provide immutable value-like domain objects.

Complex amplitudes use Python's built-in `complex` type, keeping the domain representation independent of a numerical-array implementation.

Tuple storage provides an immutable statevector representation.

Bitwise power-of-two checks validate that a statevector dimension can represent an integer number of qubits.

`int.bit_length()` derives the qubit count from an already validated power-of-two dimension without requiring floating-point logarithms.

Generator expressions and `any()` validate finite amplitude components, while `sum()` computes the squared statevector norm.

`math.isfinite()` rejects non-finite real or imaginary components, and `math.isclose()` provides floating-point-aware normalization validation.

Class methods provide semantic constructors for all-zero and arbitrary computational-basis states.

### Testing

Phase 1.3 adds dedicated initial-state coverage under:

```text
tests/domain/test_initial_state.py
```

The tests cover:

* valid normalized one-qubit states
* complex superpositions
* multi-qubit entangled statevectors
* empty and zero-qubit statevectors
* non-power-of-two dimensions
* non-finite real and imaginary amplitude components
* non-normalized statevectors
* derived qubit counts
* all-zero computational-basis construction
* arbitrary computational-basis construction
* invalid qubit counts
* out-of-range basis indices
* default circuit initial states
* explicit matching circuit initial states
* circuit/state qubit-count mismatches
* preservation of the existing positional circuit-construction API

The complete domain suite contains 88 passing tests after Phase 1.3.

### Quality Verification

Phase 1.3 was checked using the project quality gate established during Phase 0 and continued throughout Phase 1.

The final local verification produced:

```text
domain test suite:      88 passed
full test suite:       128 passed
Qiskit integration:      5 passed
Ruff linting:            passed
Ruff formatting:         passed
mypy source checking:    passed
```

Ruff reports the project clean and all 25 Python files checked by the formatter are formatted.

mypy successfully checks all 11 source files.

The five Qiskit integration tests continue to pass independently, confirming that introducing configurable initial states did not regress the Qiskit execution-boundary behavior established during Phase 0.

### 1.3 Result

Phase 1.3 establishes configurable initial quantum states as part of the QubitLens domain.

QubitLens can now:

* represent immutable normalized pure statevectors
* represent real and complex amplitudes
* represent arbitrary multi-qubit pure states, including entangled states
* derive the number of qubits from statevector dimension
* construct all-zero initial states
* construct arbitrary computational-basis states
* associate explicit initial states with circuits
* provide the conventional all-zero state when no custom state is supplied
* validate compatibility between circuit width and initial-state width
* expose initial-state construction through the public `qubitlens.domain` API

Together, Phases 1.1, 1.2, and 1.3 establish the complete Phase 1 quantum-domain foundation: circuit structure, supported gate definitions, and configurable starting states.

Quantum execution remains behind the Qiskit boundary. The domain describes what a circuit contains and where it begins without becoming a second simulator.
