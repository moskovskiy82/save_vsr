# Systemair SAVE VSR Integration - Development Roadmap

## ✅ Version 2.2 (COMPLETED)
**Critical Fix: Preset Mode Mismatch**

### Problem Solved
Preset modes were not working correctly - selecting "Fireplace" would activate "Crowded" instead.

### Root Cause
- Command values (write to register 1161) and Status values (read from register 1160) have **-1 offset**
- Example: Writing command `5` (Fireplace) results in status `4` being read back
- We were using the same mapping for both operations

### Solution Implemented
- Created separate mappings:
  - `PRESET_COMMAND_MAP` - for writing commands
  - `PRESET_STATUS_MAP` - for reading status (offset by -1)
- Added missing modes: "auto" and "manual"
- Enhanced logging to track command/status values

### Files Changed
- `const.py` - Added separate command/status maps
- `climate.py` - Updated to use correct maps for read/write operations
- `CONTEXT_NEXT_PHASE.md` - This roadmap document

---

## 📋 Version 2.3 (PLANNED - Next Release)

### 1. Add Integration Icon ⭐ HIGH PRIORITY
**Source:** `example/systemair-main/custom_components/systemair/icons.json`

The example project has a proper icon system. We need to:
- Copy icon configuration from example
- Add brand icons (logo.png, icon.png already exist in `/branding/`)
- Implement icons.json for entity icons
- Test icon display in HA UI

**Files to create/modify:**
- `icons.json` - Entity icon mappings
- Update `manifest.json` if needed

### 2. Enhanced Error Handling
**Source:** Example project's error handling patterns

- Add `HomeAssistantError` for invalid values
- Implement proper `asyncio.exceptions.TimeoutError` handling
- Better user feedback on connection failures

**Files to modify:**
- `climate.py` - Add error classes
- `hub.py` - Improve connection error messages

### 3. Additional Preset Modes
**Source:** `example/systemair-main/custom_components/systemair/const.py`

Add support for:
- Cooker Hood mode
- CDI1, CDI2, CDI3 (Configurable Digital Inputs)
- Pressure Guard mode

**Files to modify:**
- `const.py` - Add new preset definitions
- `climate.py` - Update preset list

---

## 📋 Version 2.4 (PLANNED)

### 1. Dynamic HVAC Mode Detection
**Source:** `example/systemair-main/custom_components/systemair/climate.py` lines 123-129

Automatically detect available HVAC modes based on hardware:
- Check `REG_FUNCTION_ACTIVE_HEATER` to enable HEAT mode
- Check `REG_FUNCTION_ACTIVE_COOLER` to enable COOL mode
- Only show modes that hardware supports

**Files to modify:**
- `const.py` - Add heater/cooler detection registers
- `climate.py` - Implement dynamic mode detection
- `coordinator.py` - Read heater/cooler status

### 2. Improved Temperature Handling
**Source:** Example project's scale factor system

- Implement proper scale factors for all temperature sensors
- Add validation for min/max values
- Better precision handling

**Files to modify:**
- `const.py` - Add scale factor definitions
- `coordinator.py` - Apply scale factors when reading

---

## 📋 Version 3.0 (FUTURE - Major Refactoring)

### 1. Modbus Parameter System
**Source:** `example/systemair-main/custom_components/systemair/modbus.py`

Complete refactoring to use parameter-based system:
- Define all registers with metadata (ModbusParameter dataclass)
- Automatic type conversion (INT/UINT)
- Built-in validation (min/max values)
- Scale factor support
- Boolean type handling
- 32-bit register combining

**Benefits:**
- Easier to add new sensors/controls
- Self-documenting code
- Automatic validation
- Type safety

**Files to create/modify:**
- `modbus.py` - New parameter definition system
- `const.py` - Migrate to parameter references
- `coordinator.py` - Use parameter system for reads/writes
- All entity files - Update to use parameters

### 2. Multiple Transport Support
**Source:** `example/systemair-main/custom_components/systemair/api.py`

Add support for:
- **Modbus TCP** (current - keep)
- **Modbus Serial (RS485)** - Direct serial connection
- **Web API** - HTTP-based Modbus for units with web interface

**Benefits:**
- Support more hardware configurations
- Easier setup for users with different connection types
- Unified interface for all transport types

**Files to create/modify:**
- `api.py` - New transport abstraction layer
- `config_flow.py` - Add transport selection
- `hub.py` - Refactor to use transport layer

### 3. Advanced Connection Management
**Source:** Example project's worker queue pattern

- Worker queue for Modbus requests
- Exponential backoff retry logic
- Automatic reconnection on failures
- Request queuing to prevent concurrent access
- Better handling of device busy states

**Files to modify:**
- `hub.py` - Implement worker queue pattern
- `coordinator.py` - Use queued requests

---

## 🎯 Priority Order

### Immediate (v2.3)
1. ⭐ **Add Integration Icon** - Visual polish, easy win
2. Enhanced Error Handling - Better UX
3. Additional Preset Modes - More functionality

### Short-term (v2.4)
1. Dynamic HVAC Mode Detection - Hardware-aware
2. Improved Temperature Handling - Better accuracy

### Long-term (v3.0)
1. Modbus Parameter System - Foundation for future
2. Multiple Transport Support - Broader compatibility
3. Advanced Connection Management - Reliability

---

## 📝 Notes

### Icon Implementation Details
The example project uses:
- `icons.json` for entity-specific icons
- MDI (Material Design Icons) references
- Custom icons for different states

Example structure:
```json
{
  "entity": {
    "climate": {
      "default": "mdi:air-filter"
    }
  }
}
```

### Testing Checklist for Each Version
- [ ] All preset modes work correctly
- [ ] Temperature readings accurate
- [ ] Fan speed control works
- [ ] HVAC modes function properly
- [ ] Icons display correctly (v2.3+)
- [ ] Error messages are clear
- [ ] No regression in existing features
- [ ] Documentation updated

---

## 🔗 References

- **Example Project:** `example/systemair-main/`
- **Modbus Documentation:** `example/systemair-main/docs/SAVE_MODBUS_VARIABLE_LIST_20210301_REV36.pdf`
- **Current Branding:** `/branding/icon.png`, `/branding/logo.png`