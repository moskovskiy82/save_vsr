# Missing Select Entities

## Configuration Selects
Our integration has: Preset Mode Select (basic)
Example integration has additional configuration selects:

- **Temperature Control Mode** - Choose which temperature sensor controls the system
  Register: REG_TC_CONTROL_MODE (2031)
  Options: Supply Air (0), Room Air (1), Extract Air (2)

- **Fan Regulation Unit** - Choose fan control method
  Register: REG_FAN_REGULATION_UNIT (1274)
  Options: Manual % (0), Manual RPM (1), Pressure (2), Flow (3), External (4)

- **Defrosting Mode** - Set defrosting intensity
  Register: REG_DEFROSTING_MODE (4001)
  Options: Soft (0), Normal (1), Hard (2)

- **Free Cooling Supply Fan Level** - Fan speed during free cooling (supply)
  Register: REG_FREE_COOLING_MIN_SPEED_LEVEL_SAF (4112)
  Options: Normal (3), High (4), Maximum (5)

- **Free Cooling Extract Fan Level** - Fan speed during free cooling (extract)
  Register: REG_FREE_COOLING_MIN_SPEED_LEVEL_EAF (4113)
  Options: Normal (3), High (4), Maximum (5)

Note: Our select.py only has preset mode selection. Example has 5 additional configuration
selects for advanced system tuning. Most useful would be Temperature Control Mode and
Defrosting Mode for typical users.