"""Parsing of the module status reported by the /api/homestatus endpoint.

The official Vaillant vSMART app reads the modules returned by
``api/homestatus``, e.g. the list ``boiler_error`` for dashboard warnings
(``water_pressure`` -> "Water pressure low, please refill"), ``ebus_error``
or the hot water (dhw) settings.
"""

from __future__ import annotations

from typing import Any

HOMESTATUS_PATH = "api/homestatus"

WATER_PRESSURE = "water_pressure"
MAINTENANCE = "maintenance"
BOILER_ERROR_INTERNAL = "boiler_error_internal"
BOILER_NOT_RESPONDING = "boiler_not_responding"
BOILER_FLAME = "boiler_flame"
AIR_PRESSURE = "air_pressure"
BOILER_TEMPERATURE = "boiler_temperature"

# All values of boiler_error known from the app, except "boiler_responding"
KNOWN_BOILER_ERRORS = (
    WATER_PRESSURE,
    MAINTENANCE,
    BOILER_ERROR_INTERNAL,
    BOILER_NOT_RESPONDING,
    BOILER_FLAME,
    AIR_PRESSURE,
    BOILER_TEMPERATURE,
)


def parse_module_status(body: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the raw status dict per module id from a homestatus response."""

    modules = (body.get("body") or {}).get("home", {}).get("modules") or []
    return {m["id"]: m for m in modules if isinstance(m, dict) and m.get("id")}


def parse_boiler_errors(body: dict[str, Any]) -> dict[str, list[str]]:
    """Return boiler errors per module id from a homestatus response."""

    return boiler_errors_from_status(parse_module_status(body))


def boiler_errors_from_status(
    status: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    """Return boiler errors per module id from parsed module status."""

    result: dict[str, list[str]] = {}
    for module_id, module in status.items():
        if "boiler_error" not in module:
            continue
        errors = module.get("boiler_error") or []
        if isinstance(errors, str):
            errors = [errors]
        result[module_id] = sorted({str(e) for e in errors if e})
    return result


def errors_for_device(
    errors_by_module: dict[str, list[str]], device_id: str
) -> list[str]:
    """Return the boiler errors relevant for a device.

    The gateway module usually has the same id as the device of the old API.
    If it cannot be matched, all errors of the home are returned.
    """

    if device_id in errors_by_module:
        return errors_by_module[device_id]
    return sorted({e for errors in errors_by_module.values() for e in errors})


def find_status_value(
    status: dict[str, dict[str, Any]] | None, preferred_id: str, key: str
) -> tuple[bool, Any]:
    """Return (found, value) of a status field.

    The module with ``preferred_id`` is used if it reports the field,
    otherwise the first module which reports it.
    """

    if not status:
        return False, None
    preferred = status.get(preferred_id)
    if preferred is not None and key in preferred:
        return True, preferred[key]
    for module in status.values():
        if key in module:
            return True, module[key]
    return False, None


def has_status_key(status: dict[str, dict[str, Any]] | None, key: str) -> bool:
    """Return True if any module reports the field."""

    return bool(status) and any(key in m for m in status.values())
