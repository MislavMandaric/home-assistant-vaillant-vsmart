"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantProgramEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantScheduleSelect(coordinator, device_id, module_id, program_id)
        for (device_id, module_id, program_id) in coordinator.data.programs.keys()
    ]
    async_add_devices(new_devices)


class VaillantScheduleSelect(VaillantProgramEntity, SelectEntity):
    """Vaillant vSMART Select."""

    @property
    def name(self) -> str:
        """Return the name of the select."""

        return self._program.name

    @property
    def entity_category(self) -> EntityCategory:
        """Return entity category for this select."""

        return EntityCategory.DIAGNOSTIC

    @property
    def current_option(self) -> str | None:
        """Currently active profile in a schedule."""

        zone = self._program.get_active_zone()

        if zone:
            return zone.name

        return None

    @property
    def options(self) -> list[str]:
        """All profiles available in the schedule."""

        return [zone.name for zone in self._program.zones]

    async def async_select_option(self, option: str) -> None:
        """Select different active profile."""

        _LOGGER.info(
            "Active profile can't be changed, it is always tracking a schedule. To change the profile, edit a schedule."
        )
