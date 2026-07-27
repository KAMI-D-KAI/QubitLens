# QubitLens

QubitLens is an interactive quantum circuit analysis, explanation, and visualization tool built on top of Qiskit.

The project aims to make quantum circuits easier to inspect and understand by exposing how a circuit evolves step by step and turning execution data into structured analysis that can power explanations, visualizations, exports, and interactive learning tools.

QubitLens does not aim to replace Qiskit or implement a separate quantum simulator. It provides its own analysis-oriented domain and mathematical foundations while relying on Qiskit for mature quantum execution.

## Project Status

QubitLens is currently in early development.

The Phase 0 foundation is complete. It established the package architecture, mathematical quantum core, Qiskit execution boundary, testing strategy, development quality tooling, and continuous integration.

Development is now focused on the quantum-domain foundation needed to represent circuits and their configuration before the analysis layer is built.

The current circuit-domain model provides immutable representations for:

* quantum circuits and their ordered operations
* gate applications with targets, controls, and parameters
* measurements from qubits into classical bits
* structural and circuit-relative validation

Gate-specific definitions and configurable initial-state representation are planned as the next parts of the quantum-domain foundation.

## Architecture

QubitLens separates the major responsibilities involved in understanding a quantum circuit:

* **Core** provides shared mathematical and quantum foundations.
* **Domain** represents QubitLens concepts such as circuits, gate applications, and measurements.
* **Qiskit** provides quantum execution and state evolution.
* **Analysis** will convert circuit execution into structured information about what happens at each step.
* **Explanation** will convert structured analysis into human-readable insights.
* **Visualization and export** will consume the same underlying domain and analysis information for interactive and shareable outputs.

The intended flow is:

```text
QubitLens domain
      ↓
Qiskit execution
      ↓
QubitLens analysis
      ↓
explanation / visualization / export
```

This separation keeps QubitLens focused on inspection and understanding rather than duplicating the responsibilities of a quantum SDK.

For a more detailed description of the responsibility and dependency boundaries, see `docs/architecture.md`.

## Current Domain API

Circuit-domain models are available through `qubitlens.domain`:

```python
from qubitlens.domain import Circuit, GateOperation, Measurement
```

For example:

```python
from qubitlens.domain import Circuit, GateOperation, Measurement

circuit = Circuit(
    num_qubits=2,
    operations=(
        GateOperation(gate="h", targets=(0,)),
        GateOperation(gate="cx", targets=(1,), controls=(0,)),
        Measurement(qubit=1, classical_bit=0),
    ),
)
```

The domain model describes circuit structure but does not execute the circuit. Execution remains the responsibility of the Qiskit integration boundary.

## Development

QubitLens currently targets Python 3.11 and 3.12.

Create and activate a virtual environment, then install the project in editable development mode:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

Run the full test suite:

```bash
pytest -q
```

Run only the Qiskit integration tests:

```bash
pytest -m integration -q
```

Run the local quality checks:

```bash
ruff check src tests
ruff format --check src tests
mypy src
pytest -q
```

GitHub Actions runs the main quality pipeline on Python 3.11 and separately verifies runtime compatibility on Python 3.12.

## Documentation

Project architecture and development decisions are documented under `docs/`.

* `docs/architecture.md` describes the current QubitLens architecture and responsibility boundaries.
* `docs/phase-0-foundation.md` records the completed Phase 0 foundation.
* `docs/phase-1-quantum-domain-foundation.md` records the ongoing Phase 1 quantum-domain work.

## License

QubitLens is licensed under the MIT License.
