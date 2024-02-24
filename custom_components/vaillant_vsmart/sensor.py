"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass, ENTITY_ID_FORMAT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from vaillant_netatmo_api import MeasurementType, MeasurementItem

from .const import DOMAIN, SENSOR
from .entity import VaillantCoordinator, VaillantModuleEntity, VaillantData, VaillantDataMeasure

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = []
    for device in coordinator.data.devices.values():
        for module in device.modules:
            new_devices.append(VaillantBatterySensor(coordinator, device.id, module.id))

    for measurement in coordinator.data.measurements:
        new_devices.append(VaillantGasSensor(coordinator, measurement.device.id, measurement.module.id, measurement))

    async_add_devices(new_devices)


class VaillantBatterySensor(VaillantModuleEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.BATTERY

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return current value of battery level."""

        return self._module.battery_percent

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the battery level."""

        return PERCENTAGE


class VaillantGasSensor(VaillantModuleEntity, SensorEntity):
    """Vaillant vSMART Gas Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[VaillantData],
        device_id: str,
        module_id: str,
        measurement: VaillantDataMeasure
    ):
        """Initialize."""
        super().__init__(coordinator, device_id, module_id)
        self.measurement = measurement
        self.entity_id = f"{SENSOR}.{DOMAIN}_{self.measurement.sensor.sensor_name}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return ENTITY_ID_FORMAT.format(f"{self._module.id}_{self.measurement.sensor.sensor_name}")

    @property
    def name(self) -> str | UndefinedType | None:
        # Bug : name from translation/<lang>.json is not picked up
        return self.measurement.sensor.sensor_name

    @property
    def translation_key(self) -> str | None:
        return self.measurement.sensor.key

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""
        return  self.measurement.sensor.device_class

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL

    @property
    def last_reset(self) -> datetime | None:
        return self.measurement.last_reset

    @property
    def native_value(self) -> float:
        """Return current value."""
        value: float = 0
        if self.measurement.measures:
            for measure in self.measurement.measures:
                if measure.value:
                    for val in measure.value:
                        value += val
        value *= self.measurement.sensor.conversion
        return value

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the battery level."""
        return self.measurement.sensor.unit

    @property
    def icon(self) -> str | None:
        return self.measurement.sensor.icon
