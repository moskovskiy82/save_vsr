from __future__ import annotations

DOMAIN = "save_vsr"

DEFAULT_UPDATE_INTERVAL = 10  # seconds

# Transport
TRANSPORT_SERIAL = "serial"
TRANSPORT_TCP = "tcp"

# Serial defaults
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 9600
DEFAULT_BYTESIZE = 8
DEFAULT_STOPBITS = 1
DEFAULT_PARITY = "N"

# TCP defaults
DEFAULT_HOST = "192.168.1.100"
DEFAULT_TCP_PORT = 502

DEFAULT_SLAVE_ID = 1

# --- Register map (based on your earlier notes) ------------------
# Read (holding/input)
REG_MODE_MAIN_STATUS_IN = 1160   # input (status)
REG_MODE_MAIN_CMD      = 1161    # holding (command/preset)
REG_MODE_SPEED         = 1130    # holding (2/3/4 -> low/med/high)

REG_TARGET_TEMP        = 2000    # holding, x0.1 C
REG_TEMP_OUTDOOR       = 12101   # holding, x0.1 C
REG_TEMP_SUPPLY        = 12102   # holding, x0.1 C
REG_TEMP_EXHAUST       = 12105   # holding, x0.1 C
REG_TEMP_EXTRACT       = 12542   # holding, x0.1 C
REG_TEMP_OVERHEAT      = 12107   # holding, x0.1 C

REG_SAF_RPM            = 12400   # holding
REG_EAF_RPM            = 12401   # holding
REG_SUPPLY_FAN_PCT     = 14000   # holding (%)
REG_EXTRACT_FAN_PCT    = 14001   # holding (%)
REG_HEATER_PERCENT     = 14101   # holding (%)
REG_HEAT_EXCH_STATE    = 14102   # holding
REG_ROTOR              = 14350   # holding
REG_HEATER             = 2148    # holding

REG_SETPOINT_ECO_OFFSET = 2503   # holding, x0.1 C

# Binary-ish
REG_MODE_SUMMERWINTER  = 1038    # holding (bool)
REG_FAN_RUNNING_START  = 1350    # holding (2 regs: fan_running, cooldown)
REG_DAMPER_STATE       = 14003   # holding (bool)
REG_COOLING_RECOVERY   = 2133    # holding (bool)

# Diagnostics timers
REG_USERMODE_REMAIN    = 1110    # input seconds
REG_USERMODE_FACTOR    = 1111    # input factor (extends seconds for holiday)

# Durations (setpoints)
REG_HOLIDAY_DAYS       = 1100    # holding, days
REG_AWAY_HOURS         = 1101    # holding, hours
REG_FIREPLACE_MINS     = 1102    # holding, minutes
REG_REFRESH_MINS       = 1103    # holding, minutes
REG_CROWDED_HOURS      = 1104    # holding, hours

# Alarms (enum 0..3 where applicable)
REG_ALARM_SAF          = 15001
REG_ALARM_EAF          = 15008
REG_ALARM_FROST_PROT   = 15015
REG_ALARM_SAF_RPM      = 15029
REG_ALARM_EAF_RPM      = 15036
REG_ALARM_FPT          = 15057
REG_ALARM_OAT          = 15064
REG_ALARM_SAT          = 15071
REG_ALARM_RAT          = 15078
REG_ALARM_EAT          = 15085
REG_ALARM_ECT          = 15092
REG_ALARM_EFT          = 15099
REG_ALARM_OHT          = 15106
REG_ALARM_EMT          = 15113
REG_ALARM_BYS          = 15127
REG_ALARM_SEC_AIR      = 15134
REG_ALARM_FILTER       = 15141
REG_ALARM_RH           = 15162
REG_ALARM_LOW_SAT      = 15176
REG_ALARM_PDM_RHS      = 15508
REG_ALARM_PDM_EAT      = 15515
REG_ALARM_MAN_FAN_STOP = 15522
REG_ALARM_OVERHEAT_TEMP= 15529
REG_ALARM_FIRE         = 15536
REG_ALARM_FILTER_WARN  = 15543

REG_ALARM_TYPE_A       = 15900
REG_ALARM_TYPE_B       = 15901
REG_ALARM_TYPE_C       = 15902

# Enums/maps
ALARM_STATE_TO_VALUE = {"Inactive": 0, "Active": 1, "Waiting": 2, "Cleared Error Active": 3}
ALARM_VALUE_TO_STATE = {v: k for k, v in ALARM_STATE_TO_VALUE.items()}

FAN_SPEED_MAP = {2: "low", 3: "medium", 4: "high"}
FAN_SPEED_TO_VALUE = {v: k for k, v in FAN_SPEED_MAP.items()}

# Main mode / Presets (per your earlier mapping)
PRESET_MAP = {
    2: "crowded",
    3: "refresh",
    4: "fireplace",
    5: "away",
    6: "holiday",
    7: "kitchen",          # present on some units; we expose but don't set duration
    8: "vacuum_cleaner"    # present on some units; ditto
}
PRESET_TO_VALUE = {v: k for k, v in PRESET_MAP.items()}
