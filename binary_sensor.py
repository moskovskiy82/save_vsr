from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .coordinator import VSRCoordinator

@dataclass(frozen=True, kw_only=True)
class VSRBinaryDescription(BinarySensorEntityDescription):
    coordinator_key: str

BINARY_SENSORS: tuple[VSRBinaryDescription, ...] = (
    VSRBinaryDescription(key="damper_state", name="Damper Open", device_class=BinarySensorDeviceClass.OPENING, coordinator_key="damper_state"),
    VSRBinaryDescription(key="cooldown", name="Cooldown", device_class=BinarySensorDeviceClass.COLD, coordinator_key="cooldown", entity_category=EntityCategory.DIAGNOSTIC),
    VSRBinaryDescription(key="mode_summerwinter", name="Summer/Winter Mode", device_class=BinarySensorDeviceClass.HEAT, coordinator_key="mode_summerwinter", entity_category=EntityCategory.DIAGNOSTIC),
    VSRBinaryDescription(key="fan_running", name="Fan Running", device_class=BinarySensorDeviceClass.RUNNING, coordinator_key="fan_running"),
    VSRBinaryDescription(key="cooling_recovery", name="Cooling Recovery", device_class=BinarySensorDeviceClass.COLD, coordinator_key="cooling_recovery", entity_category=EntityCategory.DIAGNOSTIC),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    device_info = data["device_info"]

    entities: list[BinarySensorEntity] = [VSRBinarySensor(coordinator, desc, device_info) for desc in BINARY_SENSORS]
    async_add_entities(entities)

class VSRBinarySensor(CoordinatorEntity[VSRCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VSRCoordinator, description: VSRBinaryDescription, device_info: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool | None:
        key = getattr(self.entity_description, "coordinator_key")
        value = self.coordinator.data.get(key)
        if value is None:
            return None
        return bool(value)
