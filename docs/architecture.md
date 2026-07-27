# Phase 0: Foundation

## Goal

Phase 0 establishes the engineering and mathematical foundation of QubitLens before circuit analysis is introduced.

## Project Setup

QubitLens uses a `src`-based Python package layout.

This ensures imports resolve through the installed package rather than accidentally resolving directly from the repository directory.

The project uses `pyproject.toml` for package metadata, dependencies, build configuration, and pytest configuration.

## Quantum Core

The first quantum components introduced were:

- common single-qubit gate matrices
- a pure-state representation
- single-qubit operator construction for multi-qubit systems

These components provide mathematical tools for later analysis without turning QubitLens into a separate quantum simulator.

### Why Qiskit remains the execution engine

An early architectural decision was to separate quantum execution from quantum analysis.

Qiskit already provides mature circuit and statevector functionality. Reimplementing circuit execution inside QubitLens would duplicate that responsibility and increase the surface area for correctness errors.

QubitLens therefore uses Qiskit for state evolution while maintaining only the mathematical representations required to inspect and explain that evolution.

## Qubit Ordering

QubitLens follows Qiskit's little-endian computational-basis convention.

For a two-qubit state written as `|q1 q0>`, applying X to q0 corresponds to `I ⊗ X`, while applying X to q1 corresponds to `X ⊗ I`.

This convention is established at the core layer so later circuit analysis remains consistent with Qiskit.

## Analysis and Explanation Boundaries

QubitLens separates mathematical foundations, structured analysis, and
human-facing explanation into distinct layers.

### Core

`qubitlens.core` contains shared mathematical and quantum foundations. It
defines representations, conventions, and small mathematical operations that
higher layers can rely on.

Core does not execute circuits, interpret circuit evolution, or generate
human-facing explanations.

### Analysis

`qubitlens.analysis` converts circuit execution data into structured facts
about circuit and state evolution.

Analysis may depend on the core mathematical foundations and may consume
results produced through Qiskit, but it does not replace Qiskit as the
execution engine. Its outputs should remain structured and suitable for
multiple consumers, including explanation and visualization.

Analysis does not generate presentation-oriented or educational prose.

### Explanation

`qubitlens.explanation` converts structured analysis into human-readable
insights.

Explanation may depend on analysis results and, where necessary, shared core
representations. It does not independently execute circuits or duplicate
mathematical analysis that belongs in the lower layers.

### Dependency Direction

Internal dependencies flow from higher-level interpretation toward lower-level
foundations:

- `analysis` may depend on `core`
- `explanation` may depend on `analysis`
- `explanation` may depend on `core` when shared representations are required

Dependencies in the opposite direction are avoided: `core` does not depend on
analysis or explanation, and analysis does not depend on explanation.

This keeps quantum foundations independent of interpretation and keeps
structured analysis reusable by explanation, visualization, and other future
consumers.
