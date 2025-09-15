# climate.py
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_MODE_MAIN_CMD,
    REG_MODE_SPEED,
    REG_TARGET_TEMP,
    FAN_SPEED_TO_VALUE,
    FAN_SPEED_MAP,
    PRESET_TO_VALUE,
    PRESET_MAP,
)
from .coordinator import VSRCoordinator

PRESET_LIST = list(PRESET_TO_VALUE.keys())


class VSRClimate(CoordinatorEntity[VSRCoordinator], ClimateEntity):
    """Climate entity for Systemair SAVE VSR."""

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
    _attr_min_temp = 12.0  # Typical VSR500 min setpoint
    _attr_max_temp = 30.0  # Typical VSR500 max setpoint
    _attr_target_temperature_step = 1.0  # Set increment to 1

    def __init__(self, coordinator: VSRCoordinator, device_info: dict[str, Any]) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self.hub = coordinator.hub
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_climate"
        self._attr_device_info = device_info

    # --- Read properties -------------------------------------------------

    @property
    def current_temperature(self) -> float | None:
        """Return the supply temperature (current)."""
        return self.coordinator.data.get("temp_supply")

    @property
    def target_temperature(self) -> float | None:
        """Return target / setpoint temperature."""
        temp = self.coordinator.data.get("target_temp")
        if temp is None:
            return None
        # Round to nearest integer for display with 0 decimals
        return round(temp)

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode based on mode_main register."""
        mode = self.coordinator.data.get("mode_main")
        if mode is None:
            return None  # Or default to HVACMode.AUTO if preferred
        if mode == 6:
            return HVACMode.OFF
        if mode == 0:
            return HVACMode.AUTO
        if mode == 1:
            return HVACMode.FAN_ONLY
        return HVACMode.AUTO

    @property
    def hvac_action(self) -> HVACAction:
        """Report the current action (simple mapping)."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        return HVACAction.FAN

    @property
    def fan_mode(self) -> str | None:
        """Return current fan mode (low/medium/high)."""
        speed = self.coordinator.data.get("mode_speed")
        if speed is None:
            return None
        return FAN_SPEED_MAP.get(speed)

    @property
    def preset_mode(self) -> str | None:
        """Return active preset (if any)."""
        mode = self.coordinator.data.get("mode_main")
        if mode is None:
            return None
        return PRESET_MAP.get(mode)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes for diagnostics."""
        return {
            "raw_mode_main": self.coordinator.data.get("mode_main"),
            "raw_mode_speed": self.coordinator.data.get("mode_speed"),
            "raw_target_temp": self.coordinator.data.get("target_temp"),
        }

    # --- Setters / commands ---------------------------------------------

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan speed (writes modbus register)."""
        val = FAN_SPEED_TO_VALUE.get(fan_mode)
        if val is None:
            return
        if await self.hub.write_register(REG_MODE_SPEED, val):
            await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature (writes modbus register)."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        value = int(round(float(temp) * 10))
        if await self.hub.write_register(REG_TARGET_TEMP, value):
            await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a preset (writes command register)."""
        val = PRESET_TO_VALUE.get(preset_mode)
        if val is None:
            return
        if await self.hub.write_register(REG_MODE_MAIN_CMD, val):
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Map HA HVAC modes to device values and write them."""
        mapping = {HVACMode.OFF: 7, HVACMode.AUTO: 1, HVACMode.FAN_ONLY: 2}
        value = mapping.get(hvac_mode)
        if value is None:
            return
        if await self.hub.write_register(REG_MODE_MAIN_CMD, value):
            await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the climate entity from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    device_info = data["device_info"]
    async_add_entities([VSRClimate(coordinator, device_info)])
