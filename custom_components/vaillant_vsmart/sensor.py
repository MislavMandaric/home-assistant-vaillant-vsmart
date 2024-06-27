"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging
from datetime import datetime, date
from decimal import Decimal

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass, ENTITY_ID_FORMAT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType, StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from vaillant_netatmo_api import MeasurementType, MeasurementItem

from .const import DOMAIN, SENSOR, VaillantSensorEntityDescription
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

    for sensor in coordinator.sensors:
        new_devices.append(VaillantEnergySensor(coordinator, sensor))

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


class VaillantEnergySensor(VaillantModuleEntity, SensorEntity):
    """Vaillant vSMART Gas Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[VaillantData],
        sensor: VaillantSensorEntityDescription):
        """Initialize."""
        super().__init__(coordinator, sensor.device.id, sensor.module.id)
        self.sensor = sensor
        self.entity_id = f"{SENSOR}.{DOMAIN}_{self.sensor.sensor_name}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return ENTITY_ID_FORMAT.format(f"{self.sensor.module.id}_{self.sensor.sensor_name}")

    @property
    def name(self) -> str | UndefinedType | None:
        # TODO bug : name from translation/<lang>.json is not picked up
        # I suspect that these translation files are read from github directly and not from component folder
        return self.sensor.sensor_name

    @property
    def translation_key(self) -> str | None:
        return self.sensor.key

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self.sensor.enabled

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""
        return  self.sensor.device_class

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL

    @property
    def last_reset(self) -> datetime | None:
        data: VaillantData = self.coordinator.data
        for measurement in data.measurements:
            if (measurement.sensor.key == self.sensor.key
                    and measurement.sensor.module.id == self.sensor.module.id):
                return measurement.last_reset
        return None

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return current value."""
        value: float = 0
        data: VaillantData = self.coordinator.data
        if data.measurements is None:
            return None
        found = False
        for measurement in data.measurements:
            if (measurement.sensor.key == self.sensor.key
                    and measurement.sensor.module.id == self.sensor.module.id):
                found = True
                if measurement.measures:
                    for measure in measurement.measures:
                        if measure.value:
                            for val in measure.value:
                                value += val
                value *= measurement.sensor.conversion
        if found:
            return value
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the battery level."""
        return self.sensor.unit

    @property
    def icon(self) -> str | None:
        return self.sensor.icon

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Vaillant updated sensor value %s : %.2f", self.sensor.sensor_name,
                      self.native_value)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        # Enable extraction of data of this sensor from API
        self.sensor.enabled = True
        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        # Disable extraction of data of this sensor from API
        self.sensor.enabled = False
        await super().async_will_remove_from_hass()
