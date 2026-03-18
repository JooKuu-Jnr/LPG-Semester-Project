"""Capabilities module.

Defines reusable abilities invoked by plans.
In this refactor, decision logic stays in `plans.py` so responsibilities
are clearer for a student-friendly Prometheus mapping.
"""
from typing import Optional

from config.constants import CYLINDER_TARE_WEIGHT_KG
from src.beliefs import AgentBeliefs
from src.percepts import (
    GasRemainingEstimate,
    RefillDetected,
    UsagePatternChange,
    WeightReading,
)


class MonitoringCapability:
    """Capability for sensing and state extraction from environment percepts.

    Trigger:
    - Triggered whenever a new WeightReading percept arrives.
    """

    def apply_weight_reading(self, beliefs: AgentBeliefs, percept: WeightReading) -> float:
        """Update weight belief and return weight delta from previous reading."""
        previous_weight = beliefs.current_cylinder_weight_kg
        beliefs.update_from_weight_reading(percept)
        return percept.gross_weight_kg - previous_weight

    def estimate_gas_remaining(self, beliefs: AgentBeliefs) -> GasRemainingEstimate:
        """Derive gas-remaining estimate from current weight and tare weight."""
        gas_remaining = max(0.0, beliefs.current_cylinder_weight_kg - CYLINDER_TARE_WEIGHT_KG)
        estimate = GasRemainingEstimate(
            gas_remaining_kg=gas_remaining,
            tare_weight_kg=CYLINDER_TARE_WEIGHT_KG,
        )
        beliefs.update_from_gas_estimate(estimate)
        return estimate

    def detect_refill(self, beliefs: AgentBeliefs, weight_delta_kg: float, refill_delta_kg: float) -> RefillDetected:
        """Detect refill event using positive weight jump threshold."""
        refill = RefillDetected(
            detected=weight_delta_kg >= refill_delta_kg,
            weight_delta_kg=weight_delta_kg,
        )
        beliefs.update_from_refill(refill)
        return refill


class PredictionCapability:
    """Capability for usage modeling and depletion prediction.

    Trigger:
    - Triggered after monitoring updates beliefs in each cycle.
    """

    def update_usage_model(
        self,
        beliefs: AgentBeliefs,
        usage_sample_kg: float,
        history_window: int,
    ) -> UsagePatternChange:
        """Update usage history and return whether pattern changed significantly."""
        previous_avg = beliefs.average_consumption_kg_per_day
        beliefs.append_usage_sample(max(0.0, usage_sample_kg), max_history=history_window)
        beliefs.recalculate_average_consumption()

        changed = False
        if previous_avg > 0:
            changed = beliefs.average_consumption_kg_per_day >= previous_avg * 1.5

        usage_change = UsagePatternChange(
            changed=changed,
            previous_rate_kg_per_day=previous_avg,
            current_rate_kg_per_day=beliefs.average_consumption_kg_per_day,
        )
        beliefs.update_from_usage_pattern_change(usage_change)
        return usage_change

    def predict_days_remaining(self, beliefs: AgentBeliefs) -> float:
        """Compute predicted days remaining and update beliefs."""
        beliefs.recalculate_predicted_days_remaining()
        return beliefs.predicted_days_remaining


class LPGAgentCapabilities:
    """Coordinator exposing a simple capability API for the agent plan.

    This preserves a compact single-class interface while internally grouping
    behavior into Monitoring and Prediction capabilities.
    """

    def __init__(self) -> None:
        self.monitoring = MonitoringCapability()
        self.prediction = PredictionCapability()
        self._last_weight_delta_kg: float = 0.0
        self._last_usage_change: Optional[UsagePatternChange] = None
        self._last_refill_event: Optional[RefillDetected] = None

    def perceive_weight(self, beliefs: AgentBeliefs, percept: WeightReading) -> None:
        """Update monitoring-related beliefs from the latest percept."""
        self._last_weight_delta_kg = self.monitoring.apply_weight_reading(beliefs, percept)
        self.monitoring.estimate_gas_remaining(beliefs)

    def detect_refill(self, beliefs: AgentBeliefs, refill_delta_kg: float) -> Optional[RefillDetected]:
        """Detect whether a refill occurred between readings."""
        self._last_refill_event = self.monitoring.detect_refill(
            beliefs,
            weight_delta_kg=self._last_weight_delta_kg,
            refill_delta_kg=refill_delta_kg,
        )
        return self._last_refill_event

    def update_usage_model(self, beliefs: AgentBeliefs, history_window: int) -> Optional[UsagePatternChange]:
        """Update rolling usage statistics and detect usage shifts."""
        usage_sample = max(0.0, -self._last_weight_delta_kg)
        self._last_usage_change = self.prediction.update_usage_model(
            beliefs,
            usage_sample_kg=usage_sample,
            history_window=history_window,
        )
        return self._last_usage_change

    def predict_depletion(self, beliefs: AgentBeliefs) -> None:
        """Compute days remaining from current gas and usage beliefs."""
        self.prediction.predict_days_remaining(beliefs)