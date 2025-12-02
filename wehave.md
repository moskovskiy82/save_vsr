# Current Implementation - What We Have

Complete inventory of all entities currently implemented in our Systemair SAVE VSR integration.

**Last Updated:** 2025-12-02
**Total Entities:** ~38 (excluding diagnostic alarms and countdowns)

---

## 📊 Summary by Domain

| Domain | Count | Description |
|--------|-------|-------------|
| **Climate** | 1 | Main ventilation control with presets and fan modes |
| **Sensors** | 22 | Temperature, fan, power, energy, alarms, diagnostics |
| **Binary Sensors** | 5 | Status indicators (damper, cooling, fan, etc.) |
| **Switches** | 3 | Feature enable/disable controls |
| **Number** | 6 | Duration settings for preset modes |
| **Select** | 1 | Preset mode selector |

---

## 🌡️ Climate Entity

### VSR Ventilation
**Entity ID:** `climate.vsr_ventilation`
**Features:**
- ✅ Target Temperature Control (12-30°C, 1°C steps)
  - Register: REG_TARGET_TEMP (2000) - stored as °C × 10
- ✅ Fan Modes: low, medium, high
  - Register: REG_MODE_SPEED (1130) - values 2, 3, 4
- ✅ HVAC Modes: OFF, AUTO, FAN_ONLY
  - Status Register: REG_MODE_MAIN_STATUS_IN (1160)
  - Command Register: REG_MODE_MAIN_CMD (1161)
- ✅ Preset Modes: auto, manual, fireplace
  - Status values: 0 (auto), 1 (manual), 4 (fireplace)
  - Command values: 1 (auto), 2 (manual), 5 (fireplace)

**Current Temperature:** Supply air temperature (REG_TEMP_SUPPLY, 12102)

---

## 📈 Sensors (22 total)

### Temperature Sensors (5)
1. **Temperature Outdoor** - Outdoor air temperature
   - Register: REG_TEMP_OUTDOOR (12101) - °C × 10
   
2. **Temperature Supply** - Supply air temperature
   - Register: REG_TEMP_SUPPLY (12102) - °C × 10
   
3. **Temperature Exhaust** - Exhaust air temperature
   - Register: REG_TEMP_EXHAUST (12543) - °C × 10
   
4. **Temperature Overheat** - Overheat protection temperature
   - Register: REG_TEMP_OVERHEAT (12107) - °C × 10
   
5. **Target Temperature** - Temperature setpoint
   - Register: REG_TARGET_TEMP (2000) - °C × 10

### Fan Sensors (6)
6. **Fan Supply RPM** - Supply fan speed in RPM
   - Register: REG_SAF_RPM (12400)
   
7. **Fan Extract RPM** - Extract fan speed in RPM
   - Register: REG_EAF_RPM (12401)
   
8. **Fan Supply %** - Supply fan speed percentage
   - Register: REG_SUPPLY_FAN_PCT (14000)
   
9. **Fan Extract %** - Extract fan speed percentage
   - Register: REG_EXTRACT_FAN_PCT (14001)
   
10. **Heater %** - Heater output percentage
    - Register: REG_HEATER_PERCENT (2148)
    
11. **Rotor %** - Heat exchanger rotor speed
    - Register: REG_ROTOR (14350)

### Power Sensors (4)
12. **Fan Supply Power** - Calculated supply fan power
    - Calculation: (fan_supply_% / 100) × 160W
    
13. **Fan Extract Power** - Calculated extract fan power
    - Calculation: (fan_extract_% / 100) × 160W
    
14. **Heater Power** - Calculated heater power
    - Calculation: (heater_% / 100) × 1650W
    
15. **VSR Power Consumption** - Total power consumption
    - Calculation: supply_power + extract_power + heater_power

### Energy Sensors (2) - Energy Dashboard Compatible
16. **Fans Energy** - Accumulated fan energy consumption
    - Integrates: supply_fan_power + extract_fan_power over time
    - **Persists across restarts** (RestoreSensor)
    
17. **Heater Energy** - Accumulated heater energy consumption
    - Integrates: heater_power over time
    - **Persists across restarts** (RestoreSensor)

### Mode & Status Sensors (2)
18. **Mode Speed** - Current fan speed mode
    - Register: REG_MODE_SPEED (1130)
    - Options: low (2), medium (3), high (4)
    
19. **Mode Main Status** - Current operating mode
    - Register: REG_MODE_MAIN_STATUS_IN (1160)

### Configuration Sensors (2)
20. **ECO Offset** - ECO mode temperature offset
    - Register: REG_SETPOINT_ECO_OFFSET (2503) - °C × 10
    
21. **Modbus Failures** - Count of Modbus communication failures

### Countdown Sensors (5) - Show time remaining for active preset
- **Away Time Remaining** (mode_main == 5)
- **Crowded Time Remaining** (mode_main == 2)
- **Refresh Time Remaining** (mode_main == 3)
- **Fireplace Time Remaining** (mode_main == 4)
- **Holiday Time Remaining** (mode_main == 6)

---

## 🔴 Alarm Sensors (27 total)

All alarm sensors show status: Inactive, Active, Waiting, or Cleared Error Active

### Alarm Type Indicators (3)
- **Alarm Type A** (REG 15900)
- **Alarm Type B** (REG 15901)
- **Alarm Type C** (REG 15902)

### Component Alarms (24)
- **Alarm SAF** - Supply air fan (15001)
- **Alarm EAF** - Extract air fan (15008)
- **Alarm Frost Protect** (15015)
- **Alarm SAF RPM** (15029)
- **Alarm EAF RPM** (15036)
- **Alarm FPT** - Frost protection temp (15057)
- **Alarm OAT** - Outdoor air temp (15064)
- **Alarm SAT** - Supply air temp (15071)
- **Alarm RAT** - Room air temp (15078)
- **Alarm EAT** - Extract air temp (15085)
- **Alarm ECT** - Extra controller temp (15092)
- **Alarm EFT** - Efficiency temp (15099)
- **Alarm OHT** - Overheat temp (15106)
- **Alarm EMT** - Emergency thermostat (15113)
- **Alarm BYS** - Bypass damper (15127)
- **Alarm Sec Air** - Secondary air (15134)
- **Alarm Filter** (15141)
- **Alarm RH** - Relative humidity (15162)
- **Alarm Low SAT** (15176)
- **Alarm PDM RHS** - PDM RHS sensor (15508)
- **Alarm PDM EAT** - PDM EAT sensor (15515)
- **Alarm Manual Fan Stop** (15522)
- **Alarm Overheat Temp** (15529)
- **Alarm Fire** (15536)
- **Alarm Filter Warn** (15543)

---

## 🔘 Binary Sensors (5 total)

1. **Damper Open** - Damper position status
   - Register: REG_DAMPER_STATE (14003)
   
2. **Cooldown** - Cooldown mode active
   - Register: REG_COOLING_RECOVERY (2133)
   
3. **Summer/Winter Mode** - Season mode indicator
   - Register: REG_MODE_SUMMERWINTER (1038)
   
4. **Fan Running** - Fan operation status
   - Register: REG_FAN_RUNNING_START (1350)
   
5. **Cooling Recovery** - Cooling recovery active
   - Register: REG_COOLING_RECOVERY (2133)

---

## 🔌 Switches (3 total)

1. **ECO Mode** - Enable/disable ECO mode
   - Register: REG_ECO_MODE_ENABLE (2504)
   
2. **Heater Enable** - Enable/disable heater
   - Register: REG_HEATER_ENABLE (3001)
   
3. **RH Transfer** - Enable/disable humidity transfer
   - Register: REG_RH_TRANSFER_ENABLE (2203)

---

## 🔢 Number Entities (6 total)

1. **Eco Offset** - ECO mode temperature offset
   - Register: REG_SETPOINT_ECO_OFFSET (2503)
   - Range: 0.0 - 10.0°C, Step: 0.5°C
   
2. **Holiday Duration** - Holiday mode duration
   - Register: REG_HOLIDAY_DAYS (1100)
   - Range: 1 - 365 days
   
3. **Away Duration** - Away mode duration
   - Register: REG_AWAY_HOURS (1101)
   - Range: 1 - 72 hours
   
4. **Refresh Duration** - Refresh mode duration
   - Register: REG_REFRESH_MINS (1103)
   - Range: 1 - 240 minutes
   
5. **Crowded Duration** - Crowded mode duration
   - Register: REG_CROWDED_HOURS (1104)
   - Range: 1 - 8 hours
   
6. **Fireplace Duration** - Fireplace mode duration
   - Register: REG_FIREPLACE_MINS (1102)
   - Range: 1 - 60 minutes

---

## 📋 Select Entities (1 total)

1. **Preset Mode** - Select preset mode
   - Register: REG_MODE_MAIN_CMD (1161)
   - Options: auto, manual, fireplace
   - **Note:** Duplicates climate entity preset functionality

---

## 🎯 Key Features

### ✅ Implemented
- Complete climate control (temperature, fan, presets)
- Comprehensive temperature monitoring (5 sensors)
- Fan speed monitoring (RPM + percentage)
- Power consumption tracking (real-time, 4 sensors)
- Energy consumption tracking (persistent, Energy Dashboard compatible)
- Full alarm system (27 alarm types)
- Mode duration configuration (6 preset timers)
- Basic binary status indicators (5 sensors)
- Feature enable/disable switches (3 switches)

### 🔧 Architecture Highlights
- **ModbusParameter system** - Clean register definitions in modbus.py
- **Coordinator pattern** - Efficient polling with get_modbus_data()
- **Energy sensors** - RestoreSensor for persistence across restarts
- **Optimistic updates** - Immediate UI feedback on writes

---

## 📊 Comparison with Example Integration

| Feature | Our Integration | Example Integration |
|---------|----------------|---------------------|
| Climate Presets | 3 | 13 |
| Temperature Sensors | 5 | 7 |
| Power Sensors | 4 | 4 |
| Energy Sensors | 2 | 2 |
| Binary Sensors | 5 | ~25 |
| Switches | 3 | 5 |
| Number Entities | 6 | 24 |
| Select Entities | 1 | 6 |

**See [`missing/`](missing/) directory for detailed breakdown of missing features.**