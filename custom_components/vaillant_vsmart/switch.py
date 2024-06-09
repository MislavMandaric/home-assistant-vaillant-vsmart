"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vaillant_netatmo_api import ApiException

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantProgramEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantScheduleSwitch(coordinator, device_id, module_id, program_id)
        for (device_id, module_id, program_id) in coordinator.data.programs.keys()
    ]
    async_add_devices(new_devices)


class VaillantScheduleSwitch(VaillantProgramEntity, SwitchEntity):
    """Vaillant vSMART Switch."""

    @property
    def name(self) -> str:
        """Return the name of the select."""

        return f"{self._program.name}"

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this switch."""

        return EntityCategory.CONFIG

    @property
    def device_class(self) -> SwitchDeviceClass:
        """Return device class for this switch."""

        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on, false otherwise."""

        return self._program.selected

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""

        try:
            await self._client.async_switch_schedule(
                self._device_id,
                self._module_id,
                self._program_id,
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""

        _LOGGER.info(
            "Active schedule can't be switched off. To change schedule, switch the one you want as active to on state."
        )
