"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging


from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantDeviceEntity, VaillantModuleEntity
from homeassistant.const import ENERGY_WATT_HOUR, PERCENTAGE
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantBatterySensor(coordinator, device_id, module_id)
        for (device_id, module_id) in coordinator.data.modules.keys()
    ]

    new_devices += [
        VaillantGasHeatingSensor(coordinator, device_id)
        for device_id in coordinator.data.gas_heating_measurements.keys()
    ]

    new_devices += [
        VaillantGasWaterSensor(coordinator, device_id)
        for device_id in coordinator.data.gas_water_measurements.keys()
    ]

    new_devices += [
        VaillantElecHeatingSensor(coordinator, device_id)
        for device_id in coordinator.data.elec_heating_measurements.keys()
    ]

    new_devices += [
        VaillantElecWaterSensor(coordinator, device_id)
        for device_id in coordinator.data.elec_water_measurements.keys()
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


class VaillantGasHeatingSensor(VaillantDeviceEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_gas_heating"

    @property
    def translation_key(self) -> str:
        """Return the translation key of the sensor."""

        return "gas_heating"

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
        """Return current value of gas heating sensor."""
        measurement = self.coordinator.data.gas_heating_measurements.get(
            self._device.id
        )

        if measurement:
            if len(measurement.value) > 0:
                return measurement.value[-1]

        return 0

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the gas heating sensor."""

        return ENERGY_WATT_HOUR


class VaillantGasWaterSensor(VaillantDeviceEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_gas_water"

    @property
    def translation_key(self) -> str:
        """Return the translation key of the sensor."""

        return "gas_water"

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
        """Return current value of gas water sensor."""
        measurement = self.coordinator.data.gas_water_measurements.get(
            self._device.id
        )

        if measurement:
            if len(measurement.value) > 0:
                return measurement.value[-1]

        return 0

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the elec water sensor."""

        return ENERGY_WATT_HOUR


class VaillantElecHeatingSensor(VaillantDeviceEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_elec_heating"

    @property
    def translation_key(self) -> str:
        """Return the translation key of the sensor."""

        return "elec_heating"

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
        """Return current value of gas water sensor."""
        measurement = self.coordinator.data.elec_heating_measurements.get(
            self._device.id
        )

        if measurement:
            if len(measurement.value) > 0:
                return measurement.value[-1]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the elec heating sensor."""

        return ENERGY_WATT_HOUR


class VaillantElecWaterSensor(VaillantDeviceEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_elec_water"

    @property
    def translation_key(self) -> str:
        """Return the translation key of the sensor."""

        return "elec_water"

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
        """Return current value of elec water sensor."""
        measurement = self.coordinator.data.elec_water_measurements.get(
            self._device.id
        )

        if measurement:
            if len(measurement.value) > 0:
                return measurement.value[-1]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the elec water sensor."""

        return ENERGY_WATT_HOUR
