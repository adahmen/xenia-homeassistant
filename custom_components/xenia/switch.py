from __future__ import annotations

import json
import logging

from aiohttp import ClientSession
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, API_MACHINE_CONTROL
from .coordinator import XeniaOverviewCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xenia switch from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    overview: XeniaOverviewCoordinator = data["overview"]
    session: ClientSession = data["session"]
    ip: str = data["ip"]

    async_add_entities([XeniaPowerSwitch(overview, session, ip)])


class XeniaPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Power switch for the Xenia machine."""

    _attr_has_entity_name = True
    _attr_name = "Xenia Power"
    _attr_icon = "mdi:coffee-maker"

    def __init__(self, coordinator: XeniaOverviewCoordinator, session: ClientSession, ip: str) -> None:
        super().__init__(coordinator)
        self._session = session
        self._ip = ip
        self._attr_unique_id = f"xenia_power_{ip.replace('.', '_')}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for Xenia Espresso machine."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._ip)},
            name="Xenia Espresso",
            manufacturer="Xenia",
            model="Xenia DBL",
        )

    @property
    def is_on(self) -> bool:
        data = self.coordinator.data or {}
        return data.get("MA_STATUS") == 1

    async def _send_action(self, action: int) -> None:
        url = f"http://{self._ip}{API_MACHINE_CONTROL}"
        payload = {"action": action}
        try:
            async with self._session.post(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to control Xenia: HTTP %s", resp.status)
        except Exception as err:
            _LOGGER.error("Error controlling Xenia: %s", err)

        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs) -> None:
        await self._send_action(1)

    async def async_turn_off(self, **kwargs) -> None:
        await self._send_action(0)
