# Testing Energy Sensors - Instructions

## What Was Added

Two new energy sensors for Home Assistant Energy Dashboard:

1. **`sensor.vsr_fans_energy`** - Combined energy of supply + extract fans
2. **`sensor.vsr_heater_energy`** - Heater energy consumption

## How to Test

### Step 1: Restart Home Assistant

```bash
# Restart HA to load the new sensors
ha core restart
```

### Step 2: Verify Sensors Exist

1. Go to **Developer Tools → States**
2. Search for:
   - `sensor.vsr_fans_energy`
   - `sensor.vsr_heater_energy`
3. Check that both sensors show:
   - **State:** `0.0` (or restored value if restarted)
   - **Unit:** `kWh`
   - **Device Class:** `energy`
   - **State Class:** `total_increasing`

### Step 3: Monitor Energy Accumulation

Wait 1-2 minutes and check if values are increasing:

```
Initial:  sensor.vsr_fans_energy = 0.0000 kWh
After 1m: sensor.vsr_fans_energy = 0.0015 kWh  ✓ (increasing)
After 2m: sensor.vsr_fans_energy = 0.0030 kWh  ✓ (increasing)
```

**Expected behavior:**
- Values should increase every 30 seconds (coordinator update interval)
- Increment depends on current fan/heater power consumption
- If fans are off (0%), energy should not increase

### Step 4: Test State Restoration

1. Note current energy values
2. Restart Home Assistant
3. After restart, verify sensors restored their values (not reset to 0)

### Step 5: Add to Energy Dashboard

1. Go to **Settings → Dashboards → Energy**
2. Click **"Add Consumption"**
3. Select `sensor.vsr_fans_energy`
4. Click **"Add Consumption"** again
5. Select `sensor.vsr_heater_energy`
6. Wait 24 hours for meaningful statistics

## Expected Power Consumption

Based on your VSR 500 specifications:

### Fans (sensor.vsr_fans_energy)
- **Supply Fan:** 160W max
- **Extract Fan:** 160W max
- **Total:** 320W max
- **Typical:** 50-150W (depending on speed)

### Heater (sensor.vsr_heater_energy)
- **Max Power:** 1650W
- **Typical:** 0-1650W (depending on heating demand)

## Calculation Example

If fans run at 50% for 1 hour:
```
Power = (50% × 160W) + (50% × 160W) = 160W
Energy = 160W × 1h / 1000 = 0.16 kWh
```

If heater runs at 30% for 1 hour:
```
Power = 30% × 1650W = 495W
Energy = 495W × 1h / 1000 = 0.495 kWh
```

## Troubleshooting

### Sensors Not Appearing
- Check HA logs: `Settings → System → Logs`
- Look for errors related to `save_vsr` or `sensor.py`
- Verify integration is loaded: `Developer Tools → States` → search for other VSR sensors

### Energy Not Increasing
- Check power sensors are working:
  - `sensor.vsr_supply_fan_power`
  - `sensor.vsr_extract_fan_power`
  - `sensor.vsr_heater_power`
- Verify fans are actually running (check RPM sensors)
- Check coordinator is updating (look at temperature sensors)

### Energy Resets to Zero After Restart
- Check HA logs for restoration errors
- Verify database is working (other sensors should also restore)
- May need to wait one update cycle (30s) after restart

## What to Report

Please report:
1. ✅ Sensors appear correctly
2. ✅ Energy values increase over time
3. ✅ Values restore after HA restart
4. ✅ Energy Dashboard accepts the sensors
5. 📊 Actual power consumption values (for validation)
6. 🐛 Any errors in logs

## Next Steps After Testing

Once confirmed working:
1. Remove Powercalc sensors for VSR (if you were using them)
2. Update Energy Dashboard to use native sensors
3. Monitor for 24-48 hours to verify stability
4. Report any issues or unexpected behavior