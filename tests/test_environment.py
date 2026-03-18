"""
test_environment.py – Unit tests for the simulated Environment.
Prometheus Phase 3: Detailed Design validation

Run with:  python -m pytest tests/
"""
from simulation.environment import HouseholdLPGEnvironment
from src.percepts import WeightReading
from config.constants import (
    CYLINDER_FULL_GAS_KG,
    CYLINDER_TARE_WEIGHT_KG,
    DEFAULT_DAILY_USAGE_KG,
)


class TestEnvironmentInitialState:
    """Tests for the environment's starting conditions."""

    def setup_method(self):
        self.env = HouseholdLPGEnvironment()

    def test_starts_with_full_cylinder(self):
        """Environment should start with gas_remaining equal to CYLINDER_FULL_GAS_KG."""
        assert self.env.gas_remaining_kg == CYLINDER_FULL_GAS_KG

    def test_initial_gross_weight_is_tare_plus_full_gas(self):
        """Gross weight at start should be tare + full gas."""
        expected = CYLINDER_TARE_WEIGHT_KG + CYLINDER_FULL_GAS_KG
        assert self.env._gross_weight() == expected


class TestEnvironmentStep:
    """Tests for the step() method."""

    def setup_method(self):
        self.env = HouseholdLPGEnvironment()

    def test_step_returns_weight_reading(self):
        """step() must return a WeightReading percept."""
        # TODO: uncomment once step() is implemented
        # assert isinstance(self.env.step(), WeightReading)
        pass

    def test_step_reduces_gas_by_daily_usage(self):
        """Gas should decrease by daily_usage_kg after one step."""
        # TODO: call step() and assert gas_remaining_kg decreased correctly
        pass


class TestEnvironmentEvents:
    """Tests for refill and usage spike events."""

    def setup_method(self):
        self.env = HouseholdLPGEnvironment()

    def test_refill_resets_gas_to_full(self):
        """trigger_refill() should restore gas to CYLINDER_FULL_GAS_KG."""
        # TODO: deplete gas with step(), call trigger_refill(), assert full
        pass

    def test_usage_spike_increases_consumption(self):
        """A spiked step should consume more gas than a normal step."""
        # TODO: compare gas level after spiked vs normal step
        pass
