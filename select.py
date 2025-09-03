from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN, PRESET_TO_VALUE, PRESET_MAP, REG_MODE_MAIN_CMD
from .coordinator import VSRCoordinator
from .hub import VSRHub

SELECT_DESC = SelectEntityDescription(
    key="vsr_preset_select",
    name="Preset Mode",
    entity_category=EntityCategory.CONFIG,
)

class VSRPresetSelect(CoordinatorEntity[VSRCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_options = list(PRESET_TO_VALUE.keys())

    def __init__(self, coordinator: VSRCoordinator, hub: VSRHub, device_info: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.hub = hub
        self.entity_description = SELECT_DESC
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_preset_select"
        self._attr_device_info = device_info

    @property
    def current_option(self) -> str | None:
        mode = self.coordinator.data.get("mode_main")
        return PRESET_MAP.get(mode)

    async def async_select_option(self, option: str) -> None:
        val = PRESET_TO_VALUE.get(option)
        if val is None:
            return
        if await self.hub.write_register(REG_MODE_MAIN_CMD, val):
            await self.coordinator.async_request_refresh()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    hub: VSRHub = data["hub"]
    device_info = data["device_info"]
    async_add_entities([VSRPresetSelect(coordinator, hub, device_info)])
