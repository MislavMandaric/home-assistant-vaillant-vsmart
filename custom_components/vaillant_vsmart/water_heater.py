"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import logging
import math

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vaillant_netatmo_api import ApiException, SystemMode

from .const import (
    DOMAIN,
)
from .entity import VaillantCoordinator, VaillantDeviceEntity

_LOGGER = logging.getLogger(__name__)

OPERATION_HEATING = "heating"
OPERATION_HOT_WATER_ONLY = "hot_water_only"
OPERATION_STAND_BY = "stand_by"

SUPPORTED_FEATURES = (
    WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.OPERATION_MODE
)
SUPPORTED_WATER_HEATER_MODES = [OPERATION_HEATING,
                                OPERATION_HOT_WATER_ONLY, OPERATION_STAND_BY]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantWaterHeater(coordinator, device.id)
        for device in coordinator.data.devices.values()
    ]
    async_add_devices(new_devices)


class VaillantWaterHeater(VaillantDeviceEntity, WaterHeaterEntity):
    """Vaillant vSMART Water Heater."""

    @property
    def name(self) -> str:
        """Return the name of the water heater."""

        return None

    @property
    def translation_key(self) -> str:
        """Return the translation key of the water heater."""

        return "vaillant"

    @property
    def supported_features(self) -> int:
        """Return the flag of supported features for the water heater."""

        return SUPPORTED_FEATURES

    @property
    def temperature_unit(self) -> str:
        """Return the measurement unit for all temperature values."""

        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self) -> float:
        """Return the current water temperature."""

        return self._device.dhw

    @property
    def target_temperature(self) -> float:
        """Return the targeted water temperature."""

        return self._device.dhw

    @property
    def min_temp(self) -> float:
        """Return the min supported water temperature."""

        return self._device.dhw_min

    @property
    def max_temp(self) -> float:
        """Return the max supported water temperature."""

        return self._device.dhw_max

    @property
    def operation_list(self) -> list[str]:
        """Return the list of available operation modes."""

        return SUPPORTED_WATER_HEATER_MODES

    @property
    def current_operation(self) -> str:
        """Return currently selected operation mode."""

        if self._device.system_mode == SystemMode.FROSTGUARD:
            return OPERATION_STAND_BY
        elif self._device.system_mode == SystemMode.SUMMER:
            return OPERATION_HOT_WATER_ONLY
        else:
            return OPERATION_HEATING

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Select new operation mode."""

        _LOGGER.debug(
            "Setting water heater operation mode to: %s", operation_mode)

        try:
            system_mode = SystemMode.FROSTGUARD if operation_mode == OPERATION_STAND_BY else \
                SystemMode.SUMMER if operation_mode == OPERATION_HOT_WATER_ONLY else \
                SystemMode.WINTER

            await self._client.async_set_system_mode(
                self._device_id,
                self._device.modules[0].id,
                system_mode,
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Update target water temperature value."""

        new_temperature = kwargs.get(ATTR_TEMPERATURE)
        if new_temperature is None:
            return

        _LOGGER.debug("Setting target temperature to: %s", new_temperature)

        try:
            await self._client.async_set_hot_water_temperature(
                self._device_id,
                int(math.ceil(new_temperature)),
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()
