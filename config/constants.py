"""
constants.py – Configuration constants for the LPG Monitoring Agent.

"""

# --- Cylinder ---
CYLINDER_TARE_WEIGHT_KG = 14.5   # empty cylinder weight (standard Ghana 14.5 kg cylinder)
CYLINDER_FULL_GAS_KG    = 14.5   # gas content when full (14.5 kg LPG cylinder)

# --- Usage ---
DEFAULT_DAILY_USAGE_KG  = 0.20   # average daily consumption (kg/day)
USAGE_HISTORY_WINDOW    = 7      # days of history used in rolling average

# --- Alert thresholds ---
LOW_GAS_DAYS_THRESHOLD  = 3      # warn when days remaining falls to or below this
CRITICAL_GAS_KG         = 0.50  # escalate to critical alert below this gas level

# --- Refill detection ---
REFILL_DELTA_KG         = 1.0   # minimum weight increase that signals a refill
