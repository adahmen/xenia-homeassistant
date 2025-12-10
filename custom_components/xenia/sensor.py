from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfPressure,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xenia sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    overview = data["overview"]
    single = data["single"]
    ip = data["ip"]

    entities: list[SensorEntity] = [
        XeniaStatusSensor(overview, ip),
        XeniaTempSensor(overview, "brew_group_temp", "BG_SENS_TEMP_A", ip),
        XeniaTempSensor(overview, "brew_boiler_temp", "BB_SENS_TEMP_A", ip),
        XeniaPressureSensor(overview, "pump_pressure", "PU_SENS_PRESS", ip),
        XeniaPressureSensor(overview, "steam_boiler_pressure", "SB_SENS_PRESS", ip),
        XeniaCurrentPowerSensor(overview, ip),
        XeniaEnergySensor(overview, ip),
        XeniaExtractionsSensor(overview, ip),
        XeniaOperatingHoursSensor(overview, ip),
        XeniaSetTempSensor(single, ip),
    ]

    async_add_entities(entities)


class XeniaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Xenia sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, name_suffix: str, ip: str, friendly: str | None = None) -> None:
        super().__init__(coordinator)
        self._name_suffix = name_suffix
        self._ip = ip
        self._attr_unique_id = f"xenia_{name_suffix}_{ip.replace('.', '_')}"
        if friendly:
            self._attr_name = friendly
        else:
            self._attr_name = f"Xenia {name_suffix.replace('_', ' ').title()}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for Xenia Espresso machine."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._ip)},
            name="Xenia Espresso",
            manufacturer="Xenia",
            model="Xenia DBL",
        )


class XeniaStatusSensor(XeniaBaseSensor):
    """Status (Off/On/Eco) of the machine."""

    def __init__(self, coordinator, ip: str) -> None:
        super().__init__(coordinator, "status", ip, "Xenia Status")

    @property
    def native_value(self) -> str | None:
        data: dict[str, Any] = self.coordinator.data or {}
        status = data.get("MA_STATUS")
        if status == 0:
            return "Off"
        if status == 1:
            return "On"
        if status == 2:
            return "Eco"
        return "Unknown"


class XeniaTempSensor(XeniaBaseSensor):
    """Temperature sensor (brew group / brew boiler)."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, name_suffix: str, key: str, ip: str) -> None:
        super().__init__(coordinator, name_suffix, ip)
        self._key = key

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get(self._key)
        if value is None:
            return None
        try:
            return round(float(value), 1)
        except (TypeError, ValueError):
            return None


class XeniaPressureSensor(XeniaBaseSensor):
    """Pressure sensor (pump / steam boiler)."""

    _attr_native_unit_of_measurement = UnitOfPressure.BAR

    def __init__(self, coordinator, name_suffix: str, key: str, ip: str) -> None:
        super().__init__(coordinator, name_suffix, ip)
        self._key = key

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get(self._key)
        if value is None:
            return None
        try:
            return round(float(value), 1)
        except (TypeError, ValueError):
            return None


class XeniaCurrentPowerSensor(XeniaBaseSensor):
    """Current power consumption (A)."""

    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    def __init__(self, coordinator, ip: str) -> None:
        super().__init__(coordinator, "current_power", ip, "Xenia Current Power")

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get("MA_CUR_PWR")
        if value is None:
            return None
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None


class XeniaEnergySensor(XeniaBaseSensor):
    """Total energy consumption (kWh)."""

    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, ip: str) -> None:
        super().__init__(coordinator, "total_energy", ip, "Xenia Total Energy")

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get("MA_ENERGY_TOTAL_KWH")
        if value is None:
            return None
        try:
            return round(float(value), 3)
        except (TypeError, ValueError):
            return None


class XeniaExtractionsSensor(XeniaBaseSensor):
    """Number of extractions."""

    def __init__(self, coordinator, ip: str) -> None:
        super().__init__(coordinator, "extractions", ip, "Xenia Extractions")

    @property
    def native_value(self) -> int | None:
        data = self.coordinator.data or {}
        value = data.get("MA_EXTRACTIONS")
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class XeniaOperatingHoursSensor(XeniaBaseSensor):
    """Operating hours."""

    def __init__(self, coordinator, ip: str) -> None:
        super().__init__(coordinator, "operating_hours", ip, "Xenia Operating Hours")

    @property
    def native_value(self) -> int | None:
        data = self.coordinator.data or {}
        value = data.get("MA_OPERATING_HOURS")
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class XeniaSetTempSensor(XeniaBaseSensor):
    """Brew group set temperature."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, ip: str) -> None:
        super().__init__(coordinator, "brewgroup_set_temp", ip, "Xenia Brew Group Set Temp")

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get("BG_SET_TEMP")
        if value is None:
            return None
        try:
            return round(float(value), 1)
        except (TypeError, ValueError):
            return None
