# Agent Descriptors
**Prometheus Phase 2 – Architectural Design**

---

## Agent: LPGMonitorAgent

### Role
Monitor household LPG usage, predict depletion, and alert the user proactively.

### Architecture Rationale
- A single agent is sufficient for this project because all intelligence centers on one household cylinder context.
- The same agent handles monitoring, prediction, and notification decisions internally.
- Splitting into multiple agents would add coordination complexity without clear benefit for this prototype.
- The environment and user are modeled as external entities, not agents.

### Capabilities

| Capability | Description |
|---|---|
| `perceive_weight` | Read the latest weight percept from the environment |
| `detect_refill` | Compare current weight to previous; flag refill if weight rose significantly |
| `update_usage_model` | Maintain a rolling average of daily gas consumption |
| `predict_depletion` | Estimate days of gas remaining = gas_remaining / avg_daily_usage |
| `evaluate_thresholds` | Check whether alert conditions are met |
| `act` | Execute the appropriate action (alert, log, warn) |

### Internal State (Beliefs)

| Belief | Type | Description |
|---|---|---|
| `cylinder_tare_weight` | float | Empty cylinder weight (constant, set at init) |
| `last_weight` | float | Most recent gross weight reading |
| `gas_remaining` | float | Derived: last_weight − tare_weight |
| `avg_daily_usage` | float | Rolling average consumption in kg/day |
| `usage_history` | list[float] | Recent per-day usage values |
| `days_remaining` | float | Predicted days until depletion |
| `alert_sent` | bool | Prevents duplicate alerts in the same cycle |

### Plans (Perceive → Decide → Act)

```
Plan: MonitorCycle
  TRIGGER: new weight_reading percept
  BODY:
    1. perceive_weight()          → update last_weight, gas_remaining
    2. detect_refill()            → if refill: log_refill_event(), reset baseline
    3. update_usage_model()       → update avg_daily_usage
    4. predict_depletion()        → compute days_remaining
    5. evaluate_thresholds()      → determine which actions to fire
    6. act()                      → send alerts / warnings as needed
```

---

## Environment

| Element | Description |
|---|---|
| Simulated scale | Produces weight readings at configurable time intervals |
| LPG cylinder | Has a fixed tare weight; gas portion decreases with usage |
| Household usage profile | Defines base consumption rate with optional spike events |

---

## Interaction Overview

```
[Environment] -- weight_reading --> [LPGMonitorAgent] -- alerts --> [User (console)]
                                           |
                                    (internal beliefs)
```

`Environment` and `User` are interaction endpoints only; `LPGMonitorAgent` is the sole intelligent agent.
