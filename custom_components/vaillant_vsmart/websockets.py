import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.core import HomeAssistant
from homeassistant.components.websocket_api import (
    decorators,
    ActiveConnection,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from vaillant_netatmo_api.thermostat import Program

from .const import DOMAIN, ATTR_SCHEDULE_ID, SWITCH, SELECT
from .entity import VaillantCoordinator
from .schedule import map_program_to_schedule


_LOGGER = logging.getLogger(__name__)


# class SchedulesAddView(HomeAssistantView):
#     """Login to Home Assistant cloud."""

#     url = "/api/{}/add".format(DOMAIN)
#     name = "api:{}:add".format(DOMAIN)

#     @RequestDataValidator(const.SCHEDULE_SCHEMA)
#     async def post(self, request, data):
#         """Handle config update request."""
#         hass = request.app["hass"]
#         coordinator = hass.data[const.DOMAIN]["coordinator"]
#         coordinator.async_create_schedule(data)
#         return self.json({"success": True})


# class SchedulesEditView(HomeAssistantView):
#     """Login to Home Assistant cloud."""

#     url = "/api/{}/edit".format(const.DOMAIN)
#     name = "api:{}:edit".format(const.DOMAIN)

#     @RequestDataValidator(
#         const.SCHEDULE_SCHEMA.extend({vol.Required(const.ATTR_SCHEDULE_ID): cv.string})
#     )
#     async def post(self, request, data):
#         """Handle config update request."""
#         hass = request.app["hass"]
#         coordinator = hass.data[const.DOMAIN]["coordinator"]
#         schedule_id = data[const.ATTR_SCHEDULE_ID]
#         del data[const.ATTR_SCHEDULE_ID]
#         await coordinator.async_edit_schedule(schedule_id, data)
#         return self.json({"success": True})


# class SchedulesRemoveView(HomeAssistantView):
#     """Login to Home Assistant cloud."""

#     url = "/api/{}/remove".format(const.DOMAIN)
#     name = "api:{}:remove".format(const.DOMAIN)

#     @RequestDataValidator(vol.Schema({vol.Required(const.ATTR_SCHEDULE_ID): cv.string}))
#     async def post(self, request, data):
#         """Handle config update request."""
#         hass = request.app["hass"]
#         coordinator = hass.data[const.DOMAIN]["coordinator"]
#         await coordinator.async_delete_schedule(data[const.ATTR_SCHEDULE_ID])
#         return self.json({"success": True})


@decorators.websocket_command(
    {
        vol.Required("type"): f"scheduler",
    }
)
@decorators.async_response
async def websocket_get_schedules(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Publish scheduler list data."""

    er = await hass.helpers.entity_registry.async_get_registry()

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
        vol.Required("type"): f"scheduler/item",
        vol.Required(ATTR_SCHEDULE_ID): cv.string,
    }
)
@decorators.async_response
async def websocket_get_schedule_item(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict,
) -> None:
    """Publish scheduler list data."""

    er = await hass.helpers.entity_registry.async_get_registry()

    for entry_id in hass.data[DOMAIN].keys():
        coordinator: VaillantCoordinator = hass.data[DOMAIN][entry_id]

        program = coordinator.data.programs.get(msg[ATTR_SCHEDULE_ID])
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
        vol.Required("type"): f"scheduler/tags",
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


# @decorators.websocket_command(
#     {
#         vol.Required("type"): f"{DOMAIN}_updated",
#     }
# )
# @decorators.async_response
# async def handle_subscribe_updates(
#     hass: HomeAssistant,
#     connection: ActiveConnection,
#     msg: dict,
# ) -> None:
#     """subscribe listeners when frontend connection is opened"""

#     listeners = []

#     @callback
#     def async_handle_event_item_created(schedule: ScheduleEntry):
#         """pass data to frontend when backend changes"""
#         connection.send_message(
#             {
#                 "id": msg["id"],
#                 "type": "event",
#                 "event": {  # data to pass with event
#                     "event": const.EVENT_ITEM_CREATED,
#                     "schedule_id": schedule.schedule_id,
#                 },
#             }
#         )

#     listeners.append(
#         async_dispatcher_connect(
#             hass, const.EVENT_ITEM_CREATED, async_handle_event_item_created
#         )
#     )

#     @callback
#     def async_handle_event_item_updated(schedule_id: str):
#         """pass data to frontend when backend changes"""
#         connection.send_message(
#             {
#                 "id": msg["id"],
#                 "type": "event",
#                 "event": {  # data to pass with event
#                     "event": const.EVENT_ITEM_UPDATED,
#                     "schedule_id": schedule_id,
#                 },
#             }
#         )

#     listeners.append(
#         async_dispatcher_connect(
#             hass, const.EVENT_ITEM_UPDATED, async_handle_event_item_updated
#         )
#     )

#     @callback
#     def async_handle_event_item_removed(schedule_id: str):
#         """pass data to frontend when backend changes"""
#         connection.send_message(
#             {
#                 "id": msg["id"],
#                 "type": "event",
#                 "event": {  # data to pass with event
#                     "event": const.EVENT_ITEM_REMOVED,
#                     "schedule_id": schedule_id,
#                 },
#             }
#         )

#     listeners.append(
#         async_dispatcher_connect(
#             hass, const.EVENT_ITEM_REMOVED, async_handle_event_item_removed
#         )
#     )

#     @callback
#     def async_handle_event_timer_updated(schedule_id: str):
#         """pass data to frontend when backend changes"""
#         connection.send_message(
#             {
#                 "id": msg["id"],
#                 "type": "event",
#                 "event": {  # data to pass with event
#                     "event": const.EVENT_TIMER_UPDATED,
#                     "schedule_id": schedule_id,
#                 },
#             }
#         )

#     listeners.append(
#         async_dispatcher_connect(
#             hass, const.EVENT_TIMER_UPDATED, async_handle_event_timer_updated
#         )
#     )

#     @callback
#     def async_handle_event_timer_finished(schedule_id: str):
#         """pass data to frontend when backend changes"""
#         connection.send_message(
#             {
#                 "id": msg["id"],
#                 "type": "event",
#                 "event": {  # data to pass with event
#                     "event": const.EVENT_TIMER_FINISHED,
#                     "schedule_id": schedule_id,
#                 },
#             }
#         )

#     listeners.append(
#         async_dispatcher_connect(
#             hass, const.EVENT_TIMER_FINISHED, async_handle_event_timer_finished
#         )
#     )

#     def unsubscribe_listeners():
#         """unsubscribe listeners when frontend connection closes"""
#         while len(listeners):
#             listeners.pop()()

#     connection.subscriptions[msg["id"]] = unsubscribe_listeners
#     connection.send_result(msg["id"])


async def async_register_websockets(hass: HomeAssistant) -> None:
    # hass.http.register_view(SchedulesAddView)
    # hass.http.register_view(SchedulesEditView)
    # hass.http.register_view(SchedulesRemoveView)

    hass.components.websocket_api.async_register_command(websocket_get_schedules)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_item)
    hass.components.websocket_api.async_register_command(websocket_get_tags)
    # hass.components.websocket_api.async_register_command(handle_subscribe_updates)
