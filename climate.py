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

    # Features: target temp (1°C stepping for UI), fan mode and presets
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["low", "medium", "high"]
    _attr_preset_modes = PRESET_LIST

    # Present integer steps in UI (1 °C) per your request,
    # but device stores tenths internally so we convert on write/read.
    _attr_min_temp = 12.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 1.0

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
        """
        Return target temperature for display.

        We display whole degrees (1°C step) to match the device control panel.
        The coordinator stores tenths (x0.1) so we round to integer for UI.
        """
        t = self.coordinator.data.get("target_temp")
        if t is None:
            return None
        # Round to nearest integer for clean UI (device supports tenths internally)
        return float(round(t))

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode based on mode_main register (status)."""
        mode = self.coordinator.data.get("mode_main")
        if mode is None:
            return None
        # Observed status mapping from your device reads:
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
            "raw_target_temp_tenths": self.coordinator.data.get("target_temp"),
        }

    # --- Setters / commands ---------------------------------------------

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan speed (writes modbus register)."""
        val = FAN_SPEED_TO_VALUE.get(fan_mode)
        if val is None:
            return
        ok = await self.hub.write_register(REG_MODE_SPEED, val)
        if ok:
            # optimistic: update coordinator data immediately so UI is snappy
            new = dict(self.coordinator.data or {})
            new["mode_speed"] = val
            # FIXED: Remove await - async_set_updated_data is NOT a coroutine
            self.coordinator.async_set_updated_data(new)
            # schedule background refresh to validate
            await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature (user sees 1°C steps, device expects tenths)."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        # device stores tenths of °C -> convert
        reg_value = int(round(float(temp) * 10))
        ok = await self.hub.write_register(REG_TARGET_TEMP, reg_value)
        if ok:
            # optimistic update: coordinator stores tenths as float with 1 decimal
            new = dict(self.coordinator.data or {})
            new["target_temp"] = round(reg_value * 0.1, 1)
            # FIXED: Remove await
            self.coordinator.async_set_updated_data(new)
            await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a preset (writes command register)."""
        val = PRESET_TO_VALUE.get(preset_mode)
        if val is None:
            return
        ok = await self.hub.write_register(REG_MODE_MAIN_CMD, val + 1)
        if ok:
            # optimistic update
            new = dict(self.coordinator.data or {})
            new["mode_main"] = val
            # FIXED: Remove await
            self.coordinator.async_set_updated_data(new)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """
        Map HA HVAC modes to device command values and write them.

        NOTE: your device exhibits inconsistent values for status vs command.
        Observed *status* values: 6 -> OFF, 0 -> AUTO, 1 -> FAN_ONLY.
        Some devices expect command OFF=7 while status shows 6. To be robust
        we attempt the common command (7) first and fall back to 6 if 7 fails.
        """
        if hvac_mode == HVACMode.OFF:
            # Try 7 first (common command value for OFF), then 6 as fallback
            if await self.hub.write_register(REG_MODE_MAIN_CMD, 7):
                new = dict(self.coordinator.data or {})
                new["mode_main"] = 7
                # FIXED: Remove await
                self.coordinator.async_set_updated_data(new)
                await self.coordinator.async_request_refresh()
                return
            # fallback try 6
            if await self.hub.write_register(REG_MODE_MAIN_CMD, 6):
                new = dict(self.coordinator.data or {})
                new["mode_main"] = 6
                # FIXED: Remove await
                self.coordinator.async_set_updated_data(new)
                await self.coordinator.async_request_refresh()
                return
            return

        mapping = {HVACMode.AUTO: 1, HVACMode.FAN_ONLY: 2}
        value = mapping.get(hvac_mode)
        if value is None:
            return
        ok = await self.hub.write_register(REG_MODE_MAIN_CMD, value)
        if ok:
            new = dict(self.coordinator.data or {})
            new["mode_main"] = value
            # FIXED: Remove await
            self.coordinator.async_set_updated_data(new)
            await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the climate entity from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    device_info = data["device_info"]
    async_add_entities([VSRClimate(coordinator, device_info)])
