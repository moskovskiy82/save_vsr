# Systemair SAVE VSR - Development Roadmap

## 📊 Progress Tracking

| Phase | Task | Status | Priority |
|-------|------|--------|----------|
| 2.4 | Add Integration Logo | ✅ Completed | ⭐⭐ HIGH |
| 3.1 | Create modbus.py | ✅ Completed | ⭐⭐⭐ CRITICAL |
| 3.2 | Refactor coordinator.py | ✅ Completed | ⭐⭐⭐ CRITICAL |
| 3.2.2 | Localize preset names | ✅ Completed | ⭐⭐ HIGH |
| 4.1 | Energy Dashboard | ✅ Completed | ⭐⭐ HIGH |
| 4.2 | Alarm History | ⏳ Pending | ⭐ MEDIUM |
| 4.3 | Virtual Efficiency | ⏳ Pending | ⭐ MEDIUM |
| 5.1 | ML Anomaly Detection | ⏳ Future | ⭐ LOW |

**Last Updated:** 2025-12-02 17:00 MSK
**Current Focus:** Phase 4.2 ⏳ Pending - Alarm History

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

### Completed Phases
- **Week 1:** Visual Polish (Logo) ✅
- **Week 2:** Foundation (ModbusParameter) ✅
- **Week 3:** Core Refactoring (Coordinator) ✅
- **Week 4:** Energy Dashboard ✅

### Week 5+: Additional Features
1. Alarm history sensor (Phase 4.2)
2. Virtual efficiency sensor (Phase 4.3)
3. ML anomaly detection (Phase 5.1)

---

## 📋 Version 4.0 (Feature Expansion)

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

**START:** Phase 4.2 - Alarm History

Implement alarm history sensor to track last 10 alarms with timestamps.
