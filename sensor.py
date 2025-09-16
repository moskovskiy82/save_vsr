# sensor.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPower,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ALARM_VALUE_TO_STATE,
)
from .coordinator import VSRCoordinator


@dataclass(frozen=True, kw_only=True)
class VSRSensorDescription(SensorEntityDescription):
    coordinator_key: str


SENSORS: tuple[VSRSensorDescription, ...] = (
    # Mode / Speed
    VSRSensorDescription(
        key="mode_speed",
        name="Mode Speed",
        device_class=SensorDeviceClass.ENUM,
        options=["low", "medium", "high"],
        coordinator_key="mode_speed",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VSRSensorDescription(
        key="mode_main_status",
        name="Mode Main Status",
        coordinator_key="mode_main",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VSRSensorDescription(
        key="target_temp",
        name="Target Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="target_temp",
    ),

    # Temperatures
    VSRSensorDescription(
        key="temp_outdoor",
        name="Temperature Outdoor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_outdoor",
    ),
    VSRSensorDescription(
        key="temp_supply",
        name="Temperature Supply",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_supply",
    ),
    VSRSensorDescription(
        key="temp_exhaust",
        name="Temperature Exhaust",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_exhaust",
    ),
    VSRSensorDescription(
        key="temp_overheat",
        name="Temperature Overheat",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_overheat",
    ),

    # Fans / RPM / Percentages
    VSRSensorDescription(
        key="saf_rpm",
        name="Fan Supply RPM",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="saf_rpm",
    ),
    VSRSensorDescription(
        key="eaf_rpm",
        name="Fan Extract RPM",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="eaf_rpm",
    ),
    VSRSensorDescription(
        key="fan_supply",
        name="Fan Supply %",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="fan_supply",
    ),
    VSRSensorDescription(
        key="fan_extract",
        name="Fan Extract %",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="fan_extract",
    ),
    VSRSensorDescription(
        key="heater_percentage",
        name="Heater %",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="heater_percentage",
    ),
    # Rotor as percentage (not diagnostic)
    VSRSensorDescription(
        key="rotor",
        name="Rotor %",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="rotor",
    ),

    # Power Sensors (Energy Dashboard Compatible)
    VSRSensorDescription(
        key="supply_fan_power",
        name="Fan Supply Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="fan_supply",
    ),
    VSRSensorDescription(
        key="extract_fan_power",
        name="Fan Extract Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="fan_extract",
    ),
    VSRSensorDescription(
        key="heater_power",
        name="Heater Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="heater_percentage",
    ),
    VSRSensorDescription(
        key="total_power",
        name="VSR Power Consumption",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="total_power",
    ),

    # ECO Offset
    VSRSensorDescription(
        key="setpoint_eco_offset",
        name="ECO Offset",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_key="setpoint_eco_offset",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Countdown Raw (Diagnostics)
    VSRSensorDescription(
        key="countdown_time_s",
        name="Countdown Remaining (s)",
        coordinator_key="countdown_time_s",
    ),
    VSRSensorDescription(
        key="countdown_time_s_factor",
        name="Countdown Factor",
        coordinator_key="countdown_time_s_factor",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # Modbus Failures (Diagnostics)
    VSRSensorDescription(
        key="modbus_failures",
        name="Modbus Failures",
        state_class=SensorStateClass.TOTAL_INCREASING,
        coordinator_key="modbus_failures",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


@dataclass(frozen=True, kw_only=True)
class VSRAlarmDescription(SensorEntityDescription):
    coordinator_key: str


ALARM_SENSORS: tuple[VSRAlarmDescription, ...] = tuple(
    VSRAlarmDescription(
        key=k,
        name=n,
        device_class=SensorDeviceClass.ENUM,
        options=["Inactive", "Active", "Waiting", "Cleared Error Active"],
        coordinator_key=k,
        entity_category=EntityCategory.DIAGNOSTIC,
    )
    for k, n in [
        ("alarm_typeA", "Alarm Type A"),
        ("alarm_typeB", "Alarm Type B"),
        ("alarm_typeC", "Alarm Type C"),
        ("alarm_saf", "Alarm SAF"),
        ("alarm_eaf", "Alarm EAF"),
        ("alarm_frost_protect", "Alarm Frost Protect"),
        ("alarm_saf_rpm", "Alarm SAF RPM"),
        ("alarm_eaf_rpm", "Alarm EAF RPM"),
        ("alarm_fpt", "Alarm FPT"),
        ("alarm_oat", "Alarm OAT"),
        ("alarm_sat", "Alarm SAT"),
        ("alarm_rat", "Alarm RAT"),
        ("alarm_eat", "Alarm EAT"),
        ("alarm_ect", "Alarm ECT"),
        ("alarm_eft", "Alarm EFT"),
        ("alarm_oht", "Alarm OHT"),
        ("alarm_emt", "Alarm EMT"),
        ("alarm_bys", "Alarm BYS"),
        ("alarm_sec_air", "Alarm Sec Air"),
        ("alarm_filter", "Alarm Filter"),
        ("alarm_rh", "Alarm RH"),
        ("alarm_low_SAT", "Alarm Low SAT"),
        ("alarm_pdm_rhs", "Alarm PDM RHS"),
        ("alarm_pdm_eat", "Alarm PDM EAT"),
        ("alarm_man_fan_stop", "Alarm Manual Fan Stop"),
        ("alarm_overheat_temp", "Alarm Overheat Temp"),
        ("alarm_fire", "Alarm Fire"),
        ("alarm_filter_warn", "Alarm Filter Warn"),
    ]
)


@dataclass(frozen=True, kw_only=True)
class VSRCountdownDescription(SensorEntityDescription):
    coordinator_key: str
    target_mode: int


COUNTDOWN_SENSORS: tuple[VSRCountdownDescription, ...] = (
    VSRCountdownDescription(key="away_countdown", name="Away Time Remaining", coordinator_key="mode_main", target_mode=5, entity_category=EntityCategory.DIAGNOSTIC),
    VSRCountdownDescription(key="crowded_countdown", name="Crowded Time Remaining", coordinator_key="mode_main", target_mode=2, entity_category=EntityCategory.DIAGNOSTIC),
    VSRCountdownDescription(key="refresh_countdown", name="Refresh Time Remaining", coordinator_key="mode_main", target_mode=3, entity_category=EntityCategory.DIAGNOSTIC),
    VSRCountdownDescription(key="fireplace_countdown", name="Fireplace Time Remaining", coordinator_key="mode_main", target_mode=4, entity_category=EntityCategory.DIAGNOSTIC),
    VSRCountdownDescription(key="holiday_countdown", name="Holiday Time Remaining", coordinator_key="mode_main", target_mode=6, entity_category=EntityCategory.DIAGNOSTIC),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    device_info = data["device_info"]

    entities: list[SensorEntity] = []

    for desc in SENSORS:
        entities.append(VSRSensor(coordinator, desc, device_info))

    for desc in ALARM_SENSORS:
        entities.append(VSRAlarmSensor(coordinator, desc, device_info))

    for desc in COUNTDOWN_SENSORS:
        entities.append(VSRCountdownSensor(coordinator, desc, device_info))

    async_add_entities(entities)


class VSRBaseSensor(CoordinatorEntity[VSRCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VSRCoordinator, description: SensorEntityDescription, device_info: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = device_info


class VSRSensor(VSRBaseSensor):
    @property
    def native_value(self) -> Any:
        key = getattr(self.entity_description, "coordinator_key")
        value = self.coordinator.data.get(key)

        # Map mode_speed raw -> enum text
        if self.entity_description.key == "mode_speed":
            raw = self.coordinator.data.get("mode_speed")
            return {2: "low", 3: "medium", 4: "high"}.get(raw, "low")

        # Power sensors calculations (defensive)
        if self.entity_description.key == "supply_fan_power":
            supply_pct = self.coordinator.data.get("fan_supply")
            if supply_pct is None:
                return None
            return round((supply_pct / 100) * 160, 1)
        if self.entity_description.key == "extract_fan_power":
            extract_pct = self.coordinator.data.get("fan_extract")
            if extract_pct is None:
                return None
            return round((extract_pct / 100) * 160, 1)
        if self.entity_description.key == "heater_power":
            heater_pct = self.coordinator.data.get("heater_percentage")
            if heater_pct is None:
                return None
            return round((heater_pct / 100) * 1650, 1)
        if self.entity_description.key == "total_power":
            supply_pct = self.coordinator.data.get("fan_supply") or 0
            extract_pct = self.coordinator.data.get("fan_extract") or 0
            heater_pct = self.coordinator.data.get("heater_percentage") or 0
            supply = (supply_pct / 100) * 160
            extract = (extract_pct / 100) * 160
            heater = (heater_pct / 100) * 1650
            return round(supply + extract + heater, 1)

        return value


class VSRAlarmSensor(VSRBaseSensor):
    @property
    def native_value(self) -> str | None:
        key = getattr(self.entity_description, "coordinator_key")
        raw = int(self.coordinator.data.get(key, 0))
        return ALARM_VALUE_TO_STATE.get(raw, "Inactive")


class VSRCountdownSensor(VSRBaseSensor):
    @property
    def native_value(self) -> str:
        mode = self.coordinator.data.get("mode_main", 0)
        desc: VSRCountdownDescription = self.entity_description  # type: ignore[assignment]
        if mode != desc.target_mode:
            return "Inactive"

        time_s = int(self.coordinator.data.get("countdown_time_s", 0))
        factor = int(self.coordinator.data.get("countdown_time_s_factor", 0))
        total = time_s + factor * 65535 if desc.target_mode == 6 else time_s

        if total < 60:
            return "Less than 1 min"

        days = total // 86400
        hours = (total % 86400) // 3600
        minutes = (total % 3600) // 60

        if days > 0:
            return f"{days} days"
        if hours > 0 and minutes > 0:
            return f"{hours} h {minutes} min"
        if hours > 0:
            return f"{hours} h"
        return f"{minutes} min"
