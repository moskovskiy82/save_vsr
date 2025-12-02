# Missing Sensors

## Temperature Sensors
- **Extract Air Relative Humidity** - Humidity sensor reading (%)
  Register: REG_SENSOR_RHS_PDM (12136)

## Fan & Airflow Sensors
- **Heater Demand** - Heating demand from temperature control (%)
  Register: REG_HEATER_FROM_SATC (2114)
- **Heater Analog Output** - Heater analog output value (%)
  Register: REG_OUTPUT_Y1_ANALOG (14101)
- **Changeover Analog Output** - Changeover analog output value (%)
  Register: REG_OUTPUT_Y1_Y3_ANALOG (14306)

## Circulation Pump Counters (Diagnostic) #To copy into ours: ⚠️ False for all Circ pump
- **Heating Circ Pump Counter** - Time counter for heating circulation pump (seconds)
  Register: REG_HEATER_CIRC_PUMP_COUNTER (2124)
- **Cooling Circ Pump Counter** - Time counter for cooling circulation pump (seconds)
  Register: REG_COOLER_CIRC_PUMP_COUNTER (2318)
- **Changeover Circ Pump Counter** - Time counter for changeover circulation pump (seconds)
  Register: REG_CHANGE_OVER_CIRC_PUMP_COUNTER (2453)
- **Extra Controller Circ Pump Counter** - Time counter for extra controller circulation pump (seconds)
  Register: REG_EXTRA_CONTROLLER_CIRC_PUMP_COUNTER (2419)

## Filter & Maintenance
- **Filter Remaining Time** - Remaining filter time before replacement (seconds)
  Register: REG_FILTER_REMAINING_TIME_L (7005) + REG_FILTER_REMAINING_TIME_H (7006) [32-bit]

## Air Quality & Control
- **IAQ Level** - Indoor air quality level (Perfect/Good/Improving)
  Register: REG_IAQ_LEVEL (1123)
- **Demand Active Controller** - Active demand controller type (CO2/RH)
  Register: REG_DEMC_ACTIVE_CONTROLLER (1004)
- **Auto Mode Source** - Source of auto mode (External control/Demand control/Week schedule/Configuration fault)
  Register: REG_DEMC_AUTO_MODE_SOURCE (1062)

## Defrosting
- **Defrosting State** - Current defrosting state (Normal/Bypass/Stop/Secondary air/Error)
  Register: REG_DEFROSTING_STATE (4011)

## Alarm History
- **Alarm History** - Shows most recent alarm with full history in attributes
  Special sensor with alarm log parsing from registers 15701-15890

## Power Sensors (Already Implemented) 
✓ Supply Fan Power
✓ Extract Fan Power  
✓ Total Power

## Energy Sensors (Already Implemented)
✓ Fans Energy
✓ Heater Energy

Note: Example has separate supply_fan_energy and extract_fan_energy, we combine into fans_energy