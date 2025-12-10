from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL_OVERVIEW,
    CONF_SCAN_INTERVAL_SINGLE,
)
from .coordinator import XeniaOverviewCoordinator, XeniaSingleCoordinator

PLATFORMS: list[str] = ["sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Xenia from YAML (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xenia from a config entry."""
    session = aiohttp_client.async_get_clientsession(hass)
    ip = entry.data[CONF_IP_ADDRESS]

    scan_overview = entry.data[CONF_SCAN_INTERVAL_OVERVIEW]
    scan_single = entry.data[CONF_SCAN_INTERVAL_SINGLE]

    overview = XeniaOverviewCoordinator(hass, session, ip, scan_overview)
    single = XeniaSingleCoordinator(hass, session, ip, scan_single)

    await overview.async_config_entry_first_refresh()
    await single.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "overview": overview,
        "single": single,
        "session": session,
        "ip": ip,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
