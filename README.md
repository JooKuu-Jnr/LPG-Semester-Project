# LPG Monitoring Intelligent Agent Prototype

The agent monitors simulated household LPG cylinder weight, estimates gas remaining, predicts depletion, and issues warning actions before gas runs out.

## Project Structure
```
main.py                    # Entry point
design/                    # Prometheus design notes/artifacts
src/                       # Agent modules (percepts, beliefs, capabilities, plans, actions)
simulation/                # Simulated household LPG environment + scenario runner
config/                    # Constants and thresholds
tests/                     # Lightweight pytest tests
requirements.txt           # Minimal dependencies
```

## Setup
1. Open the project in GitHub Codespaces (or any Python 3.10+ environment).
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

Note: Runtime uses the Python standard library. `pytest` is optional for tests.

## Run the Simulation
```bash
python main.py
```

This runs all predefined scenarios from one command.

## Prototype Behaviors Demonstrated
- Normal household LPG usage monitoring
- Low gas warning behavior
- Critical gas warning behavior
- Refill detection and prediction-state reset
- Usage pattern change handling over time

Console output is labeled by agent stages: `PERCEIVE`, `BELIEF`, `DECIDE`, and `ACT`.