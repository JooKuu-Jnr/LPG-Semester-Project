# Goals and Scenarios
**Prometheus Phase 1 – System Specification**

## Single-Agent Assumption
- All goals in this document are achieved by one agent (`LPGMonitorAgent`).
- There are no coordinator, predictor, or notifier sub-agents.
- User behavior and household conditions are treated as environmental context, not autonomous agents.

---

## Agent Goals

### G1 – Monitor Gas Level
**Description:** Track the current gas remaining in the cylinder at all times.  
**Condition for success:** The agent always holds an up-to-date estimate of gas remaining (in kg).

### G2 – Predict Depletion
**Description:** Use observed usage patterns to estimate how many days of gas remain.  
**Condition for success:** The agent can produce a days-remaining estimate whenever queried or when a threshold is crossed.

### G3 – Alert Before Depletion
**Description:** Notify the user when gas will run out within a configurable warning window (default: 3 days).  
**Condition for success:** At least one alert is issued before the cylinder reaches empty.

### G4 – Record Refill Events
**Description:** Detect and log when a cylinder is refilled so baselines are reset.  
**Condition for success:** After a refill, the agent uses the new full-cylinder weight as the updated baseline.

---

## Scenarios

### Scenario 1 – Normal Weekly Usage
**Context:** A household uses roughly 0.2 kg of gas per day.  
**Events:**
1. Agent reads weight daily.
2. Agent updates average daily usage.
3. When days-remaining drops to 3, agent issues a low-gas alert.
4. User refills cylinder, agent detects weight increase and resets baseline.

### Scenario 2 – Sudden High Usage (Party / Guests)
**Context:** On a weekend, usage spikes to 0.6 kg/day.  
**Events:**
1. Agent observes rapid weight drop.
2. Agent recalculates days-remaining with new usage rate.
3. Alert is issued earlier than expected.

### Scenario 3 – Missed Refill
**Context:** User ignores the alert and does not refill.  
**Events:**
1. Gas reaches critical level (< 0.5 kg).
2. Agent escalates to a critical alert.
3. Agent logs that the warning was ignored (for pattern analysis).
