# QubitLens Architecture

## Purpose

QubitLens is an interactive quantum circuit analysis, explanation, and visualization tool built on top of Qiskit.

Its architecture separates circuit representation, quantum execution, mathematical foundations, structured analysis, explanation, and presentation so that each layer has a clear responsibility.

QubitLens does not aim to replace Qiskit or implement a separate quantum simulator. Qiskit remains the quantum execution engine, while QubitLens provides the domain representations and analysis-oriented structures needed to inspect, understand, explain, and eventually visualize circuit behavior.

## Package Structure

The current source package is organized into four main areas:

```text
qubitlens/
├── core/
├── domain/
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

`qubitlens.domain` contains QubitLens's internal quantum-domain representations.

The circuit-domain API currently exposes:

* `Circuit`
* `GateOperation`
* `Measurement`

A `Circuit` describes the number of qubits in a circuit and preserves its ordered operations.

A `GateOperation` describes the placement and configuration of a gate application through its gate identifier, targets, controls, and parameters.

A `Measurement` describes the measurement of a qubit into a classical bit.

These objects represent circuit structure. They do not execute the operations they describe.

The domain models are immutable and validate gate-independent structural invariants. Validation that depends on the meaning of a particular gate belongs to the gate catalogue rather than the circuit representation itself.

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

These checks belong to the operation objects because no external context is required to determine that the configuration is invalid.

### Circuit-Relative Validation

A `Circuit` validates properties that depend on its own configuration.

For example, an operation referencing qubit 4 may be valid in a five-qubit circuit and invalid in a two-qubit circuit.

The circuit therefore verifies that target, control, and measured qubits fall within its qubit register.

### Gate-Specific Validation

Rules that depend on the meaning of a particular gate are kept outside the generic circuit model.

Examples include:

* required target count
* required control count
* required parameter count
* gate-specific metadata

These responsibilities belong to the gate catalogue rather than `Circuit` or `GateOperation`.

This keeps circuit structure independent from the definitions of the gates placed within it.

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
└── integration/
```

Core tests verify QubitLens's mathematical foundations independently.

Domain tests verify circuit representation, structural validation, ordering, immutability, and public domain behavior.

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
