"""Modbus parameters for Systemair SAVE VSR ventilation units."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntegerType(Enum):
    """
    Enum class representing integer types for Modbus communication.

    Attributes
    ----------
        UINT (str): Unsigned integer type.
        INT (str): Signed integer type.
    """

    UINT = "UINT"
    INT = "INT"


class RegisterType(Enum):
    """
    Enum class representing the types of Modbus registers.

    Attributes
    ----------
        Input (str): Represents an input register.
        Holding (str): Represents a holding register.
    """

    Input = "Input"
    Holding = "Holding"


@dataclass(kw_only=True, frozen=True)
class ModbusParameter:
    """Describes a modbus register for Systemair SAVE VSR."""

    register: int
    sig: IntegerType
    reg_type: RegisterType
    short: str
    description: str
    min_value: int | None = None
    max_value: int | None = None
    boolean: bool | None = None
    scale_factor: int | None = None
    combine_with_32_bit: int | None = None


# Register definitions for SAVE VSR
# Only includes registers currently used in our integration
parameters_list = [
    # User modes - Status and Command
    ModbusParameter(
        register=1160,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_MODE_MAIN_STATUS_IN",
        description="Active User mode status (read): 0: Auto, 1: Manual, 2: Crowded, 3: Refresh, 4: Fireplace, 5: Away, 6: Holiday, 7: Kitchen, 8: Vacuum Cleaner",
        min_value=0,
        max_value=8,
    ),
    ModbusParameter(
        register=1161,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MODE_MAIN_CMD",
        description="User mode command (write): 1: Auto, 2: Manual, 3: Crowded, 4: Refresh, 5: Fireplace, 6: Away, 7: Holiday, 8: Kitchen, 9: Vacuum Cleaner",
        min_value=1,
        max_value=9,
    ),
    ModbusParameter(
        register=1130,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MODE_SPEED",
        description="Fan speed level: 2: Low, 3: Medium, 4: High",
        min_value=2,
        max_value=4,
    ),
    # User mode durations
    ModbusParameter(
        register=1100,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_HOLIDAY_DAYS",
        description="Time delay setting for user mode Holiday (days)",
        min_value=1,
        max_value=365,
    ),
    ModbusParameter(
        register=1101,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_AWAY_HOURS",
        description="Time delay setting for user mode Away (hours)",
        min_value=1,
        max_value=72,
    ),
    ModbusParameter(
        register=1102,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_FIREPLACE_MINS",
        description="Time delay setting for user mode Fire Place (minutes)",
        min_value=1,
        max_value=60,
    ),
    ModbusParameter(
        register=1103,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_REFRESH_MINS",
        description="Time delay setting for user mode Refresh (minutes)",
        min_value=1,
        max_value=240,
    ),
    ModbusParameter(
        register=1104,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_CROWDED_HOURS",
        description="Time delay setting for user mode Crowded (hours)",
        min_value=1,
        max_value=8,
    ),
    # User mode remaining time (32-bit)
    ModbusParameter(
        register=1110,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_USERMODE_REMAIN",
        description="Remaining time for user mode, lower 16 bits (seconds)",
        combine_with_32_bit=1111,
    ),
    ModbusParameter(
        register=1111,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_USERMODE_FACTOR",
        description="Remaining time for user mode, higher 16 bits (seconds)",
        combine_with_32_bit=1110,
    ),
    # Temperature control
    ModbusParameter(
        register=2000,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TARGET_TEMP",
        description="Temperature setpoint for supply air (°C × 10)",
        scale_factor=10,
        min_value=120,
        max_value=300,
    ),
    # Temperature sensors
    ModbusParameter(
        register=12101,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TEMP_OUTDOOR",
        description="Outdoor Air Temperature (°C × 10)",
        scale_factor=10,
    ),
    ModbusParameter(
        register=12102,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TEMP_SUPPLY",
        description="Supply Air Temperature (°C × 10)",
        scale_factor=10,
    ),
    ModbusParameter(
        register=12543,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TEMP_EXHAUST",
        description="Exhaust Air Temperature (°C × 10)",
        scale_factor=10,
    ),
    ModbusParameter(
        register=12542,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TEMP_EXTRACT",
        description="Extract Air Temperature (°C × 10)",
        scale_factor=10,
    ),
    ModbusParameter(
        register=12107,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TEMP_OVERHEAT",
        description="Overheat Temperature (°C × 10)",
        scale_factor=10,
    ),
    ModbusParameter(
        register=12106,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_TEMP_EFFICENCY",
        description="Efficiency Temperature (°C × 10)",
        scale_factor=10,
    ),
    # Fan RPM and percentages
    ModbusParameter(
        register=12400,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_SAF_RPM",
        description="Supply Air Fan RPM",
    ),
    ModbusParameter(
        register=12401,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_EAF_RPM",
        description="Extract Air Fan RPM",
    ),
    ModbusParameter(
        register=14000,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_SUPPLY_FAN_PCT",
        description="Supply air fan speed (%)",
        min_value=0,
        max_value=100,
    ),
    ModbusParameter(
        register=14001,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_EXTRACT_FAN_PCT",
        description="Extract air fan speed (%)",
        min_value=0,
        max_value=100,
    ),
    # Heater and heat exchanger
    ModbusParameter(
        register=2148,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_HEATER_PERCENT",
        description="Heater output (%)",
        min_value=0,
        max_value=100,
    ),
    ModbusParameter(
        register=14102,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_HEAT_EXCH_STATE",
        description="Heat exchanger state",
        boolean=True,
    ),
    ModbusParameter(
        register=14350,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_ROTOR",
        description="Rotor speed/state",
    ),
    ModbusParameter(
        register=14101,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_HEATER",
        description="Heater state",
        boolean=True,
    ),
    # Moisture
    ModbusParameter(
        register=12135,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MOIST_RELEASE",
        description="Moisture release (%)",
        min_value=0,
        max_value=100,
    ),
    ModbusParameter(
        register=2210,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MOIST_CALC_EXT",
        description="Calculated extract moisture (%)",
        min_value=0,
        max_value=100,
    ),
    ModbusParameter(
        register=2211,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MOIST_CALC_INT",
        description="Calculated internal moisture (%)",
        min_value=0,
        max_value=100,
    ),
    ModbusParameter(
        register=2202,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MOIST_EXT_SP",
        description="Extract moisture setpoint (%)",
        min_value=0,
        max_value=100,
    ),
    # ECO mode
    ModbusParameter(
        register=2503,
        sig=IntegerType.INT,
        reg_type=RegisterType.Holding,
        short="REG_SETPOINT_ECO_OFFSET",
        description="ECO mode temperature offset (°C × 10)",
        scale_factor=10,
        min_value=0,
        max_value=100,
    ),
    # Binary states
    ModbusParameter(
        register=1038,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_MODE_SUMMERWINTER",
        description="Summer/Winter mode",
        boolean=True,
    ),
    ModbusParameter(
        register=1350,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_FAN_RUNNING_START",
        description="Fan running status",
        boolean=True,
    ),
    ModbusParameter(
        register=14003,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_DAMPER_STATE",
        description="Damper state",
        boolean=True,
    ),
    ModbusParameter(
        register=2133,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_COOLING_RECOVERY",
        description="Cooling recovery",
        boolean=True,
    ),
    # Switches (enable/disable features)
    ModbusParameter(
        register=2504,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_ECO_MODE_ENABLE",
        description="ECO mode enable",
        boolean=True,
    ),
    ModbusParameter(
        register=3001,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_HEATER_ENABLE",
        description="Heater enable",
        boolean=True,
    ),
    ModbusParameter(
        register=2203,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short="REG_RH_TRANSFER_ENABLE",
        description="RH transfer enable",
        boolean=True,
    ),
    # Alarm type indicators
    ModbusParameter(
        register=15900,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_TYPE_A",
        description="Alarm Type A active",
        boolean=True,
    ),
    ModbusParameter(
        register=15901,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_TYPE_B",
        description="Alarm Type B active",
        boolean=True,
    ),
    ModbusParameter(
        register=15902,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_TYPE_C",
        description="Alarm Type C active",
        boolean=True,
    ),
    # Individual alarms (0: Inactive, 1: Active, 2: Waiting, 3: Cleared Error Active)
    ModbusParameter(
        register=15001,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_SAF",
        description="Supply air fan alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15008,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_EAF",
        description="Extract air fan alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15015,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_FROST_PROT",
        description="Frost protection alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15029,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_SAF_RPM",
        description="Supply air fan RPM alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15036,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_EAF_RPM",
        description="Extract air fan RPM alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15057,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_FPT",
        description="Frost protection temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15064,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_OAT",
        description="Outdoor air temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15071,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_SAT",
        description="Supply air temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15078,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_RAT",
        description="Room air temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15085,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_EAT",
        description="Extract air temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15092,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_ECT",
        description="Extra controller temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15099,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_EFT",
        description="Efficiency temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15106,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_OHT",
        description="Overheat temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15113,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_EMT",
        description="Emergency thermostat alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15127,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_BYS",
        description="Bypass damper alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15134,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_SEC_AIR",
        description="Secondary air alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15141,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_FILTER",
        description="Filter alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15162,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_RH",
        description="Relative humidity alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15176,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_LOW_SAT",
        description="Low supply air temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15508,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_PDM_RHS",
        description="PDM RHS sensor alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15515,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_PDM_EAT",
        description="PDM EAT sensor alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15522,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_MAN_FAN_STOP",
        description="Manual fan stop alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15529,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_OVERHEAT_TEMP",
        description="Overheat temperature alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15536,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_FIRE",
        description="Fire alarm",
        min_value=0,
        max_value=3,
    ),
    ModbusParameter(
        register=15543,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Input,
        short="REG_ALARM_FILTER_WARN",
        description="Filter warning alarm",
        min_value=0,
        max_value=3,
    ),
]


# Create parameter map for easy lookup by short name
parameter_map = {param.short: param for param in parameters_list}