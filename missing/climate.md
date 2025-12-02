# Missing Climate Features

## Additional Preset Modes
Our integration has: auto, manual, fireplace
Example integration has additional presets:
- **Crowded** - High ventilation for crowded spaces
  Command: 3, Status: 2
- **Refresh** - Boost ventilation temporarily
  Command: 4, Status: 3
- **Away** - Reduced ventilation when away
  Command: 6, Status: 5
- **Holiday** - Extended away mode
  Command: 7, Status: 6
- **Cooker Hood** - Kitchen extraction mode
  Command: 8, Status: 7
- **Vacuum Cleaner** - Boost for vacuum cleaning
  Command: 9, Status: 8
- **CDI1/CDI2/CDI3** - Configurable digital input modes
  Commands: 10, 11, 12, Status: 9, 10, 11
- **Pressure Guard** - Pressure control mode
  Command: 13, Status: 12

## HVAC Modes
✓ OFF - Already implemented
✓ AUTO - Already implemented
✓ FAN_ONLY - Already implemented
- **HEAT** - Heating mode (if heater active)
  Check: REG_FUNCTION_ACTIVE_HEATER (3002)
- **COOL** - Cooling mode (if cooler active)
  Check: REG_FUNCTION_ACTIVE_COOLER (3014)
- **HEAT_COOL** - Combined mode (if both active)

## HVAC Actions
✓ OFF - Already implemented
✓ FAN - Already implemented
- **HEATING** - When heater is actively heating
  Check: REG_OUTPUT_TRIAC (14381)
- **COOLING** - When cooler is actively cooling
  Check: REG_OUTPUT_Y3_DIGITAL (14202)
  #To copy into ours: Pending

## Additional Properties
- **Current Humidity** - Display current humidity from RH sensor
  Register: REG_SENSOR_RHS_PDM (12136)
  #To copy into ours: True

## Turn On/Off Support
- **Turn On/Off** - ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
  Control fan speed: 0=OFF, 2=ON (low speed)
  Register: REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF (1131)
  #To copy into ours: Pending

Note: Our implementation already has good foundation with preset modes and fan control.
Main additions would be: more preset modes, HVAC mode detection, and turn on/off feature.