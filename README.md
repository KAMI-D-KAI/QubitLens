# QubitLens

> **See the math inside a quantum circuit.**
> Build a circuit → run it → watch it evolve → stop anywhere → inspect the state → understand the math → verify it → export/share it.

QubitLens is an interactive quantum circuit builder and state-evolution explorer. Qiskit is the quantum engine underneath; QubitLens is the representation, analysis, explanation, visualization, and UX layer on top, designed to make the mathematics of a circuit understandable **gate by gate**.

---

## Roadmap

A checked box means the capability lives in the current codebase and is covered by tests.

### Foundation
- [x] Installable Python package with a clean `src/` layout
- [x] Immutable numerical quantum core (statevectors, gate matrices, operator construction)
- [x] Explicit little-endian, Qiskit-compatible qubit ordering
- [x] Qiskit set up as the reference execution engine
- [x] CI on Python 3.11 (dev) and 3.12, with Ruff, mypy, and pytest gates
- [x] Reserved architectural boundaries for analysis and explanation

### Quantum domain
- [x] Immutable circuit, operation, and initial-state model
- [x] Gate catalogue with display metadata and catalogue-aware validation
- [x] Configurable pure initial states with complex amplitudes
- [x] Default `|0…0⟩` initialisation and full structural validation

### Mathematical input *(current work)*
- [x] Safe expression engine parse and evaluate real/complex maths with **no** arbitrary code execution
- [ ] Named parameter variables (`theta`, `phi`, …) with safe binding at evaluation time
- [ ] Scientific state input from full vectors, basis-state dicts, or sparse dicts, with symbolic amplitudes

### Execution & tracing
- [ ] Qiskit-backed statevector execution with explicit little-endian semantics
- [ ] Operation-by-operation state evolution: `|ψ₀⟩ → |ψ₁⟩ → |ψ₂⟩ → …` as first-class checkpoints

### Visual experience
- [ ] Web-based circuit builder (React + FastAPI adapter) 1–10 qubits, drag-and-drop gates, controls/targets, parameter form, measurements
- [ ] Playable simulation: play/pause/step, clickable checkpoints, adjustable speed, active-gate highlighting
- [ ] Structured, depth-adjustable explanations for every gate step

### Analysis, measurement, export
- [ ] Measurement lab: analytic probabilities, seeded shot sampling, side-by-side comparison
- [ ] Circuit and state analysis: depth, entropy, entanglement entropy, entangling-step locator
- [ ] Export to runnable Qiskit Python, PNG/SVG diagrams, or ASCII
- [ ] Export animated walk-throughs of any circuit (GIF / MP4)

### Polish & ship
- [ ] Keyboard-navigable, screen-reader-labeled, color-blind-safe UI with hard/soft qubit budgets
- [ ] Package release, live-hosted demo, and public documentation

---

## Where we are right now

The **quantum foundation** and **quantum domain** are complete and locked down by 128 passing tests. Active work is on the **mathematical input** system: turning human-typed maths into validated QubitLens values without ever running user code as Python.

Once mathematical input closes, the next milestones are Qiskit-backed execution and the operation-by-operation trace engine, which together unlock the visual experience.

---

## Vision

QubitLens should make the invisible mathematical process inside a quantum circuit **inspectable**. A user should be able to move from

**circuit diagram → operation → state transformation → mathematical explanation → verification → export**

without needing to reconstruct the computation manually or write a Qiskit program first. The finished product connects visual intuition, mathematical understanding, correct quantum execution, and reusable/shareable output in one coherent system.

---

## Architecture at a glance

```
Visual UI  ──┐
             ├──►  Shared QubitLens application layers
CLI       ──┘

┌─────────────────────────────┐
│ User interfaces             │
├─────────────────────────────┤
│ Mathematical input          │  ← safe expression engine, parameters, states
├─────────────────────────────┤
│ Circuit domain              │  ← immutable circuits, operations, initial states
├─────────────────────────────┤
│ Qiskit execution            │  ← statevector run, little-endian at the boundary
├─────────────────────────────┤
│ Trace engine                │  ← |ψ₀⟩ → |ψ₁⟩ → … checkpoints
├─────────────────────────────┤
│ Analysis · Explanation · Visualization │
├─────────────────────────────┤
│ Export & presentation       │  ← Qiskit source, diagrams, animations
└─────────────────────────────┘
```

Qiskit is used as the execution and reference layer; QubitLens does not attempt to reimplement it. Everything the user sees. the builder, the checkpoints, the explanations, the exports — lives above Qiskit and passes through QubitLens's own semantic model.

---

## Development

```bash
# create a venv, then:
pip install -e ".[dev]"

# quality gate
ruff check .
ruff format --check .
mypy
pytest -q

# Qiskit-touching integration tests
pytest -m integration -q
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — layers, responsibilities, conventions
- [`docs/journey.md`](docs/journey.md) — the engineering story behind each capability *(coming soon)*
- [`docs/api.md`](docs/api.md) — public Python API reference *(coming soon)*

## License

MIT — see [LICENSE](LICENSE).
