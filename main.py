"""
main.py – Entry point for the LPG Monitoring Agent prototype.
Run with:  python main.py
"""
from simulation.runner import run_simulation


def main() -> None:
    """Run continuous single-agent simulation.

    The loop inside `run_simulation` follows:
    perceive -> update beliefs -> decide -> act
    for a fixed number of simulated days.
    """
    run_simulation(days=30)


if __name__ == "__main__":
    main()
