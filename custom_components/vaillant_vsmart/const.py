"""Constants for Vaillant vSMART."""

import re
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.const import (
    WEEKDAYS,
    ATTR_ENTITY_ID,
    SUN_EVENT_SUNRISE,
    SUN_EVENT_SUNSET,
    ATTR_SERVICE,
    ATTR_SERVICE_DATA,
    CONF_CONDITIONS,
    CONF_ATTRIBUTE,
    ATTR_NAME,
)


OffsetTimePattern = re.compile(r"^([a-z]+)([-|\+]{1})([0-9:]+)$")


def validate_time(time):
    """Input must be a valid time."""

    res = OffsetTimePattern.match(time)
    if not res:
        if dt_util.parse_time(time):
            return time
        else:
            raise vol.Invalid(f"Invalid time entered: {time}")
    else:
        if res.group(1) not in [SUN_EVENT_SUNRISE, SUN_EVENT_SUNSET]:
            raise vol.Invalid(f"Invalid time entered: {time}")
        elif res.group(2) not in ["+", "-"]:
            raise vol.Invalid(f"Invalid time entered: {time}")
        elif not dt_util.parse_time(res.group(3)):
            raise vol.Invalid(f"Invalid time entered: {time}")
        else:
            return time


def validate_date(value: str) -> str:
    """Input must be either none or a valid date."""

    if value is None:
        return None
    date = dt_util.parse_date(value)
    if date is None:
        raise vol.Invalid(f"Invalid date entered: {value}")
    else:
        return date.strftime("%Y-%m-%d")


# Base component constants
NAME = "Vaillant vSMART"
DOMAIN = "vaillant_vsmart"

# Platforms
CLIMATE = "climate"
NUMBER = "number"
SWITCH = "switch"
SENSOR = "sensor"
SELECT = "select"
PLATFORMS = [CLIMATE, NUMBER, SWITCH, SENSOR, SELECT]

# Configuration and options
CONF_APP_VERSION = "app_version"
CONF_USER_PREFIX = "user_prefix"

DAY_TYPE_DAILY = "daily"
DAY_TYPE_WORKDAY = "workday"
DAY_TYPE_WEEKEND = "weekend"

ATTR_CONDITION_TYPE = "condition_type"
CONDITION_TYPE_AND = "and"
CONDITION_TYPE_OR = "or"

ATTR_MATCH_TYPE = "match_type"
MATCH_TYPE_EQUAL = "is"
MATCH_TYPE_UNEQUAL = "not"
MATCH_TYPE_BELOW = "below"
MATCH_TYPE_ABOVE = "above"

ATTR_REPEAT_TYPE = "repeat_type"
REPEAT_TYPE_REPEAT = "repeat"
REPEAT_TYPE_SINGLE = "single"
REPEAT_TYPE_PAUSE = "pause"

ATTR_START = "start"
ATTR_STOP = "stop"
ATTR_TIMESLOTS = "timeslots"
ATTR_WEEKDAYS = "weekdays"
ATTR_ENABLED = "enabled"
ATTR_SCHEDULE_ID = "schedule_id"
ATTR_ACTIONS = "actions"
ATTR_VALUE = "value"
ATTR_TAGS = "tags"
ATTR_SCHEDULES = "schedules"
ATTR_START_DATE = "start_date"
ATTR_END_DATE = "end_date"

CONDITION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_VALUE): vol.Any(int, float, str),
        vol.Optional(CONF_ATTRIBUTE): cv.string,
        vol.Required(ATTR_MATCH_TYPE): vol.In(
            [MATCH_TYPE_EQUAL, MATCH_TYPE_UNEQUAL, MATCH_TYPE_BELOW, MATCH_TYPE_ABOVE]
        ),
    }
)


ACTION_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_SERVICE): cv.entity_id,
        vol.Optional(ATTR_SERVICE_DATA): dict,
    }
)


TIMESLOT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_START): validate_time,
        vol.Optional(ATTR_STOP): validate_time,
        vol.Optional(CONF_CONDITIONS): vol.All(  # TODO: Not supported
            cv.ensure_list, vol.Length(min=1), [CONDITION_SCHEMA]
        ),
        vol.Optional(ATTR_CONDITION_TYPE): vol.In(  # TODO: Not supported
            [
                CONDITION_TYPE_AND,
                CONDITION_TYPE_OR,
            ]
        ),
        vol.Required(ATTR_ACTIONS): vol.All(
            cv.ensure_list, vol.Length(min=1), [ACTION_SCHEMA]
        ),
    }
)


SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Optional(
            ATTR_WEEKDAYS, default=[DAY_TYPE_DAILY]
        ): vol.All(  # TODO: Not supported
            cv.ensure_list,
            vol.Unique(),
            vol.Length(min=1),
            [
                vol.In(
                    WEEKDAYS
                    + [
                        DAY_TYPE_WORKDAY,
                        DAY_TYPE_WEEKEND,
                        DAY_TYPE_DAILY,
                    ]
                )
            ],
        ),
        vol.Optional(
            ATTR_START_DATE, default=None
        ): validate_date,  # TODO: Not supported
        vol.Optional(ATTR_END_DATE, default=None): validate_date,  # TODO: Not supported
        vol.Required(ATTR_TIMESLOTS): vol.All(
            cv.ensure_list, vol.Length(min=1), [TIMESLOT_SCHEMA]
        ),
        vol.Required(ATTR_REPEAT_TYPE): vol.In(  # TODO: Not supported
            [
                REPEAT_TYPE_REPEAT,
                REPEAT_TYPE_SINGLE,
                REPEAT_TYPE_PAUSE,
            ]
        ),
        vol.Optional(ATTR_NAME): vol.Any(cv.string, None),
        vol.Optional(ATTR_TAGS): vol.All(
            cv.ensure_list, vol.Unique(), [cv.string]
        ),  # TODO: Not supported
    }
)
