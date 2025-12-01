# Analysis of Working Systemair Integration - Key Findings

## CRITICAL DISCOVERY: Preset Mode Mapping Offset

### The Problem
In the working example project, there's a **-1 offset** between the command values and status values for preset modes!

### Evidence from `example/systemair-main/custom_components/systemair/climate.py`

**Line 44-58: Command Map (What to WRITE)**
```python
PRESET_MODE_TO_VALUE_MAP = {
    PRESET_MODE_AUTO: 1,
    PRESET_MODE_MANUAL: 2,
    PRESET_MODE_CROWDED: 3,
    PRESET_MODE_REFRESH: 4,
    PRESET_MODE_FIREPLACE: 5,
    PRESET_MODE_AWAY: 6,
    PRESET_MODE_HOLIDAY: 7,
    PRESET_MODE_COOKER_HOOD: 8,
    PRESET_MODE_VACUUM_CLEANER: 9,
    PRESET_MODE_CDI1: 10,
    PRESET_MODE_CDI2: 11,
    PRESET_MODE_CDI3: 12,
    PRESET_MODE_PRESSURE_GUARD: 13,
}
```

**Line 60: Status Map (What to READ) - THE KEY LINE!**
```python
VALUE_TO_PRESET_MODE_MAP = {value - 1: key for key, value in PRESET_MODE_TO_VALUE_MAP.items()}
```

**This creates:**
- Status 0 → "auto" (command was 1)
- Status 1 → "manual" (command was 2)
- Status 2 → "crowded" (command was 3)
- Status 3 → "refresh" (command was 4)
- Status 4 → "fireplace" (command was 5)
- Status 5 → "away" (command was 6)
- Status 6 → "holiday" (command was 7)

### Registers Used

**Line 221 (Read Status):**
```python
mode = self.coordinator.get_modbus_data(parameter_map["REG_USERMODE_MODE"])
```
- Register: **1161** (Input Register) - from modbus.py line 475

**Line 229 (Write Command):**
```python
await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"], ventilation_mode)
```
- Register: **1162** (Holding Register) - from modbus.py line 487

### Register Definitions from modbus.py

**Line 472-482: Status Register**
```python
ModbusParameter(
    register=1161,
    sig=IntegerType.UINT,
    reg_type=RegisterType.Input,
    short="REG_USERMODE_MODE",
    description=(
        "Active User mode.\n0: Auto\n1: Manual\n2: Crowded\n3: Refresh\n4: Fireplace\n5: Away\n6: Holiday\n"
        "7: Cooker Hood\n8: Vacuum Cleaner\n9: CDI1\n10: CDI2\n11: CDI3\n12: PressureGuard"
    ),
    min_value=0,
    max_value=12,
)
```

**Line 484-493: Command Register**
```python
ModbusParameter(
    register=1162,
    sig=IntegerType.UINT,
    reg_type=RegisterType.Holding,
    short="REG_USERMODE_HMI_CHANGE_REQUEST",
    description=(
        "New desired user mode as requested by HMI\n1: Auto\n2: Manual\n3: Crowded\n4: Refresh\n5: Fireplace\n6: Away\n7: Holiday"
    ),
    min_value=1,
    max_value=7,
)
```

## Our Current Implementation Issues

### Current Registers (const.py)
- **READ:** `REG_MODE_MAIN_STATUS_IN = 1160` (Input Register)
- **WRITE:** `REG_MODE_MAIN_CMD = 1161` (Holding Register)

### Current Mapping (const.py line 117-126)
```python
PRESET_MAP = {
    2: "crowded",
    3: "refresh",
    4: "fireplace",
    5: "away",
    6: "holiday",
    7: "kitchen",
    8: "vacuum_cleaner"
}
```

**This is WRONG because:**
1. We're using the SAME map for both reading and writing
2. The example shows status values are offset by -1 from command values
3. We're missing "auto" and "manual" modes

## Solution Required

We need to:
1. Create **separate maps** for reading (status) and writing (command)
2. Apply the **-1 offset** for status values
3. Add missing modes: "auto" and "manual"
4. Verify we're using the correct registers (1161 for status, 1162 for command)

## Additional Features Found in Example

### 1. More Comprehensive Mode Support
- Auto mode
- Manual mode
- CDI1, CDI2, CDI3 (Configurable Digital Inputs)
- Pressure Guard mode
- Cooker Hood mode

### 2. Better Error Handling
- Uses `HomeAssistantError` for invalid values
- Proper async exception handling with `asyncio.exceptions.TimeoutError`

### 3. Dynamic HVAC Mode Detection
- Checks if heater/cooler are active to determine available HVAC modes
- Uses registers `REG_FUNCTION_ACTIVE_HEATER` and `REG_FUNCTION_ACTIVE_COOLER`

### 4. Modbus Parameter System
- Comprehensive parameter definitions with metadata
- Scale factors for temperature values
- Min/max value validation
- Boolean type handling
- 32-bit register combining

### 5. Multiple API Types Support
- Modbus TCP
- Modbus Serial (RS485)
- Web API (HTTP-based Modbus)
- All with unified interface

### 6. Robust Connection Handling
- Worker queue pattern for Modbus requests
- Exponential backoff retry logic
- Automatic reconnection on failures
- Request queuing to prevent concurrent access

## Next Steps

1. **Immediate Fix:** Implement separate status/command maps with -1 offset
2. **Register Verification:** Confirm we're using correct registers (might need to use 1161/1162 instead of 1160/1161)
3. **Add Missing Modes:** Include "auto" and "manual" at minimum
4. **Consider Refactoring:** Adopt the parameter system from example for better maintainability