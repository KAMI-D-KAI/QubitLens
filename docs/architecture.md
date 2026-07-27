# Phase 0: Foundation

## Goal

Phase 0 is where I'm building the engineering and mathematical foundation QubitLens will need before I start working on actual circuit analysis.

The main goal here is to get the boundaries right early. I want enough quantum and mathematical machinery inside QubitLens to inspect circuit behavior later, without slowly turning the project into another quantum simulator.

## Project Setup

I'm using a `src`-based Python package layout.

One reason for choosing this structure is that it forces imports to resolve through the installed `qubitlens` package rather than accidentally working because Python can see files directly from the repository root. That gives me a development environment that's closer to how the package is actually installed and used.

Project metadata, dependencies, build configuration, and tool configuration live in `pyproject.toml` so the basic project setup stays centralized.

## Quantum Core

The first quantum components I introduced into `core` are:

* common single-qubit gate matrices
* an immutable pure-state representation
* single-qubit operator construction for multi-qubit systems

I need these mathematical pieces because later analysis will have to reason about states, probabilities, operators, and how individual operations affect a larger register.

At the same time, I'm deliberately keeping the core small. These are foundations for inspecting quantum behavior, not the beginning of a second execution engine.

### Why Qiskit remains the execution engine

One of the early architectural decisions was to separate **quantum execution** from **quantum analysis**.

Qiskit already provides mature circuit and statevector functionality. Reimplementing circuit execution inside QubitLens would duplicate that responsibility and increase the surface area for correctness errors, while not really helping with what I'm trying to build.

So Qiskit remains responsible for circuit representation and state evolution. QubitLens keeps only the mathematical representations and utilities it needs to inspect, analyze, explain, and eventually visualize that evolution.

That boundary also gives me something useful when testing the project: QubitLens can define its own mathematical expectations, while Qiskit provides an independent implementation I can compare integration behavior against.

## Qubit Ordering

QubitLens follows Qiskit's little-endian computational-basis convention.

For a two-qubit register written as `|q1 q0⟩`, qubit 0 is the least-significant bit. Applying `X` to `q0` therefore corresponds to:

```text
I ⊗ X
```

while applying `X` to `q1` corresponds to:

```text
X ⊗ I
```

I wanted to establish this convention in the core before circuit analysis begins because qubit ordering is the kind of detail that can produce perfectly reasonable-looking but incorrect results if different parts of the project interpret it differently.

The core tests verify this convention mathematically, and the integration tests separately check that the resulting state evolution agrees with Qiskit.

## Analysis and Explanation Boundaries

Another boundary I wanted to establish before implementing either layer is the difference between **doing analysis** and **explaining analysis**.

The package is split so mathematical foundations, structured interpretation, and human-facing communication don't gradually collapse into one layer.

### Core

`qubitlens.core` contains the shared mathematical and quantum foundations.

This is where representations, conventions, and small mathematical operations belong. Higher layers can build on these pieces, but the core shouldn't need to know anything about how those results will eventually be analyzed, explained, or displayed.

In particular, core does not:

* execute circuits
* interpret circuit evolution
* generate explanations
* make presentation decisions

Keeping those responsibilities out of the core lets it stay focused on mathematical behavior that can be tested independently.

### Analysis

`qubitlens.analysis` will turn circuit execution data into structured facts about what happened during circuit and state evolution.

The important part of that definition for me is **structured facts**.

I don't want the analysis layer producing sentences intended for the user. Its job is to determine information that other parts of QubitLens can consume. Later, that might include changes in amplitudes, probabilities, phase, or other properties of a state as a circuit evolves.

Analysis may use the mathematical foundations in `core` and consume execution results produced through Qiskit, but it does not replace Qiskit as the execution engine.

Keeping the output structured also means the same analysis can eventually support more than explanations. Visualization, interactive inspection, and export features should be able to consume the same underlying information without having to reproduce the analysis themselves.

### Explanation

`qubitlens.explanation` sits above that structured analysis.

Its responsibility will be to turn analysis results into human-readable insights. The mathematical interpretation should already have happened lower down; explanation is concerned with communicating that information clearly.

This means I want to avoid explanation code independently recalculating facts that belong in analysis. If probability changes or state properties are derived in two different layers, those implementations can eventually disagree.

Explanation may depend on analysis results and, where useful, shared representations from `core`. It should not execute circuits or become a second mathematical analysis layer.

## Dependency Direction

The internal dependency direction follows the responsibility boundaries:

* `analysis` may depend on `core`
* `explanation` may depend on `analysis`
* `explanation` may depend directly on `core` when shared representations are useful

The reverse dependencies are intentionally avoided:

* `core` does not depend on `analysis`
* `core` does not depend on `explanation`
* `analysis` does not depend on `explanation`

I don't want to enforce these boundaries through unnecessary abstractions before the actual analysis APIs exist. For now, defining the responsibilities and dependency direction gives later implementation a clear place to grow.

The broader idea is that quantum foundations stay independent of interpretation, analysis stays independent of presentation, and structured results remain reusable by whatever QubitLens builds on top of them later.
