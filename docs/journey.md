# The QubitLens Journey

*A curated engineering-and-learning narrative. Read this to understand not just what QubitLens is, but why every piece looks the way it does.*

Each section follows the same four-beat structure:

- **Problem**   the concrete thing the project could not yet do.
- **Concept**   the piece of physics, math, or engineering that had to be understood before writing a line of code.
- **Design & implementation**   the shape of the solution, without turning into a code listing.
- **Learning**   what the author will carry forward from this step.

---

## 1. Why QubitLens exists

A quantum circuit diagram is a wonderful lie. It looks like a small pipeline, but underneath, the state is a complex vector living in a `2ⁿ`-dimensional space, and *every* wire in the diagram is entangled with every other wire once a two-qubit gate touches them. The diagram compresses this away.

The problem is not that quantum mechanics is unlearnable. The problem is that most tools show either the diagram (readable but silent about the math) or the raw statevector (mathematically honest but unreadable). Nothing in between.

QubitLens exists to occupy that in-between space: a system where a learner can build a circuit visually, run it, stop at any point, and see the *actual mathematical state* along with an explanation of why it changed. Qiskit is the ground truth for execution; QubitLens is the layer that turns Qiskit's answers into an inspectable narrative.

---

## 2. Building a foundation that could carry the rest of the project

### Problem

Before any pretty visualisation could exist, the project needed a numerical core that was:
- correct on every simple statement of linear algebra,
- deterministic to test against,
- immutable, so nothing downstream could accidentally corrupt a state,
- and Qiskit-compatible in its *conventions* (particularly qubit ordering) even before Qiskit was actually used as an engine.

### Concept the two conventions that trip everyone up

Two things about representing qubits are worth internalising before writing code:

1. **A pure state on `n` qubits is a complex vector of length `2ⁿ`, normalised to unit ℓ²-norm.** The `k`-th entry is the amplitude of the computational basis state whose bit-pattern equals `k`.
2. **Which bit is qubit 0?** There are two conventions. QubitLens (like Qiskit) uses **little-endian**: the *least-significant* bit of the basis-state index is qubit 0. So on two qubits, index `1 = 01ₐ` means "qubit 0 is `|1⟩`, qubit 1 is `|0⟩`". Big-endian conventions swap this; almost every subtle bug in a quantum-visualisation tool traces back to mixing the two.

Once you accept these two facts, everything else in the core follows.

### Design & implementation

The foundation is an installable `src/`-layout Python package. Its lowest layer, `qubitlens.core`, owns three tiny things:

- gate matrices as immutable numpy arrays,
- a `PureState` primitive that stores a complex-128 amplitude vector, validates length and normalisation on construction, and refuses in-place mutation,
- a helper that lifts a single-qubit gate into a full `2ⁿ × 2ⁿ` operator with **explicit little-endian** semantics.

Everything is tested against hand-computed references (`H|0⟩`, `X|0⟩`, `CX|10⟩`) *and* against Qiskit's `Statevector` on the same circuits, precisely to prove the two conventions agree.

Around this core, the repository grew a full quality gate: Ruff for style, mypy for types, pytest for behaviour, GitHub Actions for CI, and a marker system that keeps Qiskit-touching tests separate from the fast unit-test path.

### Learning

The most valuable thing this phase taught me was **that "just testing" is not the same as "testing invariants".** A test that says *"H|0⟩ produces this exact array"* is fine. A test that says *"H⊗I applied to |00⟩ still normalises to 1 and matches Qiskit"* is much more powerful, because it locks the convention *and* the math *and* the boundary with the reference engine in one assertion.

I also learned that establishing quality tooling (Ruff/mypy/CI) at the start feels slow but pays back within a week. Every subsequent commit has a working "does this still lint / type / test" answer in seconds.

---

## 3. Making circuits and states first-class objects

### Problem

Once the numerical core existed, I still couldn't say *"here is a circuit"* in the codebase. There was no notion of a gate operation with targets and controls, no notion of an initial state configurable to something other than `|0…0⟩`, and no way to validate *before running anything*  that "apply CX to qubit 3 on a 2-qubit circuit" is nonsense.

Every subsequent layer (execution, tracing, explanation, visualisation) needs to consume validated, self-describing circuit objects. Building those objects properly here saves that layer from re-implementing validation.

### Concept a circuit as ordered semantics, not as a matrix

There's a temptation to think of a circuit as *"the big unitary you get by multiplying all its gates in the right order"*. Mathematically true; operationally useless. If you flatten a circuit into a matrix, you throw away the very thing QubitLens exists to expose: **the intermediate states**. A checkpoint like `|ψ₂⟩` doesn't exist inside a monolithic matrix; it only exists if the circuit is stored as an ordered sequence of operations.

So the domain model treats a `Circuit` as *"a qubit count plus an ordered tuple of `Operation`s"*, and treats an `Operation` as *"a gate name plus its targets, controls, and parameters"*. Nothing more. No matrices, no statevectors those live in the numerical core.

### Design & implementation

Two clean layers appeared:

- **Circuit domain (`qubitlens.domain`)**   `Circuit`, `Operation`, `Measurement`, `InitialState`, all frozen dataclasses. A `Circuit` grows by returning a new `Circuit` from `.append_gate(...)` never by mutation. Validation happens on construction: gate names must exist in the catalogue, qubit indices must be in range, parameter counts must match the catalogue's declaration.
- **Gate catalogue** a data-only registry of every supported gate with its display name, target/control/parameter counts. This is intentionally separate from the numerical matrices, because the *domain* only needs to know structural facts ("CX has one control and one target"), not the underlying matrix. The matrix lookup lives in the core.
- **Initial state model**  `InitialState` wraps a complex amplitude vector. It validates length (`2ⁿ`), finiteness (no `NaN`/`inf`), and normalisation. `InitialState.zero(n)` is the convenience constructor for the canonical `|0…0⟩`. Every downstream layer that "needs a starting state" takes an `InitialState`; nothing takes a raw numpy array.

### Learning

Freezing everything (`@dataclass(frozen=True)`) turned out to be more than aesthetic. It made testing dramatically simpler: because a `Circuit` can never mutate, any test can reason about *"the circuit passed in"* without worrying that a helper somewhere squirreled away a reference and modified it. This is why almost every test in the codebase reads like a mathematical claim rather than a stateful sequence.

The other lesson: **let the domain and the numerics be different things.** The domain describes what the user asked for; the numerics describe what happens when you execute it. Keeping them in different modules made every subsequent question ("where does execution live?" "where does explanation live?") answer itself.

---

## 4. Accepting human mathematics without running human code

### Problem

Quantum states and gate parameters are described mathematically: `1/sqrt(2)`, `exp(i*pi/4)`, `cos(theta/2)`. The natural way to accept them from a user is as a string. The naïve way to evaluate that string is `eval(...)`. The naïve way is a disaster: a user (or a shared circuit, or a malicious payload) can then run *arbitrary Python*: file access, network calls, subprocess spawns, everything.

At the same time, the mathematical surface needed is genuinely non-trivial: complex numbers, transcendentals, parenthesised sub-expressions, negative exponents. So the answer can be neither "accept everything" nor "accept only a fixed list of literals".

### Concept Python's own AST as a security surface

Python provides `ast.parse(source, mode="eval")`, which returns a syntax tree of the expression **without executing it**. This is the leverage point. If I walk that tree and refuse any node type I did not explicitly bless, I can guarantee no name lookup, no attribute access, no function call, no comprehension, and no lambda ever runs regardless of how devious the input is. Python provides `ast.parse(source, mode="eval")`, which returns a syntax tree of the expression **without executing it**. This is the leverage point. If I walk that tree and refuse any node type I did not explicitly bless, I can prevent unsupported Python constructs from crossing the input boundary. Once the tree is validated, QubitLens recursively interprets only the mathematical nodes and whitelisted names it explicitly supports.

This turns "safe evaluation" from a fuzzy problem into a *whitelist* problem: list the allowed AST node classes, list the allowed identifiers, list the allowed functions. Anything not on those three lists is rejected at the boundary.

### Design & implementation

The Safe Expression Engine sits under `qubitlens.input.expression`. Its public API is one function, `evaluate(expression: str) -> complex`, and one exception hierarchy rooted at `InputError`. Internally the pipeline is:

1. reject inputs longer than a hard limit (length DoS),
2. parse with `ast.parse(..., mode="eval")`, translating any `SyntaxError` into `ExpressionSyntaxError`,
3. enforce structural resource limits on AST depth and total node count,
4. reject any node whose class is not in the allowed set (`Expression`, `BinOp`, `UnaryOp`, `Constant`, `Name`, `Call`, `Load`, and a small set of numeric operators),
5. validate numeric literals, names, direct function calls, argument structure, and exponent limits,
6. recursively interpret the validated AST using QubitLens's own evaluator, with explicit handling for literals, constants, binary arithmetic, unary arithmetic, and whitelisted function calls,
7. verify the resulting complex value is finite (`NaN`/`inf` becomes `NonFiniteResultError`),
8. return a `complex`.

The whitelist is a data-only module. Adding a new capability to the mini-language is intentionally a two-step change: add the name/function to the whitelist *and* extend the tests. Reviewers see both diffs; nothing sneaks in.

### Learning

This phase reshaped how I think about "safe evaluation" more than any other. Three things stuck:

1. **Parsing is safer when execution semantics are owned explicitly.** `ast.parse(..., mode="eval")` lets QubitLens inspect user mathematics without executing it, and interpreting only the node types we explicitly support keeps the mini-language separate from Python's general execution machinery.
2. **Resource limits matter as much as capability limits.** A whitelist that allows `2**10**10` is a whitelist that allows a denial-of-service. Every allowed operator needs a cost story.
3. **Errors are UX.** Splitting failure into `ExpressionSyntaxError`, `DisallowedNameError`, `DisallowedNodeError`, `ResourceLimitError`, `NonFiniteResultError` (and later `UnboundParameterError`, `InvalidParameterNameError`) means the eventual UI can say *"the character `@` is not allowed"* instead of a generic *"invalid input"*. Structured errors here mean better messages three layers up.

---

## 5. Where the story picks up next

The foundation, the domain, and safe human-math input now exist. The next chapters of this journey parameter variables and scientific state input will finish the input boundary. After that the tale shifts from *"can we describe circuits correctly?"* to *"can we execute and inspect them faithfully?"*, and the pieces start to visibly connect: an initial state and a circuit go into a runner, an ordered sequence of intermediate states comes out, and every one of those states becomes a checkpoint the user can click on.

The pattern established here **problem → concept → design → learning**   will repeat in each of those chapters. The goal is that a reader who reaches the end of this document not only understands what QubitLens does, but also has a small library of transferable ideas: AST-as-security-surface, immutable domain modelling, "let the reference engine be the reference", and   perhaps most importantly the discipline of separating *what the user asked for* from *what happens when you compute it*.
