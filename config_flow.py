from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    TRANSPORT_SERIAL,
    TRANSPORT_TCP,
    DEFAULT_SERIAL_PORT,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOPBITS,
    DEFAULT_HOST,
    DEFAULT_TCP_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_UPDATE_INTERVAL,
)

SERIAL_SCHEMA = vol.Schema(
    {
        vol.Required("port", default=DEFAULT_SERIAL_PORT): str,
        vol.Required("baudrate", default=DEFAULT_BAUDRATE): int,
        vol.Required("bytesize", default=DEFAULT_BYTESIZE): vol.In([7, 8]),
        vol.Required("parity", default=DEFAULT_PARITY): vol.In(["N", "E", "O"]),
        vol.Required("stopbits", default=DEFAULT_STOPBITS): vol.In([1, 2]),
        vol.Required("slave_id", default=DEFAULT_SLAVE_ID): int,
        vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
    }
)

TCP_SCHEMA = vol.Schema(
    {
        vol.Required("host", default=DEFAULT_HOST): str,
        vol.Required("tcp_port", default=DEFAULT_TCP_PORT): int,
        vol.Required("slave_id", default=DEFAULT_SLAVE_ID): int,
        vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
    }
)

TRANSPORT_PICK = vol.Schema({vol.Required("transport", default=TRANSPORT_SERIAL): vol.In([TRANSPORT_SERIAL, TRANSPORT_TCP])})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=TRANSPORT_PICK)

        transport = user_input["transport"]
        self._transport = transport
        return await self.async_step_transport_details()

    async def async_step_transport_details(self, user_input=None) -> FlowResult:
        schema = SERIAL_SCHEMA if self._transport == TRANSPORT_SERIAL else TCP_SCHEMA
        if user_input is None:
            return self.async_show_form(step_id="transport_details", data_schema=schema)

        # Save config
        data = {"transport": self._transport, **user_input}
        return self.async_create_entry(title="Systemair VSR", data=data)

    async def async_step_import(self, user_input=None) -> FlowResult:
        # Optional: support YAML import if desired later
        return await self.async_step_user(user_input)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "update_interval",
                        default=self.config_entry.options.get("update_interval", self.config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)),
                    ): int
                }
            ),
        )

async def async_get_options_flow(config_entry):
    return OptionsFlowHandler(config_entry)
