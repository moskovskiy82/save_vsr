# Missing Binary Sensors

## Active Functions (RUNNING device class)
Our integration has: Damper Open, Cooldown, Summer/Winter Mode, Fan Running, Cooling Recovery
Example integration has many more active function indicators:

- **Heat Exchange Active** - Heat exchanger is operating
  Register: REG_OUTPUT_Y2_DIGITAL (14104)

- **Heater Active** - Heater is currently on
  Register: REG_OUTPUT_TRIAC (14381)

- **Heat Recovery Active** - Heat recovery function active
  Register: REG_FUNCTION_ACTIVE_HEAT_RECOVERY (3105)

- **Cool Recovery Active** - Cooling recovery function active
  Register: REG_FUNCTION_ACTIVE_COOLING_RECOVERY (3106)

- **Free Cooling Active** - Free cooling function active
  Register: REG_FUNCTION_ACTIVE_FREE_COOLING (3102)

- **Defrosting Active** - Defrosting function active
  Register: REG_FUNCTION_ACTIVE_DEFROSTING (3104)

- **Moisture Transfer Active** - Moisture transfer function active
  Register: REG_FUNCTION_ACTIVE_MOISTURE_TRANSFER (3107)

- **Secondary Air Active** - Secondary air function active
  Register: REG_FUNCTION_ACTIVE_SECONDARY_AIR (3108)

- **Vacuum Cleaner Active** - Vacuum cleaner mode active
  Register: REG_FUNCTION_ACTIVE_VACUUM_CLEANER (3109)

- **Cooker Hood Active** - Cooker hood mode active
  Register: REG_FUNCTION_ACTIVE_COOKER_HOOD (3110)

- **Heating Active** - Heating function active
  Register: REG_FUNCTION_ACTIVE_HEATING (3103)

- **Heater Cool Down Active** - Heater cool down phase active
  Register: REG_FUNCTION_ACTIVE_HEATER_COOL_DOWN (3113)

## Digital Outputs (RUNNING device class)
- **Heater Digital Output** - Heater digital output state
  Register: REG_OUTPUT_Y1_DIGITAL (14102)

## Circulation Pumps (RUNNING device class)
- **Heating Circ Pump** - Heating circulation pump running
  Register: REG_OUTPUT_Y1_CIRC_PUMP (14301)

- **Cooling Circ Pump** - Cooling circulation pump running
  Register: REG_OUTPUT_Y3_CIRC_PUMP (14302)

- **Changeover Circ Pump** - Changeover circulation pump running
  Register: REG_OUTPUT_Y1_Y3_CIRC_PUMP (14303)

- **Extra Controller Circ Pump** - Extra controller circulation pump running
  Register: REG_OUTPUT_Y4_CIRC_PUMP (14304)

## Safety & Feedback (PROBLEM device class)
- **Emergency Thermostat** - Emergency thermostat triggered
  Register: REG_SENSOR_EMT (12111)

- **Changeover Feedback** - Changeover feedback status
  Register: REG_SENSOR_DI_CHANGE_OVER_FEEDBACK (12312)

Note: Our integration has basic binary sensors. Example has comprehensive coverage of all
active functions, circulation pumps, and safety indicators. Most useful additions would be
the active function indicators (heating, cooling, defrosting, etc.) for better monitoring.