# Phase 0: Foundation

## Objective

Phase 0 establishes the project, architectural, and mathematical foundation required before QubitLens begins analyzing Qiskit circuits.

The goal is to build a small and well-tested core while keeping quantum execution separate from QubitLens's analysis responsibilities.

## Project Foundation

QubitLens is structured as an installable Python package using a `src` layout.

The project uses `pyproject.toml` to define package metadata, runtime dependencies, development dependencies, build configuration, and test configuration.

The initial package is divided into three primary areas:

- `core` for shared mathematical and quantum foundations
- `analysis` for structured circuit analysis
- `explanation` for converting analysis into human-understandable information

This separation is intended to keep mathematical representation, factual analysis, and presentation concerns independent as the project grows.

## Quantum Core

The first core implementation introduces:

- standard single-qubit gate matrices
- an immutable pure-state representation
- utilities for embedding single-qubit operators into multi-qubit Hilbert spaces

These components provide mathematical primitives that later analysis code can use.

They are deliberately not being developed into a separate quantum simulator.

## Execution Boundary

Qiskit is the quantum execution engine for QubitLens.

QubitLens will inspect and analyze circuit behavior rather than duplicate Qiskit's circuit execution capabilities.

This boundary reduces duplicated functionality and allows the project to focus on its primary goal: making quantum circuit behavior easier to inspect, explain, and visualize.

## Qubit Ordering

QubitLens follows Qiskit's computational-basis ordering convention.

For a two-qubit register written as `|q1 q0>`, qubit 0 corresponds to the least-significant bit.

Therefore, applying `X` to `q0` corresponds to:

`I ⊗ X`

while applying `X` to `q1` corresponds to:

`X ⊗ I`

Establishing this convention early prevents inconsistencies when QubitLens later compares its analysis with Qiskit statevectors.

## Testing

The core foundation is tested for:

- gate definitions and unitarity
- basis-state gate behavior
- statevector dimensions and normalization
- measurement probabilities
- invalid state handling
- operator dimensions and unitarity
- multi-qubit operator ordering

## Verifying Qubit Ordering Against Qiskit

The initial operator tests established QubitLens's expected tensor-product ordering internally, but internal tests alone cannot prove that the convention matches Qiskit.

An integration test was therefore added using Qiskit's `QuantumCircuit` and `Statevector` APIs.

For representative single-qubit operations, QubitLens constructs the corresponding full-system operator and evolves the initial state mathematically. The same operation is independently represented as a Qiskit circuit and evolved using Qiskit's statevector implementation.

The resulting statevectors are compared numerically.

This verifies that QubitLens's operator construction follows the same computational-basis ordering used by the Qiskit functionality that the analysis layer will later consume.

It also establishes an important testing principle for the project: behavior at Qiskit integration boundaries should be verified against Qiskit rather than only against QubitLens's own assumptions.