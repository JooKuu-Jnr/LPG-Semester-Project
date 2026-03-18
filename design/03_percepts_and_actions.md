# Percepts and Actions
**Prometheus Phase 1 – System Specification**

---

## Percepts
Percepts are what the agent observes from its environment.

| Percept | Type | Description |
|---|---|---|
| `weight_reading` | float (kg) | Current gross weight of the cylinder + gas |
| `timestamp` | datetime | Time at which the weight was recorded |
| `refill_detected` | bool | True when weight increases significantly (refill event) |
| `usage_rate_change` | float (kg/day) | Detected change in average daily consumption |

### Percept Notes
- Weight readings come from a simulated scale in the prototype.
- A refill is detected when the current weight exceeds the previous reading by more than 1 kg.
- Usage rate is computed as a rolling average over the last 7 readings.
- Percepts originate from the **environment model**, which is not an agent.

---

## Actions
Actions are what the agent does in response to its decisions.

> Architectural note: these actions are executed by a single agent. The user is an alert recipient and decision target, not another agent.

| Action | Trigger | Description |
|---|---|---|
| `send_low_gas_alert` | Days remaining ≤ warning threshold | Notifies the user to plan a refill |
| `send_critical_alert` | Gas remaining < 0.5 kg | Urgent notification that gas is nearly empty |
| `send_usage_warning` | Usage rate increases > 50% above baseline | Warns that gas is being consumed faster than normal |
| `log_refill_event` | Refill detected | Records the new full weight and resets usage baseline |
| `update_usage_model` | Every new weight reading | Recalculates rolling average daily consumption |

---

## Percept–Action Mapping

```
weight_reading  ──►  update_usage_model
                ──►  [if days_remaining ≤ 3]  send_low_gas_alert
                ──►  [if gas_remaining < 0.5] send_critical_alert

refill_detected ──►  log_refill_event

usage_rate_change ──►  send_usage_warning  (if spike detected)
```
