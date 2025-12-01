# Systemair SAVE VSR - Development Roadmap

## 📊 Progress Tracking

| Phase | Task | Status | Priority |
|-------|------|--------|----------|
| 2.4 | Add Integration Logo | ✅ Completed | ⭐⭐ HIGH |
| 3.1 | Create modbus.py | ✅ Completed | ⭐⭐⭐ CRITICAL |
| 3.2 | Refactor coordinator.py | ✅ Completed | ⭐⭐⭐ CRITICAL |
| 3.2.2 | Localize preset names | ⏳ Pending | ⭐⭐ HIGH |
| 4.1 | Energy Dashboard | ✅ Completed | ⭐⭐ HIGH |
| 4.2 | Alarm History | ⏳ Pending | ⭐ MEDIUM |
| 4.3 | Virtual Efficiency | ⏳ Pending | ⭐ MEDIUM |
| 5.1 | ML Anomaly Detection | ⏳ Future | ⭐ LOW |

**Last Updated:** 2025-12-01 23:27 MSK
**Current Focus:** Phase 4.1 ✅ COMPLETED - Testing Energy Dashboard

## 📊 Missing Features Analysis

Detailed comparison with reference integration (`example/systemair-main/`):

| Domain | Our Integration | Example Integration | Missing | Priority |
|--------|----------------|---------------------|---------|----------|
| **Sensors** | ~20 | ~35 | ~15 | ⭐⭐ HIGH |
| **Climate** | 3 presets | 13 presets | 10 | ⭐⭐ HIGH |
| **Switches** | 3 | 5 | 2 | ⭐ MEDIUM |
| **Binary Sensors** | 5 | ~25 | ~20 | ⭐ MEDIUM |
| **Select** | 1 | 6 | 5 | ⭐ MEDIUM |
| **Number** | 6 | 24 | 18 | ⭐ LOW |
| **Button** | 0 | 1 | 1 | ⭐ LOW |
| **TOTAL** | **~38** | **~109** | **~71** | - |

**Documentation:** See [`missing/`](missing/) directory for detailed breakdown by domain.

**Key Missing Features:**
- 🌡️ IAQ Level sensor, Humidity sensors (Supply/Extract/Outdoor)
- 🔄 Additional preset modes (Crowded, Refresh, Away, Holiday, etc.)
- ⚡ Free Cooling switch and configuration
- 🔔 Active function binary sensors (Heater, Cooler, Defrost)
- ⚙️ Temperature Control Mode, Fan Regulation Unit selects
- 🔢 Filter Period, Free Cooling schedule numbers

---

## 🎯 Implementation Order

### Week 1: Visual Polish
1. Add integration logo and icons
2. Test icon display in HA UI

### Week 2: Foundation
1. Create `modbus.py` with ModbusParameter system
2. Port all registers from `const.py`
3. Test that nothing breaks
ВАЖНО ты используешь entity Только из нашей интеграции. Это принципиально важно чтобы имена entity_ids не менялись! Потом уже будем добавлять entity из кода example



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

## ✅ Version 3.2.1 (CURRENT)

**Status:** Stable release
**Features:**
- ✅ ModbusParameter system in modbus.py
- ✅ Refactored coordinator.py with get_modbus_data()
- ✅ Cleaner code, easier maintenance
- ✅ All sensors working
- ✅ Climate control functional

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

### Phase 3.2.2: Localize Preset Names ⭐⭐
**Time:** 1 hour | **Version:** 3.2.2

**Problem:**
Current preset names are in English and not intuitive:
- `fireplace` - unclear what it does
- `refresh` - unclear what it does
- `crowded` - unclear what it does

**Solution:**
Rename presets to Russian names that clearly describe their purpose:
- `fireplace` → `камин` (Камин - for fireplace mode, closes damper)
- `refresh` → `форточка` (Форточка - like opening a window, fresh air boost)
- `crowded` → `максимум` (Максимум - maximum ventilation for many people)

**Implementation:**
1. Update `const.py`:
   - Modify `PRESET_COMMAND_MAP` keys
   - Modify `PRESET_STATUS_MAP` values
   - Keep internal values (1-9) unchanged

2. Update `climate.py`:
   - Update `PRESET_MODES` list
   - Ensure backward compatibility

3. Update `translations/en.json`:
   - Add Russian preset names
   - Keep English as fallback

**Files to modify:**
- `const.py` - Preset name mappings
- `climate.py` - Available preset modes
- `translations/en.json` - UI translations

**Testing:**
- [ ] Preset names show in Russian in UI
- [ ] Switching presets works correctly
- [ ] Device responds to preset changes
- [ ] No errors in logs

**Benefits:**
- ✅ Clear, intuitive names
- ✅ Better UX for Russian users
- ✅ Easier to understand what each mode does

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

**What it does:**
Sensor `sensor.vsr_alarm_history` shows last 10 alarms from device memory with timestamps.

**Current problem:**
- Existing alarm sensors only show CURRENT state (Active/Inactive)
- If alarm happened yesterday at 3 AM, you won't know about it

**Solution:**
- VSR stores last 10 alarms in registers 16001-16080 (10 × 8 registers)
- Each alarm record contains: ID, Status, Year, Month, Day, Hour, Minute, Second
- Sensor shows latest alarm as state + full history in attributes

**Example output:**
```
State: "Filter"
Attributes:
  history:
    - alarm: "Filter"
      status: "Active"
      timestamp: "2024-11-30 15:30:45"
    - alarm: "Frost protection"
      status: "Acknowledged"
      timestamp: "2024-11-28 03:15:20"
```

**Use cases:**
- Diagnostics: Why did ventilation stop last night?
- Prevention: Filter warning appeared 3 times → replace soon
- Automation: Send notification when specific alarm appears
- Statistics: Which alarms are most frequent?

**Implementation:**
1. Add `alarm_log_registers` to `modbus.py` (10 entries × 8 regs)
2. Add `ALARM_ID_TO_NAME_MAP` (35 alarm types: 0-34)
3. Create sensor that reads history and parses timestamps
4. Map alarm IDs to human-readable names

**Files:**
- MODIFY: `sensor.py`, `modbus.py`

**Priority:** MEDIUM - useful for diagnostics but not critical

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
