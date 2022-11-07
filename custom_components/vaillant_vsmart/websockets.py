import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.core import HomeAssistant
from homeassistant.components.websocket_api import (
    decorators,
    ActiveConnection,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from vaillant_netatmo_api.thermostat import Program

from .const import DOMAIN, SWITCH, SELECT
from .entity import VaillantCoordinator
from .schedule import map_program_to_schedule


_LOGGER = logging.getLogger(__name__)


@decorators.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}",
    }
)
@decorators.async_response
async def websocket_get_schedules(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Publish scheduler list data."""

    er = entity_registry.async_get(hass)

    schedule: list[dict] = []
    for entry_id in hass.data[DOMAIN].keys():
        coordinator: VaillantCoordinator = hass.data[DOMAIN][entry_id]
        for program in coordinator.data.programs.values():
            schedule_entity_id = er.async_get_entity_id(SWITCH, DOMAIN, program.id)
            profile_entity_id = er.async_get_entity_id(SELECT, DOMAIN, program.id)
            schedule_item = map_program_to_schedule(
                schedule_entity_id, profile_entity_id, program
            )
            schedule.append(schedule_item)

    connection.send_result(msg["id"], schedule)


@decorators.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/item",
        vol.Required("schedule_id"): cv.string,
    }
)
@decorators.async_response
async def websocket_get_schedule_item(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Publish scheduler list data."""

    er = entity_registry.async_get(hass)

    for entry_id in hass.data[DOMAIN].keys():
        coordinator: VaillantCoordinator = hass.data[DOMAIN][entry_id]

        program = coordinator.data.programs.get(msg["schedule_id"])
        if program is not None:
            schedule_entity_id = er.async_get_entity_id(SWITCH, DOMAIN, program.id)
            profile_entity_id = er.async_get_entity_id(SELECT, DOMAIN, program.id)
            schedule_item = map_program_to_schedule(
                schedule_entity_id, profile_entity_id, program
            )
            connection.send_result(msg["id"], schedule_item)
            break


@decorators.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}_updated",
    }
)
@decorators.async_response
async def websocket_schedule_item_updated(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Publish scheduler list data."""

    connection.send_result(msg["id"])


@decorators.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/tags",
    }
)
@decorators.async_response
async def websocket_get_tags(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Publish tag list data."""

    connection.send_result(msg["id"], [])


async def async_register_websockets(hass: HomeAssistant) -> None:
    """TODO"""

    hass.components.websocket_api.async_register_command(websocket_get_schedules)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_item)
    hass.components.websocket_api.async_register_command(
        websocket_schedule_item_updated
    )
    hass.components.websocket_api.async_register_command(websocket_get_tags)
