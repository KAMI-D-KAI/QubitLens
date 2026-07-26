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