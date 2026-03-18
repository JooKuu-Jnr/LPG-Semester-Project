"""Simulation runner.

Coordinates environment progression and agent monitor cycles.
Only LPGMonitorAgent is an agent in this project; environment and user
are treated as non-agent external entities.
"""
from config.constants import CRITICAL_GAS_KG
from simulation.environment import HouseholdLPGEnvironment
from src.agent import LPGMonitorAgent


def _align_agent_with_environment(agent: LPGMonitorAgent, env: HouseholdLPGEnvironment) -> None:
    """Initialize agent baseline beliefs to the current environment state.

    This avoids a false refill event at scenario start and keeps the
    simulation focused on meaningful transitions.
    """
    snapshot = env.get_state_snapshot()
    agent.beliefs.current_cylinder_weight_kg = snapshot["current_cylinder_weight_kg"]
    agent.beliefs.estimated_gas_remaining_kg = snapshot["gas_remaining_kg"]


def _run_agent_step(agent: LPGMonitorAgent, percept, step_label: str) -> None:
    """Run one explicit Perceive -> Decide -> Act step with printed trace.

    - Perceive: show percept values from environment.
    - Decide: show selected plan/actions.
    - Act: execute and print action outputs from action layer.
    """
    print(f"\n{step_label}")

    # PERCEIVE
    print(
        "[PERCEIVE] "
        f"weight_reading={percept.gross_weight_kg:.2f} kg | "
        f"timestamp={percept.timestamp.strftime('%Y-%m-%d')}"
    )
    agent.perceive(percept)

    # DECIDE
    action_names = agent.decide(percept)

    # BELIEF (after decide, because plan updates beliefs in this stage)
    print(
        "[BELIEF]   "
        f"weight={agent.beliefs.current_cylinder_weight_kg:.2f} kg | "
        f"gas_est={agent.beliefs.estimated_gas_remaining_kg:.2f} kg | "
        f"avg_use={agent.beliefs.average_consumption_kg_per_day:.2f} kg/day | "
        f"days_left={agent.beliefs.predicted_days_remaining:.2f}"
    )

    print(
        "[DECIDE] "
        f"plan={agent.selected_plan_name} | "
        f"decision={action_names if action_names else ['none']}"
    )

    # ACT
    print(f"[ACT]      executing={action_names if action_names else ['none']}")
    agent.act(action_names)


def run_continuous_loop(days: int = 30) -> None:
    """Run a continuous single-agent loop for a fixed number of days.

    Prometheus mapping:
    - Perceive: read daily weight percept from environment.
    - Decide: update beliefs and choose actions through plans.
    - Act: execute warning/log/reset actions.

    This is the default project execution path for `python main.py`.
    """
    # Start below full capacity so a 30-day demo reliably reaches warning and
    # refill conditions while still using the same agent logic.
    env = HouseholdLPGEnvironment(initial_gas_kg=6.0)
    agent = LPGMonitorAgent()
    _align_agent_with_environment(agent, env)

    print("=" * 52)
    print("   LPG Monitoring Agent  -  Continuous Run")
    print("=" * 52)

    for day in range(1, days + 1):
        # Simulate one day of household usage.
        usage_today_kg = env.sample_daily_usage()
        percept = env.step(usage_kg=usage_today_kg)

        print(f"\nDAY {day}")
        print(
            "[PERCEIVE] "
            f"weight_reading={percept.gross_weight_kg:.2f} kg | "
            f"daily_usage={usage_today_kg:.2f} kg"
        )

        # Perceive -> Decide
        agent.perceive(percept)
        action_names = agent.decide(percept)

        print(
            "[BELIEF]   "
            f"weight={agent.beliefs.current_cylinder_weight_kg:.2f} kg | "
            f"gas_est={agent.beliefs.estimated_gas_remaining_kg:.2f} kg | "
            f"avg_use={agent.beliefs.average_consumption_kg_per_day:.2f} kg/day | "
            f"days_left={agent.beliefs.predicted_days_remaining:.2f}"
        )
        print(
            "[DECIDE] "
            f"plan={agent.selected_plan_name} | "
            f"decision={action_names if action_names else ['none']}"
        )

        # Act
        print(f"[ACT]      executing={action_names if action_names else ['none']}")
        agent.act(action_names)

        # Auto-refill behavior when gas reaches critical threshold.
        if env.gas_remaining_kg <= CRITICAL_GAS_KG:
            env.trigger_refill()
            state = env.get_current_state()

            # Keep belief state consistent with environment after refill.
            agent.actions.record_refill_event(agent.beliefs, state["current_cylinder_weight_kg"])
            agent.actions.reset_prediction_state_after_refill(agent.beliefs)
            agent.actions.update_internal_state(
                agent.beliefs,
                {
                    "estimated_gas_remaining_kg": state["gas_remaining_kg"],
                    "current_cylinder_weight_kg": state["current_cylinder_weight_kg"],
                },
            )

    final_state = env.get_current_state()
    print("\n" + "=" * 52)
    print("   Continuous Run Summary")
    print("=" * 52)
    print(f"Total days simulated: {days}")
    print(f"Number of refills: {final_state['refill_count']}")
    print(
        "Final gas state: "
        f"gas_remaining={final_state['gas_remaining_kg']:.2f} kg | "
        f"current_weight={final_state['current_cylinder_weight_kg']:.2f} kg"
    )


def run_normal_usage_scenario() -> None:
    """Scenario 1: Normal household LPG use.

    Design link:
    - Supports Goal G1 (monitoring) and baseline scenario in design notes.
    """
    print("\n" + "=" * 70)
    print("SCENARIO 1: Normal Household LPG Use")
    print("=" * 70)
    env = HouseholdLPGEnvironment(initial_gas_kg=8.0, daily_usage_kg=0.20)
    agent = LPGMonitorAgent()
    _align_agent_with_environment(agent, env)

    for day in range(1, 6):
        percept = env.step()
        _run_agent_step(agent, percept, f"--- Normal Use Day {day} ---")


def run_low_gas_warning_scenario() -> None:
    """Scenario 2: Low gas warning.

    Design link:
    - Supports Goal G3 (alert before depletion).
    """
    print("\n" + "=" * 70)
    print("SCENARIO 2: Low Gas Warning")
    print("=" * 70)
    env = HouseholdLPGEnvironment(initial_gas_kg=2.0, daily_usage_kg=0.60)
    agent = LPGMonitorAgent()
    _align_agent_with_environment(agent, env)

    for day in range(1, 4):
        percept = env.step()
        _run_agent_step(agent, percept, f"--- Low Gas Check Day {day} ---")


def run_critical_gas_warning_scenario() -> None:
    """Scenario 3: Critical gas warning near depletion.

    Design link:
    - Supports Goal G3 critical alert behavior.
    """
    print("\n" + "=" * 70)
    print("SCENARIO 3: Critical Gas Warning")
    print("=" * 70)
    env = HouseholdLPGEnvironment(initial_gas_kg=CRITICAL_GAS_KG + 0.10, daily_usage_kg=0.20)
    agent = LPGMonitorAgent()
    _align_agent_with_environment(agent, env)

    percept = env.step()
    _run_agent_step(agent, percept, "--- Critical Gas Check ---")


def run_refill_reset_scenario() -> None:
    """Scenario 4: Refill event and prediction reset.

    Design link:
    - Supports Goal G4 (record refill and reset baseline state).
    """
    print("\n" + "=" * 70)
    print("SCENARIO 4: Refill / Reset Event")
    print("=" * 70)
    env = HouseholdLPGEnvironment(initial_gas_kg=2.5, daily_usage_kg=0.50)
    agent = LPGMonitorAgent()
    _align_agent_with_environment(agent, env)

    # Deplete for a short period.
    percept = env.step()
    _run_agent_step(agent, percept, "--- Before Refill: Day 1 ---")
    percept = env.step()
    _run_agent_step(agent, percept, "--- Before Refill: Day 2 ---")

    # Trigger refill event and allow agent to perceive the sudden weight increase.
    env.trigger_refill()
    refill_percept = env.generate_weight_reading()
    _run_agent_step(agent, refill_percept, "--- Refill Event Perceived ---")


def run_usage_pattern_change_scenario() -> None:
    """Scenario 5: Changing usage pattern over time.

    Design link:
    - Supports Goal G2 and Scenario 2 (sudden higher usage pattern).
    """
    print("\n" + "=" * 70)
    print("SCENARIO 5: Usage Pattern Change Over Time")
    print("=" * 70)
    env = HouseholdLPGEnvironment(initial_gas_kg=10.0, daily_usage_kg=0.20)
    agent = LPGMonitorAgent()
    _align_agent_with_environment(agent, env)

    # Baseline period
    for day in range(1, 4):
        percept = env.step()
        _run_agent_step(agent, percept, f"--- Baseline Usage Day {day} ---")

    # Increased usage period (e.g., guests/festive cooking)
    env.set_daily_usage_pattern(0.60)
    for day in range(4, 7):
        percept = env.step()
        _run_agent_step(agent, percept, f"--- High Usage Day {day} ---")


def run_simulation(days: int = 30) -> None:
        """Run the default simulation entry point.

        Important:
        - This now runs the continuous single-agent loop.
        - Scenario helper functions remain in this module for optional demos,
            but they are not executed in the default flow.
    """
        run_continuous_loop(days=days)
