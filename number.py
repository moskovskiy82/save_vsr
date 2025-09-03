from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime, REVOLUTIONS_PER_MINUTE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_SETPOINT_ECO_OFFSET,
    REG_HOLIDAY_DAYS,
    REG_AWAY_HOURS,
    REG_FIREPLACE_MINS,
    REG_REFRESH_MINS,
    REG_CROWDED_HOURS,
)
from .coordinator import VSRCoordinator
from .hub import VSRHub

@dataclass(frozen=True, kw_only=True)
class VSRNumberDescription(NumberEntityDescription):
    coordinator_key: str
    write_register: int
    scale: float = 1.0
    value_to_reg: Optional[Callable[[float], int]] = None
    reg_to_value: Optional[Callable[[int], float]] = None
    min_value: float = 0.0
    max_value: float = 100.0
    step: float = 1.0

def tenth_to_reg(v: float) -> int:
    return int(round(v * 10))

def reg_to_tenth(v: int) -> float:
    return round(v * 0.1, 1)

NUMBERS: tuple[VSRNumberDescription, ...] = (
    # ECO offset 0..10°C, step 0.5
    VSRNumberDescription(
        key="eco_offset",
        name="Eco Offset",
        coordinator_key="setpoint_eco_offset",
        write_register=REG_SETPOINT_ECO_OFFSET,
        device_class=None,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        min_value=0.0,
        max_value=10.0,
        step=0.5,
        value_to_reg=tenth_to_reg,
        reg_to_value=reg_to_tenth,
        entity_category=EntityCategory.CONFIG,
    ),
    # Holiday duration (days)
    VSRNumberDescription(
        key="holiday_days",
        name="Holiday Duration",
        coordinator_key="holiday_days",
        write_register=REG_HOLIDAY_DAYS,
        native_unit_of_measurement=UnitOfTime.DAYS,
        min_value=1,
        max_value=365,
        step=1,
        entity_category=EntityCategory.CONFIG,
    ),
    # Away duration (hours)
    VSRNumberDescription(
        key="away_hours",
        name="Away Duration",
        coordinator_key="away_hours",
        write_register=REG_AWAY_HOURS,
        native_unit_of_measurement=UnitOfTime.HOURS,
        min_value=1,
        max_value=72,
        step=1,
        entity_category=EntityCategory.CONFIG,
    ),
    # Refresh (minutes)
    VSRNumberDescription(
        key="refresh_mins",
        name="Refresh Duration",
        coordinator_key="refresh_mins",
        write_register=REG_REFRESH_MINS,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        min_value=1,
        max_value=240,
        step=1,
        entity_category=EntityCategory.CONFIG,
    ),
    # Crowded (hours)
    VSRNumberDescription(
        key="crowded_hours",
        name="Crowded Duration",
        coordinator_key="crowded_hours",
        write_register=REG_CROWDED_HOURS,
        native_unit_of_measurement=UnitOfTime.HOURS,
        min_value=1,
        max_value=8,
        step=1,
        entity_category=EntityCategory.CONFIG,
    ),
    # Fireplace (minutes)
    VSRNumberDescription(
        key="fireplace_mins",
        name="Fireplace Duration",
        coordinator_key="fireplace_mins",
        write_register=REG_FIREPLACE_MINS,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        min_value=1,
        max_value=60,
        step=1,
        entity_category=EntityCategory.CONFIG,
    ),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    hub: VSRHub = data["hub"]
    device_info = data["device_info"]

    entities: list[NumberEntity] = [VSRNumber(coordinator, hub, desc, device_info) for desc in NUMBERS]
    async_add_entities(entities)

class VSRNumber(CoordinatorEntity[VSRCoordinator], NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VSRCoordinator, hub: VSRHub, description: VSRNumberDescription, device_info: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.hub = hub
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = device_info

        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self) -> float | None:
        key = self.entity_description.coordinator_key
        raw = self.coordinator.data.get(key)
        if raw is None:
            return None
        if self.entity_description.reg_to_value:
            return self.entity_description.reg_to_value(int(raw))
        return float(raw)

    async def async_set_native_value(self, value: float) -> None:
        if self.entity_description.value_to_reg:
            reg_value = self.entity_description.value_to_reg(value)
        else:
            reg_value = int(round(value))
        if await self.hub.write_register(self.entity_description.write_register, reg_value):
            await self.coordinator.async_request_refresh()
