"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfTime, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SUPPORTED_ENERGY_MEASUREMENT_TYPES, SUPPORTED_DURATION_MEASUREMENT_TYPES
from .boiler_errors import find_status_value, has_status_key
from .entity import VaillantCoordinator, VaillantDeviceEntity, VaillantHomestatusEntity, VaillantModuleEntity, VaillantMeasurementEntity

# homestatus field -> (device class, unit, entity category)
STATUS_SENSORS: dict[str, tuple[SensorDeviceClass | None, str | None, EntityCategory | None]] = {
    "dhw_setpoint_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    "dhw_temperature_min": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, EntityCategory.DIAGNOSTIC),
    "dhw_temperature_max": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, EntityCategory.DIAGNOSTIC),
    "dhw_control": (None, None, None),
    "rf_strength": (None, None, EntityCategory.DIAGNOSTIC),
    "oem_serial": (None, None, EntityCategory.DIAGNOSTIC),
}

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantTemperatureSensor(coordinator, device.id)
        for device in coordinator.data.devices.values()
    ] + [
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
    ] + [
        VaillantStatusSensor(coordinator, device.id, key)
        for device in coordinator.data.devices.values()
        for key in STATUS_SENSORS
        if has_status_key(coordinator.data.module_status, key)
    ]

    async_add_devices(new_devices)


class VaillantTemperatureSensor(VaillantDeviceEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def translation_key(self):
        """Return the translation key to translate the entity's name and states."""

        return "outdoor_temperature"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float:
        """Return current value of temperature level."""

        return self._device.outdoor_temperature.te

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the temperature level."""

        return UnitOfTemperature.CELSIUS


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

        if self._measurement is None:
            return 0

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

        if self._measurement is None:
            return 0

        return self._measurement.value[-1]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the duration."""

        return UnitOfTime.SECONDS


class VaillantStatusSensor(VaillantHomestatusEntity, SensorEntity):
    """Sensor for a field of the homestatus module."""

    def __init__(self, coordinator: VaillantCoordinator, device_id: str, key: str) -> None:
        """Initialize."""

        super().__init__(coordinator, device_id)
        self._key = key
        device_class, unit, category = STATUS_SENSORS[key]
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = category
        if device_class == SensorDeviceClass.TEMPERATURE:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_status_{self._key}"

    @property
    def translation_key(self) -> str:
        """Return the translation key to translate the entity's name."""

        return f"status_{self._key}"

    @property
    def native_value(self):
        """Return the value of the field."""

        found, value = find_status_value(self.coordinator.data.module_status, self._device_id, self._key)
        if not found or isinstance(value, dict | list):
            return None
        return value
