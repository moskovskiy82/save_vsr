# Missing Binary Sensors

## Active Functions (RUNNING device class)
Our integration has: Damper Open, Cooldown, Summer/Winter Mode, Fan Running, Cooling Recovery
Example integration has many more active function indicators:

- **Heat Exchange Active** - Heat exchanger is operating
  Register: REG_OUTPUT_Y2_DIGITAL (14104)
  To copy into ours: ⚠️ False - same as rotor %

- **Heater Active** - Heater is currently on
  Register: REG_OUTPUT_TRIAC (14381)
  To copy into ours: ⚠️ False - We have heater data

- **Heat Recovery Active** - Heat recovery function active
  Register: REG_FUNCTION_ACTIVE_HEAT_RECOVERY (3105)
  To copy into ours: ⚠️ False - false we have rotor %

- **Cool Recovery Active** - Cooling recovery function active
  Register: REG_FUNCTION_ACTIVE_COOLING_RECOVERY (3106)
  To copy into ours: ⚠️ False - same as rotor %

- **Free Cooling Active** - Free cooling function active
  Register: REG_FUNCTION_ACTIVE_FREE_COOLING (3102)
  To copy into ours: ⚠️ False 

- **Defrosting Active** - Defrosting function active
  Register: REG_FUNCTION_ACTIVE_DEFROSTING (3104)
  To copy into ours:  ⭐True

- **Moisture Transfer Active** - Moisture transfer function active
  Register: REG_FUNCTION_ACTIVE_MOISTURE_TRANSFER (3107)
  To copy into ours:  ⭐True

- **Secondary Air Active** - Secondary air function active
  Register: REG_FUNCTION_ACTIVE_SECONDARY_AIR (3108)
  To copy into ours: ⚠️ False 

- **Vacuum Cleaner Active** - Vacuum cleaner mode active
  Register: REG_FUNCTION_ACTIVE_VACUUM_CLEANER (3109)
  To copy into ours: ⚠️ False 

- **Cooker Hood Active** - Cooker hood mode active
  Register: REG_FUNCTION_ACTIVE_COOKER_HOOD (3110)
  #To copy into ours: ⚠️ False 

- **Heating Active** - Heating function active
  Register: REG_FUNCTION_ACTIVE_HEATING (3103)
  #To copy into ours: ⚠️ False 

- **Heater Cool Down Active** - Heater cool down phase active
  Register: REG_FUNCTION_ACTIVE_HEATER_COOL_DOWN (3113)
  To copy into ours: 📝 Pending 


## Digital Outputs (RUNNING device class)
- **Heater Digital Output** - Heater digital output state
  Register: REG_OUTPUT_Y1_DIGITAL (14102)
  To copy into ours: 📝 Pending 
  
## Circulation Pumps (RUNNING device class)
- **Heating Circ Pump** - Heating circulation pump running
  Register: REG_OUTPUT_Y1_CIRC_PUMP (14301)
  To copy into ours: ⚠️ False 
- **Cooling Circ Pump** - Cooling circulation pump running
  Register: REG_OUTPUT_Y3_CIRC_PUMP (14302)
  To copy into ours: ⚠️ False 
- **Changeover Circ Pump** - Changeover circulation pump running
  Register: REG_OUTPUT_Y1_Y3_CIRC_PUMP (14303)
  To copy into ours: ⚠️ False 
- **Extra Controller Circ Pump** - Extra controller circulation pump running
  Register: REG_OUTPUT_Y4_CIRC_PUMP (14304)
  To copy into ours: ⚠️ False 

## Safety & Feedback (PROBLEM device class)
- **Emergency Thermostat** - Emergency thermostat triggered
  Register: REG_SENSOR_EMT (12111)
  To copy into ours:  ⭐True
  To copy into ours: 📝 Pending 

- **Changeover Feedback** - Changeover feedback status
  Register: REG_SENSOR_DI_CHANGE_OVER_FEEDBACK (12312)
  To copy into ours: 📝 Pending 

Note: Our integration has basic binary sensors. Example has comprehensive coverage of all
active functions, circulation pumps, and safety indicators. Most useful additions would be
the active function indicators (heating, cooling, defrosting, etc.) for better monitoring.