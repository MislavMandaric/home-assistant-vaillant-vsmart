"""The Vaillant vSMART binary sensor platform (boiler warnings and status)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .boiler_errors import (
    KNOWN_BOILER_ERRORS,
    errors_for_device,
    find_status_value,
    has_status_key,
)
from .const import DOMAIN
from .entity import VaillantCoordinator, VaillantHomestatusEntity

# Values in boiler_error which are no problem
NON_PROBLEM_ERRORS = {"boiler_responding"}

# homestatus field -> (device class, entity category)
STATUS_BINARY_SENSORS: dict[
    str, tuple[BinarySensorDeviceClass | None, EntityCategory | None]
] = {
    "ebus_error": (BinarySensorDeviceClass.PROBLEM, None),
    "boiler_status": (BinarySensorDeviceClass.RUNNING, None),
    "dhw_enabled": (None, None),
    "anticipating": (None, None),
    "dhw_always_on": (None, EntityCategory.DIAGNOSTIC),
    "emf_avail": (None, EntityCategory.DIAGNOSTIC),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART binary sensors from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]
    status = coordinator.data.module_status

    new_devices: list[BinarySensorEntity] = []
    for device in coordinator.data.devices.values():
        new_devices += [
            VaillantBoilerErrorBinarySensor(coordinator, device.id, code)
            for code in KNOWN_BOILER_ERRORS
        ]
        new_devices.append(VaillantBoilerProblemBinarySensor(coordinator, device.id))
        # Status fields are only added if this installation reports them
        new_devices += [
            VaillantStatusBinarySensor(coordinator, device.id, key)
            for key in STATUS_BINARY_SENSORS
            if has_status_key(status, key)
        ]

    async_add_devices(new_devices)


class _VaillantBoilerBinarySensorBase(VaillantHomestatusEntity, BinarySensorEntity):
    """Common logic for sensors based on the boiler_error list."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def _errors(self) -> list[str]:
        """Return the boiler errors of this device."""

        return errors_for_device(
            self.coordinator.data.boiler_errors or {}, self._device_id
        )


class VaillantBoilerErrorBinarySensor(_VaillantBoilerBinarySensorBase):
    """Binary sensor which is on while a specific boiler error is reported."""

    def __init__(
        self, coordinator: VaillantCoordinator, device_id: str, error_code: str
    ) -> None:
        """Initialize."""

        super().__init__(coordinator, device_id)
        self._error_code = error_code

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_boiler_error_{self._error_code}"

    @property
    def translation_key(self) -> str:
        """Return the translation key to translate the entity's name."""

        return f"boiler_error_{self._error_code}"

    @property
    def is_on(self) -> bool:
        """Return True if the error is active."""

        return self._error_code in self._errors


class VaillantBoilerProblemBinarySensor(_VaillantBoilerBinarySensorBase):
    """Binary sensor which is on while any boiler error is reported."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_boiler_problem"

    @property
    def translation_key(self) -> str:
        """Return the translation key to translate the entity's name."""

        return "boiler_problem"

    @property
    def is_on(self) -> bool:
        """Return True if any problem is reported."""

        return any(e not in NON_PROBLEM_ERRORS for e in self._errors)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the raw error codes."""

        return {"boiler_errors": self._errors}


class VaillantStatusBinarySensor(VaillantHomestatusEntity, BinarySensorEntity):
    """Binary sensor for a boolean field of the homestatus module."""

    def __init__(
        self, coordinator: VaillantCoordinator, device_id: str, key: str
    ) -> None:
        """Initialize."""

        super().__init__(coordinator, device_id)
        self._key = key
        device_class, category = STATUS_BINARY_SENSORS[key]
        self._attr_device_class = device_class
        self._attr_entity_category = category

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self._device.id}_status_{self._key}"

    @property
    def translation_key(self) -> str:
        """Return the translation key to translate the entity's name."""

        return f"status_{self._key}"

    @property
    def is_on(self) -> bool | None:
        """Return the state of the field."""

        found, value = find_status_value(
            self.coordinator.data.module_status, self._device_id, self._key
        )
        return bool(value) if found and value is not None else None
