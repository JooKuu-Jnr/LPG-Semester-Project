"""Plans module (Prometheus: plans).

Encodes the ordered Perceive -> Decide -> Act behavior for one cycle.
No inter-agent coordination is required because this project is single-agent.
"""
from config.constants import CRITICAL_GAS_KG, LOW_GAS_DAYS_THRESHOLD, REFILL_DELTA_KG, USAGE_HISTORY_WINDOW
from src.beliefs import AgentBeliefs
from src.capabilities import LPGAgentCapabilities
from src.percepts import WeightReading


class MonitorCyclePlan:
    """Single-agent plan executed for each new percept.

    This plan captures all core decisions internally:
    monitor -> predict -> choose notifications.
    """

    def __init__(self) -> None:
        self.last_action_context: dict = {}

    def process_weight_update(
        self,
        capabilities: LPGAgentCapabilities,
        beliefs: AgentBeliefs,
        percept: WeightReading,
    ) -> None:
        """Plan: process weight update.

        Trigger:
        - New `WeightReading` percept from the environment.

        Condition checks:
        - Always runs when a percept arrives.

        Actions taken:
        - Update weight belief.
        - Estimate gas remaining from weight and tare.

        Supports project goal/scenario:
        - Goal G1 (monitor gas level) and normal daily usage scenario.
        """
        capabilities.perceive_weight(beliefs, percept)

    def handle_refill(
        self,
        capabilities: LPGAgentCapabilities,
        beliefs: AgentBeliefs,
    ) -> list[str]:
        """Plan: handle refill event.

        Trigger:
        - Called after processing a weight percept.

        Condition checks:
        - Refill detected if positive weight jump exceeds threshold.

        Actions taken:
        - `record_refill_event`
        - `reset_prediction_after_refill`

        Supports project goal/scenario:
        - Goal G4 (record refill events) and refill scenario.
        """
        refill_event = capabilities.detect_refill(beliefs, REFILL_DELTA_KG)
        if refill_event and refill_event.detected:
            self.last_action_context["new_weight_kg"] = beliefs.current_cylinder_weight_kg
            return ["record_refill_event", "reset_prediction_after_refill"]
        return []

    def update_usage_pattern(
        self,
        capabilities: LPGAgentCapabilities,
        beliefs: AgentBeliefs,
    ) -> list[str]:
        """Plan: update usage pattern model.

        Trigger:
        - After each weight update.

        Condition checks:
        - Always update rolling usage model.
        - Add warning action if significant usage shift is detected.

        Actions taken:
        - `update_usage_model`
        - optionally `usage_pattern_warning`

        Supports project goal/scenario:
        - Goal G2 (predict depletion) and sudden high-usage scenario.
        """
        usage_change = capabilities.update_usage_model(beliefs, USAGE_HISTORY_WINDOW)
        action_names = ["update_usage_model"]

        if usage_change and usage_change.changed:
            self.last_action_context["previous_rate"] = usage_change.previous_rate_kg_per_day
            self.last_action_context["current_rate"] = usage_change.current_rate_kg_per_day
            action_names.append("usage_pattern_warning")

        return action_names

    def detect_critical_gas(self, beliefs: AgentBeliefs) -> list[str]:
        """Plan: detect critical gas condition.

        Trigger:
        - After prediction update in the same cycle.

        Condition checks:
        - gas remaining <= critical threshold.

        Actions taken:
        - `critical_gas_warning`

        Supports project goal/scenario:
        - Goal G3 (alert before depletion), critical near-empty scenario.
        """
        if beliefs.estimated_gas_remaining_kg <= CRITICAL_GAS_KG:
            return ["critical_gas_warning"]
        return []

    def detect_low_gas(self, beliefs: AgentBeliefs) -> list[str]:
        """Plan: detect low gas condition.

        Trigger:
        - After critical-gas check in the cycle.

        Condition checks:
        - predicted days remaining <= low-gas threshold.
        - avoid duplicate low-gas warning if already sent.

        Actions taken:
        - `low_gas_warning`

        Supports project goal/scenario:
        - Goal G3 (proactive warning window before depletion).
        """
        if beliefs.warning_status.low_gas_sent:
            return []
        if beliefs.predicted_days_remaining <= LOW_GAS_DAYS_THRESHOLD:
            return ["low_gas_warning"]
        return []

    def run(self, capabilities: LPGAgentCapabilities, beliefs: AgentBeliefs, percept: WeightReading) -> list[str]:
        """Execute monitor-cycle plans and return selected action names.

        This method is the ordered plan execution used by the single agent:
        process percept -> check refill -> update model/prediction -> notify.
        """
        self.last_action_context = {"beliefs": beliefs}
        action_names: list[str] = []

        self.process_weight_update(capabilities, beliefs, percept)
        action_names.extend(self.handle_refill(capabilities, beliefs))
        action_names.extend(self.update_usage_pattern(capabilities, beliefs))

        capabilities.predict_depletion(beliefs)

        critical_actions = self.detect_critical_gas(beliefs)
        action_names.extend(critical_actions)

        if not critical_actions:
            action_names.extend(self.detect_low_gas(beliefs))

        # Remove duplicates while preserving order.
        return list(dict.fromkeys(action_names))