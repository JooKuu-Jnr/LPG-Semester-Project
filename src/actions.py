"""Actions module

Defines what the agent can do after a decision is made.
Only skeletons are provided at this stage.

Action execution remains inside one agent process; there is no
separate notification agent in this architecture.
"""
from datetime import datetime

from src.beliefs import AgentBeliefs


class AgentActions:
    """Action executor for the single LPG monitoring agent."""

    def update_internal_state(self, beliefs: AgentBeliefs, updates: dict) -> None:
        """Apply simple key-value updates to the agent belief state.

        This is a generic simulation helper for actions that need to mutate
        internal state without external integrations.
        """
        for key, value in updates.items():
            if hasattr(beliefs, key):
                setattr(beliefs, key, value)

    def send_low_gas_alert(self, beliefs: AgentBeliefs) -> None:
        """Generate low-gas warning message for simulation output."""
        print(
            "[LOW-GAS WARNING] "
            f"Estimated gas remaining: {beliefs.estimated_gas_remaining_kg:.2f} kg | "
            f"Predicted days remaining: {beliefs.predicted_days_remaining:.1f} day(s)."
        )
        beliefs.warning_status.low_gas_sent = True

    def send_critical_alert(self, beliefs: AgentBeliefs) -> None:
        """Generate critical warning when cylinder is near empty."""
        print(
            "[CRITICAL WARNING] "
            f"Gas critically low: {beliefs.estimated_gas_remaining_kg:.2f} kg left. "
            "Refill immediately."
        )
        beliefs.warning_status.critical_sent = True

    def send_usage_warning(self, previous_rate: float, current_rate: float) -> None:
        """Generate usage-pattern-change warning message."""
        print(
            "[USAGE CHANGE] "
            f"Average usage changed from {previous_rate:.2f} to {current_rate:.2f} kg/day."
        )

    def record_refill_event(self, beliefs: AgentBeliefs, new_weight_kg: float) -> None:
        """Record refill event in beliefs and print a log-style message."""
        beliefs.last_refill_detected = True
        beliefs.last_refill_time = datetime.now()
        beliefs.current_cylinder_weight_kg = new_weight_kg
        print(
            "[REFILL EVENT] "
            f"Refill recorded at {beliefs.last_refill_time.isoformat(timespec='seconds')} | "
            f"New cylinder weight: {new_weight_kg:.2f} kg."
        )

    def reset_prediction_state_after_refill(self, beliefs: AgentBeliefs) -> None:
        """Reset prediction-related state after refill.

        Prometheus mapping:
        - After refill action, the agent updates beliefs to avoid stale
          depletion predictions and old warning flags.
        """
        beliefs.usage_history_kg.clear()
        beliefs.average_consumption_kg_per_day = 0.0
        beliefs.predicted_days_remaining = 0.0
        beliefs.warning_status.low_gas_sent = False
        beliefs.warning_status.critical_sent = False
        print("[STATE RESET] Prediction state reset after refill.")

    def update_usage_model(self, beliefs: AgentBeliefs) -> None:
        """Log usage model update from current belief values."""
        print(
            "[MODEL UPDATE] "
            f"Average consumption: {beliefs.average_consumption_kg_per_day:.3f} kg/day | "
            f"Predicted days remaining: {beliefs.predicted_days_remaining:.2f}."
        )

    def dispatch(self, action_name: str, context: dict) -> None:
        """Route a symbolic action name to an internal action method.

        Context is intentionally simple (plain dict) for this student prototype.
        """
        beliefs: AgentBeliefs = context.get("beliefs")
        if beliefs is None:
            raise ValueError("dispatch requires 'beliefs' in context")

        if action_name == "update_internal_state":
            self.update_internal_state(beliefs, context.get("updates", {}))
        elif action_name == "low_gas_warning":
            self.send_low_gas_alert(beliefs)
        elif action_name == "critical_gas_warning":
            self.send_critical_alert(beliefs)
        elif action_name == "record_refill_event":
            self.record_refill_event(beliefs, context.get("new_weight_kg", beliefs.current_cylinder_weight_kg))
        elif action_name == "reset_prediction_after_refill":
            self.reset_prediction_state_after_refill(beliefs)
        elif action_name == "update_usage_model":
            self.update_usage_model(beliefs)
        elif action_name == "usage_pattern_warning":
            self.send_usage_warning(
                context.get("previous_rate", 0.0),
                context.get("current_rate", 0.0),
            )
        else:
            print(f"[ACTION SKIPPED] Unknown action '{action_name}'.")
