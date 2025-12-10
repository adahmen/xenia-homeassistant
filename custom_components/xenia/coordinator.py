from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_OVERVIEW, API_OVERVIEW_SINGLE

_LOGGER = logging.getLogger(__name__)


class _BaseXeniaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        ip: str,
        scan_interval: int,
        path: str,
        name_suffix: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name_suffix}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._session = session
        self._ip = ip
        self._path = path

    async def _async_update_data(self) -> dict[str, Any]:
        url = f"http://{self._ip}{self._path}"
        try:
            async with self._session.get(url, timeout=30) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                data = await resp.json()
                if not isinstance(data, dict):
                    raise UpdateFailed("Unexpected JSON format")
                return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching {url}: {err}") from err


class XeniaOverviewCoordinator(_BaseXeniaCoordinator):
    def __init__(self, hass, session, ip, scan_interval: int) -> None:
        super().__init__(hass, session, ip, scan_interval, API_OVERVIEW, "overview")


class XeniaSingleCoordinator(_BaseXeniaCoordinator):
    def __init__(self, hass, session, ip, scan_interval: int) -> None:
        super().__init__(hass, session, ip, scan_interval, API_OVERVIEW_SINGLE, "single")
