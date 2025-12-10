from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL_OVERVIEW,
    CONF_SCAN_INTERVAL_SINGLE,
    DEFAULT_SCAN_INTERVAL_OVERVIEW,
    DEFAULT_SCAN_INTERVAL_SINGLE,
)


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Optional(
            CONF_SCAN_INTERVAL_OVERVIEW,
            default=DEFAULT_SCAN_INTERVAL_OVERVIEW,
        ): int,
        vol.Optional(
            CONF_SCAN_INTERVAL_SINGLE,
            default=DEFAULT_SCAN_INTERVAL_SINGLE,
        ): int,
    }
)


class XeniaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Xenia Espresso."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=f"Xenia ({user_input[CONF_IP_ADDRESS]})",
                data=user_input,
            )

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
