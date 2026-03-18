"""Percepts module (Prometheus: percepts/events).

Contains the environment observations consumed by the agent during
the Perceive step of the Perceive -> Decide -> Act loop.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WeightReading:
    """Current cylinder weight reading from the simulated scale.

    In this project, gross_weight_kg means empty-cylinder weight + gas weight.
    """

    gross_weight_kg: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GasRemainingEstimate:
    """Estimated gas remaining after processing the latest weight reading.

    gas_remaining_kg is derived from gross weight and known tare weight.
    """

    gas_remaining_kg: float
    tare_weight_kg: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RefillDetected:
    """Percept representing whether a refill event was detected this cycle.

    detected=True usually means the observed weight increase exceeded the
    configured refill detection threshold.
    """

    detected: bool
    weight_delta_kg: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UsagePatternChange:
    """Percept representing change in household LPG consumption pattern.

    Example scenario: guests or festive cooking increase daily usage.
    """

    changed: bool
    previous_rate_kg_per_day: float
    current_rate_kg_per_day: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LowGasCondition:
    """Percept indicating low-gas risk based on remaining gas and prediction.

    This supports proactive user alerts before depletion.
    """

    is_low: bool
    gas_remaining_kg: float
    days_remaining_estimate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentPercepts:
    """Bundle of percepts available to the single agent in one cycle.

    This keeps the perceive input readable in tests and simulation runs.
    """

    weight_reading: WeightReading
    gas_estimate: Optional[GasRemainingEstimate] = None
    refill_detected: Optional[RefillDetected] = None
    usage_pattern_change: Optional[UsagePatternChange] = None
    low_gas_condition: Optional[LowGasCondition] = None


# Backward-compatible alias retained for existing imports in skeleton modules.
UsageRateChange = UsagePatternChange


# Backward-compatible alias retained for earlier refill percept naming.
RefillEvent = RefillDetected
