# System Overview
**Prometheus Phase 1 – System Specification**

## Purpose
This document gives a high-level description of the LPG Monitoring Intelligent Agent system, the problem it solves, and the context in which it operates.

## Problem Statement
Many Ghanaian households rely on LPG cylinders as their primary cooking fuel.  
Gas depletion often goes unnoticed until cooking is interrupted, causing inconvenience and sometimes food waste.  
A monitoring agent that tracks usage and warns the household in advance addresses this gap.

## System Scope
- **Environment:** A household kitchen with a single LPG cylinder on a weighing scale.
- **Users:** Household members who cook and manage gas refills.
- **Agent role:** Passive observer + active alerter. The agent does not control appliances; it monitors and notifies.

## Architecture Decision (Single-Agent)
- This project adopts a **single-agent architecture**.
- One agent is sufficient because all intelligence is centralized around one decision task: estimate gas state and alert early.
- The same agent internally performs monitoring, prediction, and notification decisions in one Perceive → Decide → Act loop.
- The household environment and user are modeled as **non-agent external entities**:
	- Environment supplies percepts.
	- User receives alerts and may refill.


## Key Functionality
1. Continuously read cylinder weight and derive gas remaining.
2. Track daily/weekly usage patterns.
3. Predict days of gas remaining based on current usage rate.
4. Alert the user when gas falls below a safe threshold.
5. Record refill events to update baselines.


