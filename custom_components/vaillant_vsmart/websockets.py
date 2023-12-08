import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.websocket_api import (
    decorators,
    ActiveConnection,
)
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

from .const import DOMAIN, SWITCH, SELECT, SCHEDULE_SCHEMA
from .entity import VaillantCoordinator
from .schedule import map_program_to_schedule, map_schedule_to_program


_LOGGER = logging.getLogger(__name__)


class SchedulesEditView(HomeAssistantView):
    """Login to Home Assistant cloud."""

    url = f"/api/{DOMAIN}/edit"
    name = f"api:{DOMAIN}:edit"

    @RequestDataValidator(
        SCHEDULE_SCHEMA.extend({vol.Required("schedule_id"): cv.string})
    )
    async def post(self, request, data):
        """Handle config update request."""
        hass = request.app["hass"]

        for entry_id in hass.data[DOMAIN].keys():
            coordinator: VaillantCoordinator = hass.data[DOMAIN][entry_id]

            existing_program = coordinator.data.programs.get(data["schedule_id"])
            if existing_program is not None:
                new_program = map_schedule_to_program(data, existing_program)
                await coordinator.data.client.async_sync_schedule(
                    device_id=coordinator.data.device_for_program[new_program.id],
                    module_id=coordinator.data.module_for_program[new_program.id],
                    schedule_id=new_program.id,
                    name=new_program.name,
                    zones=new_program.zones,
                    timetable=new_program.timetable,
                )

                async_dispatcher_send(hass, f"{DOMAIN}_item_updated", new_program.id)

                return self.json({"success": True})

        return self.json({"success": False})


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

    listeners = []

    @callback
    def async_handle_event_item_updated(schedule_id: str):
        """pass data to frontend when backend changes"""
        connection.send_message(
            {
                "id": msg["id"],
                "type": "event",
                "event": {
                    "event": f"{DOMAIN}_item_updated",
                    "schedule_id": schedule_id,
                },
            }
        )

    listeners.append(
        async_dispatcher_connect(
            hass, f"{DOMAIN}_item_updated", async_handle_event_item_updated
        )
    )

    def unsubscribe_listeners():
        """unsubscribe listeners when frontend connection closes"""
        while len(listeners) > 0:
            listeners.pop()()

    connection.subscriptions[msg["id"]] = unsubscribe_listeners

    connection.send_result(msg["id"])


async def async_register_websockets(hass: HomeAssistant) -> None:
    """TODO"""

    hass.http.register_view(SchedulesEditView)

    hass.components.websocket_api.async_register_command(websocket_get_schedules)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_item)
    hass.components.websocket_api.async_register_command(websocket_get_tags)
    hass.components.websocket_api.async_register_command(
        websocket_schedule_item_updated
    )
