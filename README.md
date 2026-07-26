# QubitLens

QubitLens is an interactive quantum circuit analysis, explanation, and visualization tool built on top of Qiskit.

The project aims to make quantum circuits easier to inspect and understand by exposing how a circuit evolves step by step, turning execution data into structured analysis that can later power explanations, visualizations, and interactive learning tools.

## Project Status

QubitLens is currently in early development.

The initial development phase focuses on establishing the core architecture and integrating Qiskit as the quantum execution engine.

## Architecture

QubitLens is designed around a separation of responsibilities:

- **Qiskit** provides quantum circuit representation and state evolution.
- **Core** contains shared quantum and mathematical foundations used by QubitLens.
- **Analysis** converts circuit execution into structured information about what happens at each step.
- **Explanation** converts structured analysis into human-readable insights.
- **Visualization** will present circuit evolution and analysis interactively.

QubitLens does not aim to replace Qiskit or implement a separate quantum simulator.

## Development

QubitLens currently targets Python 3.11 and 3.12.

Create and activate a virtual environment, then install the project in editable development mode:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```
Run the test suite with:
```bash pytest ```
