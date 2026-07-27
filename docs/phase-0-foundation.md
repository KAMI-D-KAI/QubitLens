# QubitLens Phase 0: Foundation

**Author:** Vedank Srivastava
**Status:** In progress. This document reflects what's been built so far.

## Objective

Phase 0 is about laying down the project, architectural, and mathematical groundwork QubitLens needs before it can start analyzing Qiskit circuits. The goal isn't to build another quantum simulator, since Qiskit already does that well. It's to get the scaffolding right: a small, well-tested core that keeps quantum execution and QubitLens's own analysis responsibilities cleanly separated. That boundary is worth getting right early, because everything in later phases builds directly on top of it.

## Project Foundation

QubitLens is set up as an installable Python package using a `src` layout, with `pyproject.toml` defining package metadata, runtime and dev dependencies, build configuration, and test configuration.

The package is split into three areas from the start:

- `core` for shared mathematical and quantum foundations
- `analysis` for structured circuit analysis
- `explanation` for turning analysis output into human-understandable explanations

Splitting these apart early is meant to keep mathematical representation, factual analysis, and presentation from bleeding into each other as the project grows. It's easier to enforce that with structure than to rely on remembering to keep things tidy later.

## Quantum Core

The first real implementation in `core` introduces:

- standard single-qubit gate matrices
- an immutable pure-state representation
- utilities for embedding single-qubit operators into multi-qubit Hilbert spaces

These are meant to stay as mathematical primitives that later analysis code can build on, not the start of a second quantum simulator living inside QubitLens.

## Execution Boundary

Qiskit is QubitLens's quantum execution engine. QubitLens inspects and analyzes circuit behavior; it doesn't try to duplicate Qiskit's ability to actually run circuits. Keeping that boundary firm avoids reinventing something Qiskit already handles well, and keeps the project focused on what it's actually for: making quantum circuit behavior easier to inspect, explain, and visualize.

## Analysis and Explanation Boundary

The package-level separation between `core`, `analysis`, and `explanation` is
now backed by an explicit dependency boundary.

`core` remains independent of the higher-level interpretation layers.
`analysis` may build on core foundations to turn execution data into structured
facts, while `explanation` may consume those analysis results and shared core
representations to produce human-readable insights.

The dependency direction is intentionally one-way: core does not depend on
analysis or explanation, and analysis does not depend on explanation. This
keeps structured analysis reusable by future consumers such as visualization
rather than coupling the mathematical interpretation directly to its
presentation.

No analysis or explanation APIs are introduced at this stage. Their package
responsibilities are established now so later implementation can grow within
those boundaries instead of defining them retroactively.

## Qubit Ordering

QubitLens follows Qiskit's computational-basis ordering convention. For a two-qubit register written as `|q1 q0⟩`, qubit 0 is the least-significant bit.

So applying `X` to `q0` corresponds to:

```
I ⊗ X
```

while applying `X` to `q1` corresponds to:

```
X ⊗ I
```

This is the kind of convention that's easy to get backwards without noticing. Pinning it down early avoids a much more confusing debugging session down the line, once QubitLens starts comparing its own analysis against real Qiskit statevectors.

## Testing

The core foundation is covered by tests so far for:

- gate definitions and unitarity
- basis-state gate behavior
- statevector dimensions and normalization
- measurement probabilities
- invalid state handling
- operator dimensions and unitarity
- multi-qubit operator ordering

## Verifying Qubit Ordering Against Qiskit

The initial operator tests only checked QubitLens's tensor-product ordering against itself, which proves internal consistency, not correctness. A bug can be internally consistent and still be a bug. So an integration test was added using Qiskit's `QuantumCircuit` and `Statevector` APIs: for representative single-qubit operations, QubitLens constructs the corresponding full-system operator and evolves the initial state mathematically, while the same operation is independently built as a Qiskit circuit and evolved using Qiskit's own statevector implementation. The resulting statevectors are then compared numerically.

This confirms that QubitLens's operator construction matches the computational-basis ordering the analysis layer will later depend on. It also set a testing principle to carry through the rest of the project: anything touching a Qiskit integration boundary gets verified against Qiskit itself, not just against QubitLens's own assumptions about how it should behave.

## Development Quality Tooling and Continuous Integration

As the foundation grew past the initial package structure, this felt like the right point to start adding automated checks, before shortcuts and bad habits had a chance to set in.

### Test categorization

Tests that check QubitLens behavior directly against Qiskit are marked with a registered pytest `integration` marker, so the full suite, integration only tests, and unit only tests can each be run independently. This becomes more useful as integration tests grow slower and more expensive relative to isolated unit tests.

### Formatting and linting

Ruff handles formatting and static linting. The initial ruleset sticks to Python errors, Pyflakes checks, and import organization, deliberately staying away from an aggressively strict style config this early on.

One intentional exception: the conventional quantum-computing symbol `I` is kept for the identity matrix, even though generic linting rules flag it as an ambiguous variable name. In this context `I` is the standard notation for the identity operator, so the domain convention wins over the generic lint rule.

### Static type checking

mypy validates type contracts across the source package. During initial integration, it caught something worth noting: NumPy's inferred return type for a Kronecker product was broader than the `ComplexMatrix` representation QubitLens promises. The implementation was numerically correct, the values were right, but the type checker exposed a representation guarantee that hadn't actually been made explicit in code. Operator construction now explicitly normalizes Kronecker-product results to `np.complex128` to close that gap.

It was a useful reminder that behavioral testing and static analysis catch genuinely different classes of problems. One confirms the math works, the other confirms the code says what it means.

### Continuous integration

A GitHub Actions workflow reproduces the local quality checks in a fresh Linux environment, installing QubitLens with its dev dependencies and running:

- Ruff linting
- Ruff formatting
- mypy type checking
- the full pytest suite

The main quality job runs on Python 3.11, which is also the minimum Python version the project currently supports. Python 3.12 is checked separately by running the full test suite as a compatibility job.

The first version of the CI workflow actually ran the entire quality pipeline on both versions, which exposed an interesting issue: mypy is intentionally configured to analyze against Python 3.11, but NumPy's type stubs in the Python 3.12 environment used syntax that belongs to Python 3.12. Rather than weakening the minimum-version type check just to make the matrix green, I split the responsibilities. Python 3.11 now handles linting, formatting, static type checking, and tests, while Python 3.12 independently verifies runtime compatibility.

Since local development happens on Windows and CI runs on Linux, this also gives me an early check that nothing is quietly depending on my local environment.

---

This is where Phase 0 stands right now: the package structure, core primitives, a verified Qiskit boundary, and a CI pipeline enforcing all of it. There's more to round out before it's truly done, and Phase 1's analysis layer is next once it is.