# switch.py

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import (
    DOMAIN,
    REG_ECO_MODE_ENABLE,
    REG_HEATER_ENABLE,
    REG_RH_TRANSFER_ENABLE,
)
from .coordinator import VSRCoordinator


class _VSRSimpleRegisterSwitch(CoordinatorEntity[VSRCoordinator], SwitchEntity):
    """A simple boolean switch backed by a single holding register."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: VSRCoordinator,
        *,
        key: str,
        name: str,
        reg_addr: int | None,
        read_key: str,
        write_as_coil: bool = False,
        device_info: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._reg_addr = reg_addr
        self._read_key = read_key
        self._write_as_coil = write_as_coil

        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{key}"
        self._attr_device_info = device_info

    @property
    def available(self) -> bool:
        return self._reg_addr is not None and self._read_key in self.coordinator.data

    @property
    def is_on(self) -> bool | None:
        if not self.available:
            return None
        val = self.coordinator.data.get(self._read_key)
        if val is None:
            return None
        try:
            return int(val) != 0
        except (TypeError, ValueError):
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        if self._reg_addr is None:
            self.coordinator.logger.warning(
                "Switch '%s' has no register address configured; set it in const.py",
                self._key,
            )
            return

        hub = self.coordinator.hub
        ok = await hub.write_register(self._reg_addr, 1)
        if ok:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self._reg_addr is None:
            self.coordinator.logger.warning(
                "Switch '%s' has no register address configured; set it in const.py",
                self._key,
            )
            return

        hub = self.coordinator.hub
        ok = await hub.write_register(self._reg_addr, 0)
        if ok:
            await self.coordinator.async_request_refresh()

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    device_info = data["device_info"]

    entities: list[SwitchEntity] = []

    # ECO Mode switch
    entities.append(
        _VSRSimpleRegisterSwitch(
            coordinator,
            key="eco_mode",
            name="ECO Mode",
            reg_addr=REG_ECO_MODE_ENABLE,
            read_key="eco_mode",
            write_as_coil=False,
            device_info=device_info,
        )
    )

    # Heater Enable switch
    entities.append(
        _VSRSimpleRegisterSwitch(
            coordinator,
            key="heater_enable",
            name="Heater Enable",
            reg_addr=REG_HEATER_ENABLE,
            read_key="heater_enable",
            write_as_coil=False,
            device_info=device_info,
        )
    )

    # RH Transfer switch
    entities.append(
        _VSRSimpleRegisterSwitch(
            coordinator,
            key="rh_transfer",
            name="RH Transfer",
            reg_addr=REG_RH_TRANSFER_ENABLE,
            read_key="rh_transfer",
            write_as_coil=False,
            device_info=device_info,
        )
    )

    async_add_entities(entities)
