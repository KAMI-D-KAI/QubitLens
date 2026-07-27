# QubitLens Phase 0: Foundation

**Author:** Vedank Srivastava
**Status:** Complete

## Objective

Phase 0 is about building the engineering, architectural, and mathematical foundation QubitLens needs before I start implementing actual circuit analysis.

I don't want QubitLens to become another quantum simulator. Qiskit already handles circuit representation and quantum state evolution, so the more interesting problem for this project is what happens around that execution: inspecting it, structuring what changed, explaining those changes, and eventually visualizing them.

That made the main goal of Phase 0 less about adding features and more about getting the foundations right. I wanted a small quantum core, a clear execution boundary with Qiskit, tests that verify the mathematical assumptions I'm making, and enough engineering infrastructure that later phases can grow without constantly repairing the groundwork underneath them.

## Project Foundation

I set QubitLens up as an installable Python package using a `src` layout.

Project metadata, runtime and development dependencies, build configuration, and tool configuration are centralized in `pyproject.toml`.

The package is separated into three areas from the beginning:

* `core` for shared mathematical and quantum foundations
* `analysis` for structured circuit analysis
* `explanation` for turning analysis results into human-understandable insights

I introduced this separation before the analysis and explanation layers had implementations because I wanted their responsibilities to be visible in the structure of the project itself.

As the project grows, it would be easy for mathematical calculations, interpretation, and user-facing explanation to start bleeding into each other. Establishing those boundaries early gives later code a clearer place to belong.

## Quantum Core

The first implemented part of QubitLens is the quantum core.

At this stage it contains:

* standard single-qubit gate matrices
* an immutable pure-state representation
* utilities for embedding single-qubit gates into multi-qubit operators

The gate definitions currently cover the identity, Pauli-X, Pauli-Y, Pauli-Z, Hadamard, S, and T gates.

The state representation validates that a statevector is one-dimensional, has a non-zero power-of-two dimension, and is normalized. It also exposes the number of represented qubits and computational-basis measurement probabilities.

Operator construction embeds a single-qubit gate into a larger register while following the qubit-ordering convention QubitLens will rely on later.

These components are intentionally small. They're mathematical primitives that analysis code will eventually use to inspect quantum behavior, not the beginning of a separate circuit execution system.

## Execution Boundary

One of the most important decisions in Phase 0 was deciding what QubitLens should **not** implement.

Qiskit remains the quantum execution engine.

QubitLens can maintain mathematical representations and operations that are useful for understanding or verifying circuit behavior, but it doesn't need to reproduce Qiskit's ability to represent and execute complete quantum circuits.

Keeping that boundary firm reduces duplicated responsibility and gives me a mature external implementation to compare QubitLens against when integration behavior matters.

The relationship I want going forward is essentially:

```text
Qiskit executes quantum behavior
            ↓
QubitLens observes and structures it
            ↓
analysis determines what happened
            ↓
explanation communicates what happened
```

That keeps the project focused on inspection and understanding rather than simulation.

## Qubit Ordering

QubitLens follows Qiskit's little-endian computational-basis convention.

For a two-qubit register written as `|q1 q0⟩`, qubit 0 is the least-significant bit.

Applying `X` to `q0` therefore corresponds to:

```text
I ⊗ X
```

while applying `X` to `q1` corresponds to:

```text
X ⊗ I
```

This was worth establishing early because qubit ordering can be deceptive. An implementation can be mathematically consistent with itself while still disagreeing with the convention used by the execution engine.

That distinction became important when testing the operator implementation.

## Testing the Quantum Core

I added tests alongside the initial quantum core rather than waiting for the project to become larger.

The current tests cover:

* gate dimensions and complex-valued representations
* gate behavior on computational-basis states
* gate unitarity
* statevector construction
* qubit-count inference
* measurement probabilities
* complex amplitudes
* invalid state dimensions
* normalization requirements
* empty statevectors
* statevector ownership and copying
* multi-qubit operator dimensions
* operator unitarity
* target-qubit validation
* little-endian operator ordering

The tests are organized around responsibility rather than simply mirroring every future package directory.

Core behavior lives under:

```text
tests/core/
```

while behavior that needs to be verified against an external system lives under:

```text
tests/integration/
```

I want that distinction to remain useful as the project grows. A core test should be able to establish that QubitLens behaves according to its own mathematical contract without requiring Qiskit to prove every assertion.

Integration tests then answer the separate question of whether that contract agrees with the external system QubitLens is integrating with.

## Verifying Qubit Ordering Against Qiskit

The first operator tests established QubitLens's tensor-product ordering mathematically.

For example, they verify that targeting `q0` in a two-qubit register places the gate on the right tensor factor, while targeting `q1` places it on the left.

That establishes internal behavior, but it doesn't independently prove that the convention matches Qiskit.

A bug can be internally consistent.

So I added integration tests using Qiskit's `QuantumCircuit` and `Statevector` APIs. QubitLens constructs the full-system operator and evolves an initial state mathematically, while Qiskit independently represents the equivalent circuit operation and produces its own statevector.

The resulting statevectors are compared numerically.

The integration coverage currently checks X and Hadamard operations across different target qubits and also verifies the ordering inside a three-qubit register.

These tests are marked with pytest's registered `integration` marker so I can run them separately from the isolated core suite.

This established a testing principle I want to carry forward: when QubitLens depends on behavior at a Qiskit integration boundary, I should verify that behavior against Qiskit itself rather than only testing my interpretation of what Qiskit is supposed to do.

## Test Organization and Restoration

Once the initial foundation was working, I went back through the test suite specifically to check whether the tests were organized according to the architecture they were supposed to protect.

The structure was already mostly sound, so this didn't need a large rewrite.

One useful cleanup was separating the language of the core ordering tests from the Qiskit integration tests. The core tests now describe QubitLens's **little-endian ordering** directly instead of saying they "match Qiskit" even though those tests don't import or execute Qiskit.

That leaves two different responsibilities:

```text
core tests
    ↓
Does QubitLens satisfy its mathematical contract?

integration tests
    ↓
Does that contract agree with Qiskit?
```

I also added explicit coverage for an empty statevector. The implementation already rejected zero-length states as part of its non-zero power-of-two dimension requirement, but that side of the validation condition didn't have its own test.

After this pass, the full suite contains 40 tests.

## Verifying the Qiskit Dependency

By the time I reached the dedicated Qiskit integration checkpoint, much of the integration work already existed because it had been needed to establish the quantum core correctly.

Rather than adding another abstraction just to create new code for the checkpoint, I treated the existing integration as something to verify.

Qiskit is declared as a runtime dependency of QubitLens, and the integration tests exercise the actual Qiskit APIs used to verify operator ordering.

I also tested the project from a clean Python 3.11 virtual environment using only the package metadata:

```text
create fresh environment
        ↓
install QubitLens with development dependencies
        ↓
import QubitLens and Qiskit
        ↓
run integration suite
        ↓
run full suite
```

The clean installation successfully imported both packages, passed all five Qiskit integration tests, and passed the complete 40-test suite.

That gave me more confidence than relying only on the development environment I had already been using, because it checked that the repository itself contains enough dependency information to reproduce a working setup.

## Analysis and Explanation Boundary

Before either the analysis or explanation layer gets a real API, I established what each layer is supposed to own.

`core` remains the mathematical foundation and stays independent of the higher-level interpretation layers.

`analysis` will consume execution information and core representations to derive structured facts about circuit and state evolution.

`explanation` will consume those structured results and turn them into human-readable insights.

The intended dependency direction is:

```text
core
  ↑
analysis
  ↑
explanation
```

with explanation also allowed to use shared core representations directly where that makes sense.

The reverse dependencies are intentionally avoided:

* `core` does not depend on `analysis`
* `core` does not depend on `explanation`
* `analysis` does not depend on `explanation`

One thing I deliberately did **not** do here was create placeholder analysis interfaces or result classes before I actually know what the analysis layer needs.

It would be easy to create abstractions just because the package directories now exist, but that would mean designing Phase 1 APIs before implementing or learning from the problems those APIs are supposed to solve.

For now, the responsibility boundary is established. The concrete interfaces can emerge when the analysis work begins.

## Development Quality Tooling

Once the package structure and quantum core were established, I added automated development checks before the codebase became large enough for inconsistencies to accumulate.

The current quality pipeline uses:

* pytest for behavioral testing
* Ruff for formatting and linting
* mypy for static type checking
* GitHub Actions for clean-environment continuous integration

### Test Categorization

Tests that verify QubitLens directly against external integrations such as Qiskit use the registered pytest `integration` marker.

This allows the complete suite, integration suite, and non-integration suite to be run independently.

At the current Phase 0 checkpoint:

```text
full suite:         40 tests
integration suite:   5 tests
non-integration:    35 tests
```

The distinction isn't particularly expensive yet, but establishing it now should make the suite easier to manage once integration testing becomes larger and slower.

### Formatting and Linting

Ruff handles formatting and static linting.

I kept the initial linting rules relatively small: Python errors, Pyflakes checks, and import organization. I don't want the project spending more effort satisfying an aggressive style configuration than actually developing the architecture at this stage.

There is one intentional exception for the symbol `I`.

Generic linting rules consider `I` an ambiguous variable name, but in this project it represents the identity operator, where `I` is standard mathematical notation. I kept the domain notation and configured the lint rule accordingly.

### Static Type Checking

mypy checks the source package's type contracts.

One useful issue appeared when I first integrated it.

NumPy inferred a broader return type from `np.kron` than the `ComplexMatrix` type promised by QubitLens. The numerical result was correct and the behavioral tests passed, but the type checker exposed that the representation guarantee wasn't explicit in the implementation.

The operator construction now normalizes Kronecker-product results to `np.complex128`.

That was a useful example of why I don't want to treat static analysis as a substitute for testing or vice versa. The tests established that the mathematics behaved correctly, while the type checker found a problem in what the implementation promised about its representation.

## Continuous Integration

The GitHub Actions workflow reproduces the local quality checks in a fresh Linux environment.

The main quality job uses Python 3.11 and runs:

```text
Ruff linting
Ruff formatting
mypy
pytest
```

Python 3.11 is also the minimum Python version QubitLens currently supports, so this job acts as the main quality gate.

Python 3.12 is checked separately as a runtime compatibility job using the full test suite.

The workflow wasn't originally split this way.

My first version ran the entire quality pipeline across both Python versions. That exposed an interaction between the Python version mypy was intentionally configured to analyze and syntax used by NumPy's type stubs in the Python 3.12 environment.

Instead of weakening the Python 3.11 type contract just to make the CI matrix uniform, I separated the responsibilities:

```text
Python 3.11
    ↓
lint + format + types + tests

Python 3.12
    ↓
runtime compatibility tests
```

That structure better represents what each job is actually proving.

It also gives me an additional environment check because my local development happens on Windows while CI runs on Linux.

## Phase 0 Status

At this point, the main Phase 0 foundation is in place:

* the repository is structured as an installable Python package
* the quantum core provides the mathematical primitives needed by later work
* QubitLens follows a tested little-endian qubit convention
* Qiskit remains clearly separated as the execution engine
* the Qiskit integration boundary has been independently verified
* the test suite is organized around core and integration responsibilities
* formatting, linting, static typing, and tests form a repeatable quality gate
* CI verifies both the minimum supported Python version and Python 3.12 compatibility
* the responsibilities and dependency direction of `core`, `analysis`, and `explanation` are explicitly defined

Phase 0 is complete.

The final verification pass confirmed the full 40-test suite, the isolated core
and Qiskit integration suites, Ruff formatting and linting, mypy type checking,
package metadata, repository hygiene, and a clean working tree. The project was
also previously verified from a fresh Python 3.11 environment using only its
declared package and development dependencies.

With those checks passing, the foundation is ready to freeze. Further
development can now build on the established core, Qiskit execution boundary,
testing infrastructure, quality gates, and analysis/explanation architecture
rather than continuing to change the project foundation.
