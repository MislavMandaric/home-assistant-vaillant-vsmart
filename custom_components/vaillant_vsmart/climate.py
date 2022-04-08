"""The Vaillant vSMART climate platform."""
from __future__ import annotations

import datetime
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_HOME,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vaillant_netatmo_api import ApiException, SetpointMode, SystemMode

from .const import (
    DOMAIN,
)
from .entity import VaillantCoordinator, VaillantEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_TEMPERATURE_INCREASE = 1

PRESET_SUMMER = "Summer"
PRESET_WINTER = "Winter"

SUPPORTED_FEATURES = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE
SUPPORTED_HVAC_MODES = [HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF]
SUPPORTED_PRESET_MODES = [PRESET_SUMMER, PRESET_WINTER, PRESET_AWAY, PRESET_HOME]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up Vaillant vSMART from a config entry."""

    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    new_devices = [
        VaillantClimate(coordinator, device.id, module.id)
        for device in coordinator.data.devices.values()
        for module in device.modules
    ]
    async_add_devices(new_devices)


class VaillantClimate(VaillantEntity, ClimateEntity):
    """Vaillant vSMART Climate."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return self._module.id

    @property
    def name(self) -> str:
        """Return the name of the climate."""

        return self._module.module_name

    @property
    def supported_features(self) -> int:
        """Return the flag of supported features for the climate."""

        return SUPPORTED_FEATURES

    @property
    def temperature_unit(self) -> str:
        """Return the measurement unit for all temperature values."""

        return TEMP_CELSIUS

    @property
    def current_temperature(self) -> float:
        """Return the current room temperature."""

        return self._module.measured.temperature

    @property
    def target_temperature(self) -> float:
        """Return the targeted room temperature."""

        return self._module.measured.setpoint_temp

    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of available HVAC operation modes."""

        return SUPPORTED_HVAC_MODES

    @property
    def hvac_mode(self) -> str:
        """
        Return currently selected HVAC operation mode.
        """

        if self._device.system_mode == SystemMode.FROSTGUARD:
            return HVAC_MODE_OFF

        if self._module.setpoint_manual.setpoint_activate:
            return HVAC_MODE_HEAT

        return HVAC_MODE_AUTO

    @property
    def hvac_action(self) -> str:
        """
        Return the currently running HVAC action.
        """

        if self._device.system_mode == SystemMode.FROSTGUARD:
            return CURRENT_HVAC_OFF

        try:
            if self._module.measured.temperature < self._module.measured.setpoint_temp:
                return CURRENT_HVAC_HEAT
        except TypeError as ex:
            _LOGGER.exception(ex)

        return CURRENT_HVAC_IDLE

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available HVAC preset modes."""

        return SUPPORTED_PRESET_MODES

    @property
    def preset_mode(self) -> str:
        """Return the currently selected HVAC preset mode."""

        if self._module.setpoint_away.setpoint_activate:
            return PRESET_AWAY

        if self._device.system_mode == SystemMode.SUMMER:
            return PRESET_SUMMER

        if self._device.system_mode == SystemMode.WINTER:
            return PRESET_WINTER

        return

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Select new HVAC operation mode."""

        _LOGGER.debug(f"Setting HVAC mode to: {hvac_mode}")

        if hvac_mode == HVAC_MODE_OFF:
            try:
                await self._client.async_set_system_mode(
                    self._device_id,
                    self._module_id,
                    SystemMode.FROSTGUARD,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)
        elif hvac_mode == HVAC_MODE_HEAT:
            if self._device.system_mode == SystemMode.FROSTGUARD:
                return

            endtime = datetime.datetime.now() + datetime.timedelta(
                minutes=self._device.setpoint_default_duration
            )
            new_temperature = (
                self._module.measured.temperature + DEFAULT_TEMPERATURE_INCREASE
            )
            try:
                await self._client.async_set_minor_mode(
                    self._device_id,
                    self._module_id,
                    SetpointMode.MANUAL,
                    True,
                    setpoint_endtime=endtime,
                    setpoint_temp=new_temperature,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)
        elif hvac_mode == HVAC_MODE_AUTO:
            if self._device.system_mode == SystemMode.FROSTGUARD:
                try:
                    await self._client.async_set_system_mode(
                        self._device_id,
                        self._module_id,
                        SystemMode.SUMMER,
                    )
                except ApiException as ex:
                    _LOGGER.exception(ex)
            else:
                try:
                    await self._client.async_set_minor_mode(
                        self._device_id,
                        self._module_id,
                        SetpointMode.MANUAL,
                        False,
                    )
                except ApiException as ex:
                    _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Select new HVAC preset mode."""

        _LOGGER.debug(f"Setting HVAC preset mode to: {preset_mode}")

        if self._device.system_mode == SystemMode.FROSTGUARD:
            return

        if preset_mode == PRESET_AWAY:
            try:
                await self._client.async_set_minor_mode(
                    self._device_id,
                    self._module_id,
                    SetpointMode.AWAY,
                    True,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)
        elif preset_mode == PRESET_HOME:
            try:
                await self._client.async_set_minor_mode(
                    self._device_id,
                    self._module_id,
                    SetpointMode.AWAY,
                    False,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)
        elif preset_mode == PRESET_SUMMER:
            try:
                await self._client.async_set_system_mode(
                    self._device_id,
                    self._module_id,
                    SystemMode.SUMMER,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)
        elif preset_mode == PRESET_WINTER:
            try:
                await self._client.async_set_system_mode(
                    self._device_id,
                    self._module_id,
                    SystemMode.WINTER,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Update target room temperature value."""

        new_temperature = kwargs.get(ATTR_TEMPERATURE)
        if new_temperature is None:
            return

        _LOGGER.debug(f"Setting target temperature to: {new_temperature}")

        endtime = datetime.datetime.now() + datetime.timedelta(
            minutes=self._device.setpoint_default_duration
        )

        try:
            await self._client.async_set_minor_mode(
                self._device_id,
                self._module_id,
                SetpointMode.MANUAL,
                True,
                setpoint_endtime=endtime,
                setpoint_temp=new_temperature,
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()
