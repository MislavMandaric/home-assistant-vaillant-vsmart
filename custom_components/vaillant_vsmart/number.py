"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vaillant_netatmo_api import ApiException

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantDHWTemperatureNumber(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]
    async_add_devices(new_devices)


class VaillantDHWTemperatureNumber(VaillantEntity, NumberEntity):
    """Vaillant vSMART Number."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return self._module.id

    @property
    def name(self) -> str:
        """Return the name of the number."""

        return f"{self._module.module_name} DHW Temperature"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this number."""

        return EntityCategory.CONFIG

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return device class for this number."""

        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> float:
        """Return current DHW temperature."""

        return self._device.dhw

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the temperature."""

        return UnitOfTemperature.CELSIUS

    @property
    def native_step(self) -> float:
        """Return native step for the temperature."""

        return 1.0

    @property
    def native_min_value(self) -> float:
        """Return min possible temperature for the DHW."""

        return self._device.dhw_min

    @property
    def native_max_value(self) -> float:
        """Return max possible temperature for the DHW."""

        return self._device.dhw_max

    async def async_set_native_value(self, value: float) -> None:
        """Update the current temperature."""

        try:
            await self._client.async_set_hot_water_temperature(
                self._device_id,
                round(value),
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()
