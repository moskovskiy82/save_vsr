# Missing Features Analysis

This directory contains analysis of features present in the example Systemair integration but missing in our SAVE VSR integration.

## Files
- **sensors.md** - Missing sensor entities (temperature, airflow, diagnostics, etc.)
- **climate.md** - Missing climate features (preset modes, HVAC modes, actions)
- **switches.md** - Missing switch entities (configuration toggles)
- **binary_sensors.md** - Missing binary sensor entities (active functions, pumps, safety)

## Summary

### High Priority (Most Useful)
1. **Climate Preset Modes** - Add Crowded, Refresh, Away, Holiday modes
2. **Active Function Binary Sensors** - Heating Active, Cooling Active, Defrosting Active
3. **IAQ & Demand Control Sensors** - IAQ Level, Demand Controller, Auto Mode Source
4. **Filter Remaining Time** - Important for maintenance tracking
5. **Defrosting State** - Important for winter operation monitoring

### Medium Priority (Nice to Have)
1. **Circulation Pump Binary Sensors** - Monitor pump operation
2. **Heater Demand Sensor** - See heating demand percentage
3. **HVAC Mode Detection** - HEAT/COOL modes based on active equipment
4. **Alarm History Sensor** - Full alarm log with timestamps
5. **Additional Preset Modes** - Cooker Hood, Vacuum Cleaner, CDI modes

### Low Priority (Advanced/Rare Use)
1. **Circulation Pump Counters** - Runtime tracking for pumps
2. **Free Cooling Switch** - Enable/disable free cooling
3. **Manual Fan Stop Switch** - Safety feature toggle
4. **Emergency Thermostat Binary Sensor** - Safety indicator

## Architecture Notes

The example integration uses:
- **ModbusParameter dataclass** - Clean register definitions (we should adopt this)
- **Separate power sensors** - Supply fan, extract fan, heater (we combine)
- **Energy sensors with RestoreSensor** - Proper energy tracking (we have this)
- **Alarm log parsing** - Complex but useful for history tracking
- **32-bit register handling** - For counters and timestamps

## Recommendations

1. **Adopt ModbusParameter structure** - Makes register management cleaner
2. **Add most-used preset modes first** - Away, Holiday, Crowded, Refresh
3. **Add active function binary sensors** - Better system monitoring
4. **Consider alarm history** - Useful for troubleshooting
5. **Keep our simpler power model** - Combined fans_energy works well

## Next Steps

User should review these files and mark which features to implement.
Priority should be given to features that improve daily usability and monitoring.