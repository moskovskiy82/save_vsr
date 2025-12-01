# Missing Number Entities

## Time Delay Settings
Our integration has: ECO Offset, Holiday Days, Away Hours, Fireplace Mins, Refresh Mins, Crowded Hours
Example integration has the same PLUS additional settings:

- **Filter Period** - Filter replacement interval (months)
  Register: REG_FILTER_PERIOD (7001)
  Range: 3-15 months, Step: 1

Note: We already have all the user mode duration settings. Example adds filter period.

## Free Cooling Settings
Example integration has extensive free cooling configuration (we don't have):

- **Free Cooling Outdoor Low Limit** - Minimum outdoor temp for free cooling (°C)
  Register: REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_LOW_T_LIMIT (4103)
  Range: 7.0-30.0°C, Step: 0.1

- **Free Cooling Outdoor High Limit** - Maximum outdoor temp for free cooling (°C)
  Register: REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_HIGH_T_LIMIT (4104)
  Range: 7.0-30.0°C, Step: 0.1

- **Free Cooling Room Cancel Temp** - Room temp to cancel free cooling (°C)
  Register: REG_FREE_COOLING_ROOM_CANCEL_T (4105)
  Range: 12.0-30.0°C, Step: 0.1

- **Free Cooling Start Time Hours** - Start hour for free cooling (0-23)
  Register: REG_FREE_COOLING_START_TIME_H (4106)
  Range: 0-23, Step: 1

- **Free Cooling Start Time Minutes** - Start minutes for free cooling (0-59)
  Register: REG_FREE_COOLING_START_TIME_M (4107)
  Range: 0-59, Step: 1

- **Free Cooling End Time Hours** - End hour for free cooling (0-23)
  Register: REG_FREE_COOLING_END_TIME_H (4108)
  Range: 0-23, Step: 1

- **Free Cooling End Time Minutes** - End minutes for free cooling (0-59)
  Register: REG_FREE_COOLING_END_TIME_M (4109)
  Range: 0-59, Step: 1

## Circulation Pump Settings
Example integration has circulation pump configuration (we don't have):

- **Heating Circ Pump Start Temp** - Temperature to start heating pump (°C)
  Register: REG_HEATER_CIRC_PUMP_START_T (2113)
  Range: 0-20°C, Step: 0.1

- **Heating Circ Pump Stop Delay** - Delay before stopping heating pump (minutes)
  Register: REG_HEATER_CIRC_PUMP_STOP_DELAY (2122)
  Range: 0-60 min, Step: 1

- **Cooling Circ Pump Stop Delay** - Delay before stopping cooling pump (minutes)
  Register: REG_COOLER_CIRC_PUMP_STOP_DELAY (2317)
  Range: 0-60 min, Step: 1

- **Changeover Circ Pump Start Temp** - Temperature to start changeover pump (°C)
  Register: REG_CHANGE_OVER_CIRC_PUMP_START_T (2451)
  Range: 0-20°C, Step: 0.1

- **Changeover Circ Pump Stop Delay** - Delay before stopping changeover pump (minutes)
  Register: REG_CHANGE_OVER_CIRC_PUMP_STOP_DELAY (2452)
  Range: 0-60 min, Step: 1

- **Extra Controller Circ Pump Start Temp** - Temperature to start extra controller pump (°C)
  Register: REG_EXTRA_CONTROLLER_CIRC_PUMP_START_T (2404)
  Range: 0-20°C, Step: 0.1

- **Extra Controller Circ Pump Stop Delay** - Delay before stopping extra controller pump (minutes)
  Register: REG_EXTRA_CONTROLLER_CIRC_PUMP_STOP_DELAY (2405)
  Range: 0-60 min, Step: 1

Note: Our integration has basic time delay settings. Example has 18 additional number entities
for advanced configuration (free cooling schedule, circulation pump control). Most users won't
need these advanced settings. Filter Period would be the most useful addition.