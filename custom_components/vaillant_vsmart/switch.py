"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import datetime
import logging

from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_SWITCH
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_CONFIG
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vaillant_netatmo_api import ApiException, SetpointMode

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantEntity

NAME_SUFFIX = "HWB"

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantSwitch(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]
    async_add_devices(new_devices)


class VaillantSwitch(VaillantEntity, SwitchEntity):
    """Vaillant vSMART Switch."""

    @property
    def name(self) -> str:
        """Return the name of the switch."""

        return f"{self._module.module_name} {NAME_SUFFIX}"

    @property
    def entity_category(self) -> str:
        """Return entity category for this switch."""

        return ENTITY_CATEGORY_CONFIG

    @property
    def device_class(self) -> str:
        """Return device class for this switch."""

        return DEVICE_CLASS_SWITCH

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on, false otherwise."""

        return self._device.setpoint_hwb.setpoint_activate

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""

        endtime = datetime.datetime.now() + datetime.timedelta(
            minutes=self._device.setpoint_default_duration
        )

        try:
            await self._client.async_set_minor_mode(
                self._device_id,
                self._module_id,
                SetpointMode.HWB,
                True,
                setpoint_endtime=endtime,
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""

        try:
            await self._client.async_set_minor_mode(
                self._device_id, self._module_id, SetpointMode.HWB, False
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()
