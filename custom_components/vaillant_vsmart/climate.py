"""The Vaillant vSMART climate platform."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACAction,
    HVACMode,
    ClimateEntityFeature,
    PRESET_AWAY,
    PRESET_NONE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vaillant_netatmo_api import ApiException, SetpointMode, SystemMode

from .const import (
    DOMAIN,
)
from .entity import VaillantCoordinator, VaillantModuleEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_TEMPERATURE_INCREASE = 1

SUPPORTED_FEATURES = (
    ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
)
SUPPORTED_HVAC_MODES = [HVACMode.AUTO, HVACMode.HEAT]
SUPPORTED_PRESET_MODES = [PRESET_NONE, PRESET_AWAY]

_HOME_ID = ""  # <-- Fill with your Home ID
_ROOM_ID = ""  # <-- Fill with your Room ID

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


class VaillantClimate(VaillantModuleEntity, ClimateEntity):
    """Vaillant vSMART Climate."""

    @property
    def name(self) -> str:
        """Return the name of the climate."""

        return None

    @property
    def supported_features(self) -> int:
        """Return the flag of supported features for the climate."""

        return SUPPORTED_FEATURES

    @property
    def temperature_unit(self) -> str:
        """Return the measurement unit for all temperature values."""

        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self) -> float:
        """Return the current room temperature."""

        return self._module.measured.temperature

    @property
    def target_temperature(self) -> float:
        """Return the targeted room temperature."""

        return (
            self._module.measured.est_setpoint_temp
            if self._module.measured.est_setpoint_temp is not None
            else self._module.measured.setpoint_temp
        )

    @property
    def hvac_action(self) -> HVACAction:
        """Return the currently running HVAC action."""

        if self._device.system_mode in [SystemMode.FROSTGUARD, SystemMode.SUMMER]:
            return HVACAction.OFF

        if self._module.boiler_status is True:
            return HVACAction.HEATING

        return HVACAction.IDLE

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC operation modes."""

        return SUPPORTED_HVAC_MODES

    @property
    def hvac_mode(self) -> HVACMode:
        """Return currently selected HVAC operation mode."""

        if self._module.setpoint_manual.setpoint_activate:
            return HVACMode.HEAT

        return HVACMode.AUTO

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available HVAC preset modes."""

        return SUPPORTED_PRESET_MODES

    @property
    def preset_mode(self) -> str:
        """Return the currently selected HVAC preset mode."""

        if self._module.setpoint_away.setpoint_activate:
            return PRESET_AWAY

        return PRESET_NONE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Select new HVAC operation mode."""

        _LOGGER.debug("Setting HVAC mode to: %s", hvac_mode)

        if hvac_mode == HVACMode.HEAT:
            endtime = datetime.now() + timedelta(
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
        elif hvac_mode == HVACMode.AUTO:
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

        _LOGGER.debug("Setting HVAC preset mode to: %s", preset_mode)

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
        elif preset_mode == PRESET_NONE:
            try:
                await self._client.async_set_minor_mode(
                    self._device_id,
                    self._module_id,
                    SetpointMode.AWAY,
                    False,
                )
            except ApiException as ex:
                _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Update target room temperature value."""

        new_temperature = kwargs.get(ATTR_TEMPERATURE)
        if new_temperature is None:
            return

        _LOGGER.debug("Setting target temperature to: %s", new_temperature)

        endtime = datetime.now() + timedelta(
            minutes=self._device.setpoint_default_duration
        )

        try:
            await self._client.async_set_state_room(
                _HOME_ID,
                _ROOM_ID,
                SetpointMode.MANUAL,
                True,
                setpoint_endtime=endtime,
                setpoint_temp=new_temperature,
            )
        except ApiException as ex:
            _LOGGER.exception(ex)

        await self.coordinator.async_request_refresh()
