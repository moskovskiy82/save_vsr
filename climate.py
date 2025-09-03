from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REG_MODE_MAIN_CMD, REG_MODE_SPEED, REG_TARGET_TEMP, FAN_SPEED_TO_VALUE, FAN_SPEED_MAP, PRESET_TO_VALUE, PRESET_MAP
from .coordinator import VSRCoordinator
from .hub import VSRHub

PRESET_LIST = list(PRESET_TO_VALUE.keys())

class VSRClimate(CoordinatorEntity[VSRCoordinator], ClimateEntity):
    _attr_has_entity_name = True
    _attr_name = "Ventilation"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["low", "medium", "high"]
    _attr_preset_modes = PRESET_LIST

    def __init__(self, coordinator: VSRCoordinator, hub: VSRHub, device_info: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.hub = hub
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_climate"
        self._attr_device_info = device_info

    @property
    def current_temperature(self):
        return self.coordinator.data.get("temp_supply")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("target_temp")

    @property
    def hvac_mode(self):
        mode = self.coordinator.data.get("mode_main")
        if mode == 6:  # holiday in some firmwares means 'off'? stick to prior behavior
            return HVACMode.OFF
        if mode == 0:
            return HVACMode.AUTO
        if mode == 1:
            return HVACMode.FAN_ONLY
        # If a preset is active, we still report FAN_ONLY as action but AUTO as mode
        return HVACMode.AUTO

    @property
    def hvac_action(self):
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        return HVACAction.FAN

    @property
    def fan_mode(self):
        speed = self.coordinator.data.get("mode_speed")
        return FAN_SPEED_MAP.get(speed, "low")

    async def async_set_fan_mode(self, fan_mode: str):
        val = FAN_SPEED_TO_VALUE.get(fan_mode)
        if val is None:
            return
        if await self.hub.write_register(REG_MODE_SPEED, val):
            await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        value = int(round(float(temp) * 10))
        if await self.hub.write_register(REG_TARGET_TEMP, value):
            await self.coordinator.async_request_refresh()

    @property
    def preset_mode(self):
        mode = self.coordinator.data.get("mode_main")
        return PRESET_MAP.get(mode)

    async def async_set_preset_mode(self, preset_mode: str):
        val = PRESET_TO_VALUE.get(preset_mode)
        if val is None:
            return
        if await self.hub.write_register(REG_MODE_MAIN_CMD, val):
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        # Keep mapping aligned with your earlier code
        mapping = {HVACMode.OFF: 7, HVACMode.AUTO: 1, HVACMode.FAN_ONLY: 2}
        value = mapping.get(hvac_mode)
        if value is None:
            return
        if await self.hub.write_register(REG_MODE_MAIN_CMD, value):
            await self.coordinator.async_request_refresh()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    hub: VSRHub = data["hub"]
    device_info = data["device_info"]
    async_add_entities([VSRClimate(coordinator, hub, device_info)])
