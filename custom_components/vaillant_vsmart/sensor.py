"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    DEVICE_CLASS_BATTERY,
    STATE_CLASS_MEASUREMENT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_DIAGNOSTIC, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantEntity

NAME_SUFFIX = "battery"

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantSensor(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]
    async_add_devices(new_devices)


class VaillantSensor(VaillantEntity, SensorEntity):
    """Vaillant vSMART Sensor."""

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return f"{self._module.module_name} {NAME_SUFFIX}"

    @property
    def entity_category(self) -> str:
        """Return entity category for this sensor."""

        return ENTITY_CATEGORY_DIAGNOSTIC

    @property
    def device_class(self) -> str:
        """Return device class for this sensor."""

        return DEVICE_CLASS_BATTERY

    @property
    def state_class(self) -> str:
        """Return state class for this sensor."""

        return STATE_CLASS_MEASUREMENT

    @property
    def native_value(self) -> str:
        """Return current value of battery level."""

        return str(self._module.battery_percent)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the battery level."""

        return PERCENTAGE
