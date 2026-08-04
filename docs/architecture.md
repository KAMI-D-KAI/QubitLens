# QubitLens Architecture

## Purpose

QubitLens is an interactive quantum circuit analysis, explanation, and visualization tool built on top of Qiskit.

Its architecture separates circuit representation, quantum execution, mathematical foundations, structured analysis, explanation, and presentation so that each layer has a clear responsibility.

QubitLens does not aim to replace Qiskit or implement a separate quantum simulator. Qiskit remains the quantum execution engine, while QubitLens provides the domain representations and analysis-oriented structures needed to inspect, understand, explain, and eventually visualize circuit behavior.

## Package Structure

The current source package is organized into five main areas:

```text
qubitlens/
├── core/
├── domain/
├── input/
├── analysis/
└── explanation/
```

Each package represents a different architectural responsibility.

### Core

`qubitlens.core` contains shared mathematical and quantum foundations.

The current core provides:

* common single-qubit gate matrices
* an immutable pure-state representation
* construction of single-qubit operators for multi-qubit systems
* the qubit-ordering convention used by QubitLens

Core components describe mathematical behavior that can be tested independently of circuit execution or user-facing interpretation.

The core does not:

* execute complete circuits
* own circuit structure
* interpret circuit evolution
* generate explanations
* make presentation decisions

Keeping these responsibilities separate allows the mathematical foundation to remain small and reusable.

### Domain

`qubitlens.domain` contains QubitLens's internal quantum-domain representations and gate-catalogue capabilities.

The domain API currently exposes:

* `Circuit`
* `GateOperation`
* `Measurement`
* `InitialState`
* `GateDefinition`
* `STANDARD_GATES`
* `get_gate`
* `validate_gate_operation`

A `Circuit` describes the number of qubits in a circuit, its initial quantum state, and its ordered operations.

A `GateOperation` describes the placement and configuration of a gate application through its gate identifier, targets, controls, and parameters.

A `Measurement` describes the measurement of a qubit into a classical bit.

An `InitialState` represents the complete normalized pure statevector from which circuit execution begins. The full statevector representation supports computational-basis states, superpositions, and entangled multi-qubit states while keeping the domain independent of execution behavior.

When no custom initial state is supplied, `Circuit` canonicalizes the starting state to the all-zero computational basis state for its qubit count. An explicitly supplied initial state must represent the same number of qubits as the circuit.

A `GateDefinition` describes the structural metadata of a gate supported by QubitLens, including its canonical identifier, display name, and required target, control, and parameter counts.

`STANDARD_GATES` provides the current supported gate definitions, while `get_gate()` provides lookup through exact canonical identifiers.

`validate_gate_operation()` applies catalogue-defined structural requirements to a gate operation, including supported-gate, target-count, control-count, and parameter-count validation.

These objects and services represent quantum-domain structure and requirements. They do not execute the operations they describe.

The circuit models remain responsible for gate-independent structural invariants and circuit-relative validation. Gate-specific requirements remain separate from the generic circuit representation and are enforced explicitly through catalogue-aware validation.

This separation allows the circuit representation to remain structurally generic while supported gate semantics can evolve through the catalogue without coupling circuit structure to a fixed set of gates.


### Input

`qubitlens.input` owns the boundary between human-written mathematical text and validated values consumed by QubitLens.

The current input subsystem provides a safe expression engine for restricted real and complex mathematics. Expressions are parsed into Python abstract syntax trees, validated against an explicit mathematical language, and interpreted directly by QubitLens without using Python's general-purpose `eval()` or `exec()` machinery.

The expression engine supports whitelisted mathematical constants, functions, arithmetic operators, complex values, and grouping while rejecting unsupported Python constructs and identifiers.

The input boundary also enforces resource limits on expression length, AST depth, AST node count, and exponent magnitude, and rejects non-finite results.

The input subsystem does not:

* execute quantum circuits
* own circuit or gate semantics
* normalize or validate quantum states
* interpret gate parameters
* perform analysis or explanation

The input subsystem also provides symbolic parameter binding and scientific state input while remaining solely responsible for translating human-written mathematical input into validated QubitLens values.


### Analysis

`qubitlens.analysis` is responsible for turning circuit execution and state-evolution information into structured facts.

The important boundary is that analysis produces structured information rather than user-facing prose.

Later analysis may describe information such as:

* how amplitudes changed
* how measurement probabilities changed
* how phases changed
* which properties of a quantum state were affected by an operation
* how a circuit evolved from one step to the next

Analysis may consume QubitLens domain objects, mathematical foundations from `core`, and execution information produced through the Qiskit integration boundary.

It does not replace Qiskit as the execution engine and does not own human-facing explanation.

### Explanation

`qubitlens.explanation` is responsible for turning structured analysis into human-readable insights.

Mathematical interpretation should already have occurred in the analysis layer. Explanation focuses on communicating those results clearly rather than independently recalculating them.

This separation allows the same structured analysis to support explanation, visualization, export, and interactive inspection without each feature implementing its own interpretation of circuit behavior.

## Circuit Representation and Execution

QubitLens separates **circuit representation** from **circuit execution**.

QubitLens owns the internal domain representation used by its analysis-oriented architecture:

```text
Circuit
├── initial state
└── ordered operations
    ├── GateOperation
    └── Measurement
```

This representation gives QubitLens a stable model that can be consumed by later analysis, explanation, visualization, and export systems without requiring those layers to depend directly on Qiskit's circuit object model.

Qiskit remains responsible for executing quantum behavior and evolving quantum states.

The intended relationship is:

```text
QubitLens domain
      ↓
describes circuit structure
      ↓
Qiskit execution boundary
      ↓
produces quantum evolution
      ↓
QubitLens analysis
      ↓
produces structured facts
      ↓
explanation / visualization / export
```

Owning an internal circuit representation does not mean QubitLens is implementing a second simulator. The domain layer describes what a circuit contains; Qiskit determines the quantum behavior produced when that circuit is executed.

## Domain Validation

Validation is divided according to which object has enough information to enforce an invariant.

### Intrinsic Validation

Domain objects validate properties that are invalid regardless of their surrounding circuit.

Examples include:

* empty gate identifiers
* gate operations without targets
* negative qubit indices
* duplicate target or control qubits
* target/control overlap
* negative measurement indices
* invalid initial-state dimensions
* non-finite statevector amplitudes
* non-normalized statevectors

These checks belong to the operation objects because no external context is required to determine that the configuration is invalid.

### Circuit-Relative Validation

A `Circuit` validates properties that depend on its own configuration.

For example, an operation referencing qubit 4 may be valid in a five-qubit circuit and invalid in a two-qubit circuit.

The circuit therefore verifies that target, control, and measured qubits fall within its qubit register.

The circuit also verifies that an explicitly supplied initial state represents the same number of qubits as the circuit. This is circuit-relative validation because both the `InitialState` and the `Circuit` may be individually valid while their dimensions are incompatible with each other.

### Gate-Specific Validation

Rules that depend on the meaning of a particular gate are kept outside the generic circuit model.

`GateDefinition` represents the structural requirements of a supported gate, including:

* required target count
* required control count
* required parameter count
* canonical and display identifiers

`validate_gate_operation()` applies those requirements to a `GateOperation`.

The validator determines whether the operation refers to a currently supported gate and whether its numbers of targets, controls, and parameters match the corresponding gate definition.

This validation is explicit rather than built into `GateOperation`. The circuit representation can therefore remain structurally generic instead of being permanently restricted to the current supported gate catalogue.

Validation responsibility is divided into three layers:

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

The catalogue does not execute gates or interpret parameter values. Quantum execution remains behind the Qiskit boundary, while mathematical expression parsing, variables, and scientific input belong to the later mathematical input system.

This keeps gate definitions, circuit representation, mathematical input, and quantum execution as separate architectural responsibilities.


## Qubit Ordering

QubitLens follows Qiskit's little-endian computational-basis convention.

For a two-qubit register written as `|q1 q0⟩`, qubit 0 is the least-significant bit.

Applying `X` to `q0` corresponds to:

```text
I ⊗ X
```

while applying `X` to `q1` corresponds to:

```text
X ⊗ I
```

This convention is established mathematically by the core tests and independently verified against Qiskit through integration tests.

Keeping the ordering convention explicit is important because circuit structure, state evolution, analysis, and visualization must all interpret qubit indices consistently.

## Dependency Direction

The architecture follows a one-way dependency principle: lower-level representations and mathematical foundations should not depend on the higher-level systems that interpret or present them.

Conceptually:

```text
core ───────┐
            ↓
domain → analysis → explanation
```

The exact dependencies may evolve as the analysis APIs are implemented, but the responsibility direction remains:

* `core` provides shared mathematical foundations
* `domain` provides quantum-domain representations
* `analysis` consumes representations and execution information to derive structured facts
* `explanation` consumes structured analysis to produce human-readable insights

Higher layers may use lower-level representations where appropriate.

Reverse dependencies are avoided:

* `core` does not depend on `analysis` or `explanation`
* `domain` does not depend on `analysis` or `explanation`
* `analysis` does not depend on `explanation`

The domain and core layers serve different purposes. Core describes reusable mathematical behavior, while domain describes QubitLens concepts such as circuits and operations.

Neither layer should become responsible for user-facing interpretation.

## Qiskit Boundary

Qiskit is an execution dependency, not the architectural center of QubitLens.

QubitLens uses Qiskit where mature quantum execution behavior is needed rather than reproducing that functionality internally.

This boundary provides two benefits.

First, QubitLens can focus on its actual purpose: inspecting, structuring, explaining, and visualizing quantum circuit behavior.

Second, Qiskit provides an independent implementation against which integration assumptions can be verified.

QubitLens's core tests establish its own mathematical contracts. Integration tests separately verify that behavior at the Qiskit boundary agrees with Qiskit.

This distinction prevents external integration behavior from becoming the only definition of correctness inside QubitLens.

## Testing Boundaries

Tests are organized according to the responsibility they verify.

```text
tests/
├── core/
├── domain/
├── input/
└── integration/
```

Core tests verify QubitLens's mathematical foundations independently.

Domain tests verify circuit representation, structural validation, ordering, immutability, and public domain behavior.

Input tests verify mathematical expression behavior, rejection boundaries, security constraints, and resource limits.

Integration tests verify assumptions that cross the Qiskit boundary.

The distinction is intentional:

```text
core/domain tests
        ↓
Does QubitLens satisfy its own contract?

integration tests
        ↓
Does behavior at the external boundary agree with Qiskit?
```

This keeps internal correctness separate from external compatibility while testing both.

## Quality Boundary

The project quality gate combines complementary forms of verification:

* pytest for behavioral correctness
* Ruff for formatting and linting
* mypy for source type contracts
* GitHub Actions for clean-environment verification

Behavioral tests establish what the code does.

Static typing establishes what the source promises about its interfaces and representations.

Linting and formatting maintain a consistent codebase.

Continuous integration verifies those expectations outside the local development environment.

These tools support the architecture, but none replaces the others.

## Architectural Principle

The central architectural boundary in QubitLens is:

```text
represent
    ↓
execute
    ↓
analyze
    ↓
explain
    ↓
present
```

QubitLens owns the representations and interpretation needed for inspection and understanding.

Qiskit owns mature quantum execution.

Analysis turns execution into reusable structured information.

Explanation turns that information into human-understandable insights.

Visualization and export can later consume the same underlying domain and analysis structures without duplicating their logic.

Keeping these responsibilities separate allows QubitLens to grow as an analysis and learning tool without gradually becoming a second quantum simulator or coupling every feature directly to the execution backend.
