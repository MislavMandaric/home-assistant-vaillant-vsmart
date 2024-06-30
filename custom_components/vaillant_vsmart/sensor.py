"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SUPPORTED_ENERGY_MEASUREMENT_TYPES, SUPPORTED_DURATION_MEASUREMENT_TYPES
from .entity import VaillantCoordinator, VaillantModuleEntity, VaillantMeasurementEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantBatterySensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ] + [
        VaillantEnergySensor(
            coordinator, device.id, module.id, measurement_type)
        for device in coordinator.data.devices.values()
        for module in device.modules
        for measurement_type in SUPPORTED_ENERGY_MEASUREMENT_TYPES
    ] + [
        VaillantDurationSensor(
            coordinator, device.id, module.id, measurement_type)
        for device in coordinator.data.devices.values()
        for module in device.modules
        for measurement_type in SUPPORTED_DURATION_MEASUREMENT_TYPES
    ]

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


class VaillantEnergySensor(VaillantMeasurementEntity, SensorEntity):
    """Vaillant vSMART Energy Sensor."""

    @property
    def translation_key(self):
        """Return the translation key to translate the entity's name and states."""

        return self._measurement_type.value

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float:
        """Return current value of energy level."""

        return self._measurement.value[-1]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the energy level."""

        return UnitOfEnergy.WATT_HOUR


class VaillantDurationSensor(VaillantMeasurementEntity, SensorEntity):
    """Vaillant vSMART Duration Sensor."""

    @property
    def translation_key(self):
        """Return the translation key to translate the entity's name and states."""

        return self._measurement_type.value

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.DURATION

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float:
        """Return current value of duration."""

        return self._measurement.value[-1]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the duration."""

        return UnitOfTime.SECONDS
