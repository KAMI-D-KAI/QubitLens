# QubitLens Phase 1: Quantum Domain Foundation

**Author:** Vedank Srivastava
**Status:** In Progress

## Objective

Phase 0 established the engineering, architectural, and mathematical foundation that QubitLens needs to grow reliably. Phase 1 builds on that foundation by introducing the project's own quantum-domain representations: the structures QubitLens can use to describe circuits, gates, and initial quantum states independently of how those objects are eventually executed, analyzed, explained, or visualized.

The goal is not to turn QubitLens into a separate quantum execution engine. Qiskit remains responsible for quantum execution and continues to provide an external reference for integration behavior. The domain layer instead gives QubitLens a representation designed around its own needs, so later analysis and explanation code can reason about quantum circuits without depending directly on Qiskit's internal object model.

Phase 1 is divided into three parts:

* **1.1 Circuit Domain Model** establishes the representation of circuits, gate applications, and measurements.
* **1.2 Gate Catalogue** will define the supported gates and the metadata needed to describe their behavior and requirements.
* **1.3 Initial-State Model** will establish how configurable initial quantum states are represented before circuit execution begins.

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
* a rotation gate requires a particular number of parameters

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

With the circuit structure established, the next checkpoint is **1.2 Gate Catalogue**.
