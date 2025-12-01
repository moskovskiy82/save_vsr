# Systemair SAVE VSR - Development Roadmap

## 📊 Progress Tracking

| Phase | Task | Status | Priority |
|-------|------|--------|----------|
| 2.4 | Add Integration Logo | ⏳ Pending | ⭐⭐ HIGH |
| 3.1 | Create modbus.py | ⏳ Pending | ⭐⭐⭐ CRITICAL |
| 3.2 | Refactor coordinator.py | ⏳ Pending | ⭐⭐⭐ CRITICAL |
| 4.1 | Energy Dashboard | ⏳ Pending | ⭐⭐ HIGH |
| 4.2 | Alarm History | ⏳ Pending | ⭐ MEDIUM |
| 4.3 | Virtual Efficiency | ⏳ Pending | ⭐ MEDIUM |
| 5.1 | ML Anomaly Detection | ⏳ Future | ⭐ LOW |

---

## 🎯 Implementation Order

### Week 1: Visual Polish
1. Add integration logo and icons
2. Test icon display in HA UI

### Week 2: Foundation
1. Create `modbus.py` with ModbusParameter system
2. Port all registers from `const.py`
3. Test that nothing breaks

### Week 3: Core Refactoring
1. Refactor `coordinator.py` to use `get_modbus_data()`
2. Update all sensors to use new system
3. Remove manual decoding code

### Week 4: Energy Dashboard
1. Add `SystemairEnergySensor(RestoreSensor)`
2. Add MODEL_SPECS for VSR 500
3. Test energy tracking & persistence

### Week 5+: Additional Features
1. Alarm history sensor
2. Virtual efficiency sensor
3. ML anomaly detection (future)

---

## ✅ Version 2.3 (CURRENT)

**Status:** Stable release
**Features:**
- Preset mode fix (command/status offset)
- All basic sensors working
- Climate control functional

---

## 📋 Version 2.4 (NEXT - Quick Win)

### Add Integration Logo ⭐⭐
**Time:** 30 minutes | **Reference:** `example/.../icons.json`

**What to do:**
1. Update `icons.json` with entity icons
2. Verify logo files exist in `/branding/`
3. Test icon display in HA UI

**Files already exist:**
- `/branding/icon.png` ✅
- `/branding/logo.png` ✅

**Files to modify:**
- `icons.json` - Add entity icon mappings
- `manifest.json` - Verify icon configuration

**Example icons.json:**
```json
{
  "entity": {
    "climate": {
      "default": "mdi:air-filter"
    },
    "sensor": {
      "temperature": "mdi:thermometer",
      "fan": "mdi:fan"
    }
  }
}
```

---

## 📋 Version 3.0 (Major Refactoring)

### Phase 3.1: Create `modbus.py` ⭐⭐⭐
**Time:** 4-6 hours | **Reference:** `example/.../modbus.py`

**Create ModbusParameter dataclass:**
```python
@dataclass(kw_only=True, frozen=True)
class ModbusParameter:
    register: int              # 1-based address
    sig: IntegerType          # UINT/INT
    reg_type: RegisterType    # Input/Holding
    short: str                # "REG_SENSOR_OAT"
    description: str          # Human-readable
    min_value: int | None     # Validation
    max_value: int | None
    boolean: bool | None      # True/False register
    scale_factor: int | None  # Divide by (e.g., 10)
    combine_with_32_bit: int | None
```

**Benefits:**
- Auto type conversion (signed/unsigned)
- Auto scaling (no more `* 0.1`)
- Self-documenting
- Easy to add sensors

**Files:**
- CREATE: `modbus.py`
- MODIFY: `const.py` (keep only non-register constants)

---

### Phase 3.2: Refactor `coordinator.py` ⭐⭐⭐
**Time:** 2-3 hours

**Add method:**
```python
def get_modbus_data(self, param: ModbusParameter) -> float | bool:
    # Auto decode based on param metadata
    # - Check boolean → True/False
    # - Check sig → signed conversion
    # - Check scale_factor → divide
    # - Check combine_with_32_bit → combine registers
```

**Benefits:**
- No manual `to_signed16()`
- Cleaner code
- Fewer bugs

**Files:**
- MODIFY: `coordinator.py`

---

## 📋 Version 4.0 (Feature Expansion)

### Phase 4.1: Energy Dashboard ⭐⭐
**Time:** 3-4 hours | **Reference:** `example/.../sensor.py` (lines 556-611)

**Create:**
```python
class SystemairEnergySensor(RestoreSensor):
    # Track power × time
    # Persist across restarts
    # Integrate with HA Energy Dashboard
```

**Add MODEL_SPECS:**
```python
MODEL_SPECS = {
    "VSR 500": {
        "fan_power": 338,
        "heater_power": 1670,
        "supply_fans": 1,
        "extract_fans": 1
    }
}
```

**Files:**
- MODIFY: `sensor.py`, `const.py`

---

### Phase 4.2: Alarm History ⭐
**Time:** 2-3 hours | **Reference:** `example/.../sensor.py` (lines 458-495)

**What:**
- Parse alarm log registers (15000+)
- Show history in sensor attributes
- Map alarm IDs to names

**Files:**
- MODIFY: `sensor.py`, `modbus.py`

---

### Phase 4.3: Virtual Efficiency ⭐
**Time:** 1-2 hours

**Formula:**
```
Efficiency = (T_supply - T_outdoor) / (T_extract - T_outdoor) × 100%
```

**Why better than template:**
- Integrated (no YAML)
- Proper device class
- Better error handling

**Files:**
- MODIFY: `sensor.py`

---

## 📋 Version 5.0 (Future - ML)

### Phase 5.1: ML Anomaly Detection ⭐ (Future)
**Time:** 8-12 hours

**What:**
- Monitor RPM vs % power
- Detect filter clogging early
- Alert before alarm triggers

**Files:**
- CREATE: `ml_detector.py` (future)

---

## 💡 Quick Win Automations (No Code Needed)

### CO2 Control
```yaml
trigger: sensor.co2 > 1000
action: preset_mode = "crowded"
```

### Away Mode
```yaml
trigger: zone.home = 0 (30min)
action: preset_mode = "away"
```

### Night Mode
```yaml
trigger: time = 23:00
action: fan_speed_max = 40%
```

### Free Cooling
```yaml
trigger: outdoor_temp < indoor_temp (night)
action: free_cooling = on
```

---

## 📝 Testing Checklist

### After Each Phase
- [ ] All sensors work
- [ ] Preset modes correct
- [ ] Temps accurate
- [ ] Fan control works
- [ ] No HA errors
- [ ] Restart OK

### Energy Dashboard
- [ ] Appears in dashboard
- [ ] Power values reasonable
- [ ] Energy accumulates
- [ ] Persists after restart

---

## 🔗 References

- **Analysis:** [`gemini3.md`](gemini3.md) - Detailed comparison of both integrations
- **Reference Code:** `example/systemair-main/` - ⚠️ **Study only, DO NOT copy 1:1**
  - Learn architecture patterns (ModbusParameter, API layer)
  - Understand how they solve problems
  - Adapt concepts to our needs
- **Modbus Spec:** `example/systemair-main/docs/SAVE_MODBUS_*.pdf`

---

## 🚀 Next Action

**START:** Version 2.4 - Add Integration Logo

Quick visual improvement before major refactoring.
