"""Beliefs/knowledge module


- This file is the agent's internal data description (belief set).
- Fields here represent what the single LPG agent knows at runtime.
- Update methods map percepts into belief-state changes.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.percepts import (
    GasRemainingEstimate,
    LowGasCondition,
    RefillDetected,
    UsagePatternChange,
    WeightReading,
)


@dataclass
class WarningStatus:
    """Tracks whether warning notifications have already been raised."""

    low_gas_sent: bool = False
    critical_sent: bool = False


@dataclass
class AgentBeliefs:
    """Internal knowledge maintained across monitor cycles.

    Required beliefs:
    - current cylinder weight
    - estimated gas remaining
    - last refill state
    - usage history
    - average consumption
    - predicted days remaining
    - warning status
    """

    current_cylinder_weight_kg: float
    estimated_gas_remaining_kg: float
    last_refill_detected: bool = False
    last_refill_time: Optional[datetime] = None
    usage_history_kg: list[float] = field(default_factory=list)
    average_consumption_kg_per_day: float = 0.0
    predicted_days_remaining: float = 0.0
    warning_status: WarningStatus = field(default_factory=WarningStatus)

    def update_from_weight_reading(self, percept: WeightReading) -> None:
        """Update belief: current cylinder weight from weight-reading percept."""
        self.current_cylinder_weight_kg = percept.gross_weight_kg

    def update_from_gas_estimate(self, percept: GasRemainingEstimate) -> None:
        """Update belief: estimated gas remaining from derived percept."""
        self.estimated_gas_remaining_kg = percept.gas_remaining_kg

    def update_from_refill(self, percept: RefillDetected) -> None:
        """Update belief: refill state when refill-detected percept arrives."""
        self.last_refill_detected = percept.detected
        if percept.detected:
            self.last_refill_time = percept.timestamp

    def update_from_usage_pattern_change(self, percept: UsagePatternChange) -> None:
        """Update belief: average consumption from usage-pattern percept."""
        self.average_consumption_kg_per_day = percept.current_rate_kg_per_day

    def update_from_low_gas_condition(self, percept: LowGasCondition) -> None:
        """Update belief: predicted days remaining from low-gas percept."""
        self.predicted_days_remaining = percept.days_remaining_estimate

    def append_usage_sample(self, usage_kg: float, max_history: int = 30) -> None:
        """Append daily usage sample and maintain bounded usage history."""
        self.usage_history_kg.append(usage_kg)
        if len(self.usage_history_kg) > max_history:
            self.usage_history_kg = self.usage_history_kg[-max_history:]

    def recalculate_average_consumption(self) -> None:
        """Recompute average daily consumption from usage history."""
        if not self.usage_history_kg:
            return
        self.average_consumption_kg_per_day = sum(self.usage_history_kg) / len(self.usage_history_kg)

    def recalculate_predicted_days_remaining(self) -> None:
        """Recompute days remaining from gas estimate and average consumption."""
        if self.average_consumption_kg_per_day <= 0:
            self.predicted_days_remaining = 0.0
            return
        self.predicted_days_remaining = (
            self.estimated_gas_remaining_kg / self.average_consumption_kg_per_day
        )

    # Backward-compatible aliases for existing skeleton references.
    @property
    def last_weight_kg(self) -> float:
        return self.current_cylinder_weight_kg

    @property
    def gas_remaining_kg(self) -> float:
        return self.estimated_gas_remaining_kg

    @property
    def avg_daily_usage_kg(self) -> float:
        return self.average_consumption_kg_per_day

    @property
    def days_remaining(self) -> float:
        return self.predicted_days_remaining

    @property
    def low_alert_sent(self) -> bool:
        return self.warning_status.low_gas_sent

    @property
    def critical_alert_sent(self) -> bool:
        return self.warning_status.critical_sent