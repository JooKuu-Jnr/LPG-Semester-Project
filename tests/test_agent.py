"""Lightweight tests for core LPG agent behaviors.

Run with:
    python -m pytest tests/test_agent.py -q
"""
from src.agent import LPGMonitorAgent
from src.percepts import WeightReading


class TestLPGMonitorAgentCoreBehaviors:
    """Core behavior checks for the single-agent prototype."""

    def setup_method(self):
        self.agent = LPGMonitorAgent()

    def test_low_gas_detection_triggers_low_warning_action(self):
        """Checks that low-gas condition leads to `low_gas_warning` decision.

        Setup creates a non-critical but low-days-remaining state by using
        a sharp daily consumption sample.
        """
        self.agent.beliefs.current_cylinder_weight_kg = 16.5
        reading = WeightReading(gross_weight_kg=15.9)  # gas estimate = 1.4 kg

        action_names = self.agent.decide(reading)

        assert "low_gas_warning" in action_names

    def test_refill_handling_resets_prediction_state(self):
        """Checks refill handling updates state and resets prediction values.

        A large positive weight jump should be treated as a refill event.
        After `run_cycle`, refill actions should clear prediction history/flags.
        """
        self.agent.beliefs.current_cylinder_weight_kg = 16.0
        self.agent.beliefs.usage_history_kg = [0.5, 0.6]
        self.agent.beliefs.average_consumption_kg_per_day = 0.55
        self.agent.beliefs.predicted_days_remaining = 3.0
        self.agent.beliefs.warning_status.low_gas_sent = True
        self.agent.beliefs.warning_status.critical_sent = True

        refill_reading = WeightReading(gross_weight_kg=18.2)  # +2.2 kg delta
        self.agent.run_cycle(refill_reading)

        assert self.agent.beliefs.last_refill_detected is True
        assert self.agent.beliefs.usage_history_kg == []
        assert self.agent.beliefs.average_consumption_kg_per_day == 0.0
        assert self.agent.beliefs.predicted_days_remaining == 0.0
        assert self.agent.beliefs.warning_status.low_gas_sent is False
        assert self.agent.beliefs.warning_status.critical_sent is False

    def test_prediction_update_after_weight_change(self):
        """Checks that depletion prediction is updated from incoming percepts.

        A normal usage step should produce a positive days-remaining estimate.
        """
        self.agent.beliefs.current_cylinder_weight_kg = 22.5
        reading = WeightReading(gross_weight_kg=22.3)

        _ = self.agent.decide(reading)

        assert self.agent.beliefs.predicted_days_remaining > 0
