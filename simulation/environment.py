"""Environment module

Simulates household LPG dynamics and emits percepts for the single agent.
The environment is an external context provider, not an agent.
"""
from datetime import datetime, timedelta
import random

from src.percepts import WeightReading
from config.constants import (
    CYLINDER_TARE_WEIGHT_KG,
    CYLINDER_FULL_GAS_KG,
    DEFAULT_DAILY_USAGE_KG,
)


class HouseholdLPGEnvironment:
    """Single-household environment that provides percepts to the agent.

    This class does not make autonomous decisions; it only updates
    physical simulation state and exposes percepts.
    """

    def __init__(
        self,
        initial_gas_kg: float = CYLINDER_FULL_GAS_KG,
        daily_usage_kg: float = DEFAULT_DAILY_USAGE_KG,
        start_date: datetime = datetime(2026, 1, 1),
    ) -> None:
        self.empty_cylinder_weight_kg: float = CYLINDER_TARE_WEIGHT_KG
        self.full_gas_weight_kg: float = CYLINDER_FULL_GAS_KG

        # Project mapping:
        # - gas_remaining_kg models available LPG content in the cylinder.
        # - daily_usage_kg models household cooking demand per day.
        # - current_date allows time-based simulation for prediction tests.
        self.gas_remaining_kg: float = initial_gas_kg
        self.daily_usage_kg: float = daily_usage_kg
        self.current_date: datetime = start_date
        self._spike_multiplier: float = 1.0  
        self.refill_count: int = 0

    def step(self, usage_kg: float | None = None) -> WeightReading:
        """Advance one day, apply usage, and expose the new weight percept.

        This is the default daily environment transition used by the
        simulation runner.
        """
        usage_today_kg = usage_kg if usage_kg is not None else self.daily_usage_kg * self._spike_multiplier
        self.consume_gas(usage_today_kg)
        self._spike_multiplier = 1.0
        self.current_date += timedelta(days=1)
        return self.generate_weight_reading()

    def sample_daily_usage(self) -> float:
        """Return simulated daily usage for continuous operation.

        Normal days: random usage in 0.2–0.6 kg/day.
        Occasional high-usage days: amplified usage (e.g., guests/events).
        """
        usage_kg = random.uniform(0.2, 0.6)

        # ~15% chance of high-usage day.
        if random.random() < 0.15:
            usage_kg *= random.uniform(1.4, 2.0)

        return usage_kg

    def generate_weight_reading(self) -> WeightReading:
        """Create the weight percept the agent can perceive this cycle."""
        return WeightReading(
            gross_weight_kg=self._gross_weight(),
            timestamp=self.current_date,
        )

    def get_state_snapshot(self) -> dict:
        """Return simple environment state for debugging/testing.

        Exposes non-agent environment values that support unit tests and
        transparent simulation inspection.
        """
        return {
            "current_date": self.current_date,
            "current_cylinder_weight_kg": self._gross_weight(),
            "empty_cylinder_weight_kg": self.empty_cylinder_weight_kg,
            "full_cylinder_weight_kg": self.empty_cylinder_weight_kg + self.full_gas_weight_kg,
            "gas_remaining_kg": self.gas_remaining_kg,
            "daily_usage_kg": self.daily_usage_kg,
            "refill_count": self.refill_count,
        }

    def get_current_state(self) -> dict:
        """Return current percept-relevant state for the agent loop.

        This is a convenience alias for runner code/readability.
        """
        return self.get_state_snapshot()

    def consume_gas(self, amount_kg: float) -> None:
        """Apply event-based gas usage (e.g., heavy cooking event)."""
        if amount_kg < 0:
            raise ValueError("amount_kg must be non-negative")
        self.gas_remaining_kg = max(0.0, self.gas_remaining_kg - amount_kg)

    def trigger_refill(self) -> None:
        """Simulate refill by restoring gas content to full capacity."""
        self.gas_remaining_kg = self.full_gas_weight_kg
        self.refill_count += 1

    def trigger_usage_spike(self, multiplier: float = 3.0) -> None:
        """Apply a one-day event spike in usage.

        Example mapping: hosting guests leads to unusually high LPG use.
        """
        if multiplier <= 0:
            raise ValueError("multiplier must be greater than 0")
        self._spike_multiplier = multiplier

    def set_daily_usage_pattern(self, daily_usage_kg: float) -> None:
        """Change baseline daily usage pattern for future days.

        This models seasonal or behavioral changes in household cooking.
        """
        if daily_usage_kg < 0:
            raise ValueError("daily_usage_kg must be non-negative")
        self.daily_usage_kg = daily_usage_kg

    def _gross_weight(self) -> float:
        """Return current gross weight: cylinder tare + remaining gas."""
        return self.empty_cylinder_weight_kg + self.gas_remaining_kg
