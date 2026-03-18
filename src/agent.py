"""Agent module.

Defines a single LPG intelligent agent that coordinates:
percepts, beliefs, capabilities, plans, and actions.

Single-agent rationale:
- One household cylinder scenario requires one decision-maker.
- Monitoring, prediction, and notification are performed internally
    by this same agent in one control loop.
- Environment and user are external entities, not agents.
"""
from config.constants import (
    CYLINDER_TARE_WEIGHT_KG,
    DEFAULT_DAILY_USAGE_KG,
)
from src.actions import AgentActions
from src.beliefs import AgentBeliefs
from src.capabilities import LPGAgentCapabilities
from src.percepts import WeightReading
from src.plans import MonitorCyclePlan


class LPGMonitorAgent:
    """Single-agent controller for household LPG monitoring.

    Internal responsibilities:
    1) Monitoring percepts
    2) Predicting depletion
    3) Deciding notifications/actions
    """

    def __init__(self) -> None:
        self.beliefs = AgentBeliefs(
            current_cylinder_weight_kg=CYLINDER_TARE_WEIGHT_KG,
            estimated_gas_remaining_kg=0.0,
            average_consumption_kg_per_day=DEFAULT_DAILY_USAGE_KG,
        )
        self.capabilities = LPGAgentCapabilities()
        self.plan = MonitorCyclePlan()
        self.plans = {
            "monitor_cycle": self.plan,
        }
        self.actions = AgentActions()
        self._last_action_context: dict = {"beliefs": self.beliefs}
        self._selected_plan_name: str = "monitor_cycle"

    def perceive(self, percept: WeightReading) -> None:
        """Perceive stage: receive environment percept for current cycle.

        - This is the event/percept intake point from the environment model.
        """
        _ = percept

    def _select_plan(self, percept: WeightReading) -> MonitorCyclePlan:
        """Decide which plan should run for the current percept.

        For this prototype we intentionally keep one primary plan:
        `monitor_cycle`. This still makes the decision step explicit.
        """
        _ = percept
        self._selected_plan_name = "monitor_cycle"
        return self.plans[self._selected_plan_name]

    def decide(self, percept: WeightReading) -> list[str]:
        """Decide stage: choose plan, update beliefs, and produce action names.

        - Plan selection + reasoning happen here.
        - Belief updates occur through capabilities called by the selected plan.
        """
        selected_plan = self._select_plan(percept)
        action_names = selected_plan.run(self.capabilities, self.beliefs, percept)
        self._last_action_context = selected_plan.last_action_context
        return action_names

    def act(self, action_names: list[str]) -> None:
        """Act stage: execute actions selected by the plan.

        Prometheus mapping:
        - This applies effectors/actions (alerts, logs, state reset).
        """
        for action_name in action_names:
            self.actions.dispatch(action_name, self._last_action_context)

    def run_cycle(self, percept: WeightReading) -> None:
        """Run one explicit Perceive -> Decide -> Act control loop.

        Stage 1 (Perceive): accept environment percept.
        Stage 2 (Decide): select plan and derive actions from beliefs.
        Stage 3 (Act): execute resulting actions.
        """
        # 1) PERCEIVE: capture the latest environmental input.
        self.perceive(percept)

        # 2) DECIDE: run plan logic (includes belief update + action selection).
        chosen_actions = self.decide(percept)

        # 3) ACT: perform each selected action.
        self.act(chosen_actions)

    @property
    def avg_daily_usage(self) -> float:
        """Backward-compatible alias for tests and early prototype code."""
        return self.beliefs.average_consumption_kg_per_day

    @property
    def gas_remaining(self) -> float:
        """Backward-compatible alias for tests and early prototype code."""
        return self.beliefs.estimated_gas_remaining_kg

    @gas_remaining.setter
    def gas_remaining(self, value: float) -> None:
        self.beliefs.estimated_gas_remaining_kg = value

    @property
    def days_remaining(self) -> float:
        """Backward-compatible alias for tests and early prototype code."""
        return self.beliefs.predicted_days_remaining

    @days_remaining.setter
    def days_remaining(self, value: float) -> None:
        self.beliefs.predicted_days_remaining = value

    @property
    def selected_plan_name(self) -> str:
        """Public read-only view of current selected plan name."""
        return self._selected_plan_name
