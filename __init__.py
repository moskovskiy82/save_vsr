from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL, TRANSPORT_SERIAL
from .hub import VSRHub
from .coordinator import VSRCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Systemair SAVE VSR from a config entry."""
    transport = entry.data.get("transport", TRANSPORT_SERIAL)
    slave_id = entry.data.get("slave_id")
    update_interval = entry.options.get(
        "update_interval",
        entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    )

    # Init hub based on transport type (serial or TCP)
    if transport == TRANSPORT_SERIAL:
        hub = VSRHub(
            transport=transport,
            slave_id=slave_id,
            port=entry.data.get("port"),
            baudrate=entry.data.get("baudrate"),
            bytesize=entry.data.get("bytesize"),
            parity=entry.data.get("parity"),
            stopbits=entry.data.get("stopbits"),
        )
    else:
        hub = VSRHub(
            transport=transport,
            slave_id=slave_id,
            host=entry.data.get("host"),
            tcp_port=entry.data.get("tcp_port"),
        )

    # Initialize data coordinator
    coordinator = VSRCoordinator(hass, hub, update_interval)
    await coordinator.async_config_entry_first_refresh()

    # Store integration data in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "coordinator": coordinator,
        "device_info": {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Systemair SAVE VSR",
            "manufacturer": "Systemair",
            "model": "SAVE VSR",
        },
    }

    # Load all supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options updates (e.g., update_interval change)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Systemair SAVE VSR integration successfully initialized")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data:
            hub: VSRHub = data["hub"]
            await hub.async_close()
        _LOGGER.info("Systemair SAVE VSR integration unloaded")
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry (e.g., after options update)."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
