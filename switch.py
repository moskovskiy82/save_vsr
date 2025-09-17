from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import (
    DOMAIN,
)
from .coordinator import VSRCoordinator


class _VSRSimpleRegisterSwitch(CoordinatorEntity[VSRCoordinator], SwitchEntity):
    """A simple boolean switch backed by a single holding register or coil."""

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
        device_info: Dict[str, Any],
        write_as_coil: bool = False,
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

    async def _perform_write_and_opt_update(self, value: int) -> None:
        """Write register/coil and optimistically update coordinator cache for immediate UI feedback."""
        if self._reg_addr is None:
            self.coordinator.logger.warning(
                "Switch '%s' has no register address configured; set it in const.py",
                self._key,
            )
            return

        hub = self.coordinator.hub
        ok = False
        # prefer coil when explicitly requested and hub supports it
        if self._write_as_coil and hasattr(hub, "write_coil"):
            ok = await hub.write_coil(self._reg_addr, bool(value))
        else:
            # use write_register
            ok = await hub.write_register(self._reg_addr, int(value))

        if not ok:
            # Write failed — we log but don't change coordinator cache.
            self.coordinator.logger.error("Failed to write switch %s at %s", self._key, self._reg_addr)
            return

        # Optimistic update — update the coordinator cache immediately so UI reflects change.
        # We create a shallow copy of the current data and set the key.
        current = dict(self.coordinator.data) if self.coordinator.data else {}
        # store int for consistency with register reads
        current[self._read_key] = int(value)
        # update coordinator (this will notify entities)
        try:
            await self.coordinator.async_set_updated_data(current)
        except Exception:
            # older HA versions: fall back to directly setting data + request refresh
            try:
                self.coordinator.data = current
            except Exception:
                pass

        # Also request a background refresh to verify device actual state
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._perform_write_and_opt_update(1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._perform_write_and_opt_update(0)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: VSRCoordinator = data["coordinator"]
    device_info = data["device_info"]

    entities: list[SwitchEntity] = []

    # ECO Mode switch
    from .const import REG_ECO_MODE_ENABLE  # imported lazily to avoid import-time issues
    if REG_ECO_MODE_ENABLE is not None:
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
    from .const import REG_HEATER_ENABLE  # lazy import
    if REG_HEATER_ENABLE is not None:
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
    from .const import REG_RH_TRANSFER_ENABLE  # lazy import
    if REG_RH_TRANSFER_ENABLE is not None:
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
