"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging


from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantModuleEntity
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
        VaillantBatterySensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]

    new_devices += [
        VaillantGasHeatingSensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]

    new_devices += [
        VaillantGasWaterSensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]

    new_devices += [
        VaillantElecHeatingSensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]

    new_devices += [
        VaillantElecWaterSensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
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


class VaillantGasHeatingSensor(VaillantEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._module.id}_gas_heating"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._module.module_name} Gas heating"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.ENERGY

    @property
    def icon(self) -> str | None:
        return "mdi:heating-coil"

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> str:
        """Return current value of gas heating sensor."""
        measures = self.coordinator.data.energy_measures.get(
            self._module.id
        ).gas_heating.value

        return str(measures[measures.__len__() - 1])

    @property
    def extra_state_attributes(self):
        return {
            "historical_values": str(
                self.coordinator.data.energy_measures.get(
                    self._module.id
                ).gas_heating.value
            )
        }

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the gas heating sensor."""

        return ENERGY_WATT_HOUR


class VaillantGasWaterSensor(VaillantEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._module.id}_gas_water"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._module.module_name} Gas water"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.ENERGY

    @property
    def icon(self) -> str | None:
        return "mdi:water-boiler"

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> str:
        """Return current value of gas water sensor."""
        measures = self.coordinator.data.energy_measures.get(
            self._module.id
        ).gas_water.value

        return str(measures[measures.__len__() - 1])

    @property
    def extra_state_attributes(self):
        return {
            "historical_values": str(
                self.coordinator.data.energy_measures.get(
                    self._module.id
                ).gas_water.value
            )
        }

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the elec water sensor."""

        return ENERGY_WATT_HOUR


class VaillantElecHeatingSensor(VaillantEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._module.id}_elec_heating"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._module.module_name} Elec heating"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.ENERGY

    @property
    def icon(self) -> str | None:
        return "mdi:heating-coil"

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> str:
        """Return current value of gas water sensor."""
        measures = self.coordinator.data.energy_measures.get(
            self._module.id
        ).elec_heating.value

        return str(measures[measures.__len__() - 1])

    @property
    def extra_state_attributes(self):
        return {
            "historical_values": str(
                self.coordinator.data.energy_measures.get(
                    self._module.id
                ).elec_heating.value
            )
        }

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the elec heating sensor."""

        return ENERGY_WATT_HOUR


class VaillantElecWaterSensor(VaillantEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._module.id}_elec_water"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._module.module_name} Elec water"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this sensor."""

        return EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class for this sensor."""

        return SensorDeviceClass.ENERGY

    @property
    def icon(self) -> str | None:
        return "mdi:water-boiler"

    @property
    def state_class(self) -> SensorStateClass:
        """Return state class for this sensor."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> str:
        """Return current value of elec water sensor."""
        measures = self.coordinator.data.energy_measures.get(
            self._module.id
        ).elec_water.value

        return str(measures[measures.__len__() - 1])

    @property
    def extra_state_attributes(self):
        return {
            "historical_values": str(
                self.coordinator.data.energy_measures.get(
                    self._module.id
                ).elec_water.value
            )
        }

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the elec water sensor."""

        return ENERGY_WATT_HOUR
