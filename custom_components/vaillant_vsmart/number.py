"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ApiException, VaillantCoordinator, VaillantDeviceEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantDeviceNumber(coordinator, device.id)
        for device in coordinator.data.devices.values()
    ]
    async_add_devices(new_devices)


class VaillantDeviceNumber(VaillantDeviceEntity, NumberEntity):
    """Vaillant vSMART Number."""

    @property
    def translation_key(self):
        """Return the translation key to translate the entity's name and states."""

        return "default_setpoint_duration"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this number."""

        return EntityCategory.CONFIG

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return device class for this number."""

        return NumberDeviceClass.DURATION

    @property
    def native_max_value(self) -> float:
        """Return maximal setpoint duration."""

        return 720.0  # 12 hours

    @property
    def native_min_value(self) -> float:
        """Return minimal setpoint duration."""

        return 5.0  # 5 minutes

    @property
    def native_step(self) -> float:
        """Return step for setting setpoint duration."""

        return 5.0  # 5 minutes

    @property
    def native_value(self) -> float:
        """Return current setpoint duration."""

        return self._device.setpoint_default_duration

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement for the setpoint duration."""

        return UnitOfTime.MINUTES

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        try:
            await self._client.async_modify_device_params(
                self._device_id,
                int(value),
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()
