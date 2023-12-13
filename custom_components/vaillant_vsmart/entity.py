"""Vaillant vSMART entity classes."""
from datetime import timedelta
import logging
from typing import Any
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from vaillant_netatmo_api import (
    ApiException,
    Device,
    MeasurementItem,
    MeasurementScale,
    MeasurementType,
    Module,
    Program,
    ThermostatClient,
    RequestUnauthorizedException,
)

from .const import DOMAIN


UPDATE_INTERVAL = timedelta(minutes=5)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EnergyMeasures:
    """Class to represent energy measures."""

    def __init__(
        self,
        gas_heating: MeasurementItem,
        gas_water: MeasurementItem,
        elec_heating: MeasurementItem,
        elec_water: MeasurementItem,
    ) -> None:
        """Initialize."""
        self._gas_heating = gas_heating
        self._gas_water = gas_water
        self._elec_heating = elec_heating
        self._elec_water = elec_water

    @property
    def gas_heating(self) -> MeasurementItem:
        """Retrun value of gas_heating measurement"""

        return self._gas_heating

    @property
    def gas_water(self) -> MeasurementItem:
        """Retrun value of gas_water measurement"""

        return self._gas_water

    @property
    def elec_heating(self) -> MeasurementItem:
        """Retrun value of gas_heating measurement"""

        return self._elec_heating

    @property
    def elec_water(self) -> MeasurementItem:
        """Retrun value of gas_water measurement"""

        return self._elec_water


class VaillantData:
    """Class holding data which coordinator provides to the entity."""

    def __init__(
        self,
        client: ThermostatClient,
        devices: list[Device],
        energy_measures: dict[str, EnergyMeasures],
    ) -> None:
        """Initialize."""

        self.client = client
        self.devices = {device.id: device for device in devices}
        self.modules = {
            module.id: module for device in devices for module in device.modules
        }
        self.programs = {
            program.id: program
            for device in devices
            for module in device.modules
            for program in module.therm_program_list
        }
        self.energy_measures = energy_measures


class VaillantCoordinator(DataUpdateCoordinator[VaillantData]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: ThermostatClient) -> None:
        """Initialize."""

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._update_method,
            update_interval=UPDATE_INTERVAL,
        )

        self._client = client

    async def _update_method(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        try:
            devices = await self._client.async_get_thermostats_data()
            measured_energy = await self.get_all_measurements(devices)

            return VaillantData(self._client, devices, measured_energy)
        except RequestUnauthorizedException as ex:
            raise ConfigEntryAuthFailed from ex
        except ApiException as ex:
            _LOGGER.exception(ex)
            raise UpdateFailed(f"Error communicating with API: {ex}") from ex

    async def get_all_measurements(self, devices: list[Device]) -> MeasurementItem:
        """Returns all measurements for devices"""
        return {
            module.id: EnergyMeasures(heating, water, elec_heating, elec_water)
            for device in devices
            for module in device.modules
            for heating in await self._client.async_get_measure(
                device.id,
                module.id,
                MeasurementType.SUM_ENERGY_GAS_HEATING,
                MeasurementScale.DAY,
                datetime.now() - timedelta(days=7),
            )
            for water in await self._client.async_get_measure(
                device.id,
                module.id,
                MeasurementType.SUM_ENERGY_GAS_WATER,
                MeasurementScale.DAY,
                datetime.now() - timedelta(days=7),
            )
            for elec_heating in await self._client.async_get_measure(
                device.id,
                module.id,
                MeasurementType.SUM_ENERGY_ELEC_HEATING,
                MeasurementScale.DAY,
                datetime.now() - timedelta(days=7),
            )
            for elec_water in await self._client.async_get_measure(
                device.id,
                module.id,
                MeasurementType.SUM_ENERGY_ELEC_WATER,
                MeasurementScale.DAY,
                datetime.now() - timedelta(days=7),
            )
        }


class VaillantDeviceEntity(CoordinatorEntity[VaillantData]):
    """Base class for Vaillant device entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[VaillantData],
        device_id: str,
    ):
        """Initialize."""

        super().__init__(coordinator)

        self._device_id = device_id

    @property
    def _client(self) -> ThermostatClient:
        """Retrun the instance of the client which enables HTTP communication with the API."""

        return self.coordinator.data.client

    @property
    def _device(self) -> Device:
        """Return the device which this entity represents."""

        return self.coordinator.data.devices[self._device_id]

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return self._device.id

    @property
    def has_entity_name(self) -> bool:
        """Return if entity is using new entity naming conventions."""

        return True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return all device info available for this entity."""

        return {
            "identifiers": {(DOMAIN, self._device.id)},
            "name": self._device.station_name,
            "sw_version": self._device.firmware,
            "manufacturer": self._device.type,
        }


class VaillantModuleEntity(CoordinatorEntity[VaillantData]):
    """Base class for Vaillant module entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[VaillantData],
        device_id: str,
        module_id: str,
    ):
        """Initialize."""

        super().__init__(coordinator)

        self._device_id = device_id
        self._module_id = module_id

    @property
    def _client(self) -> ThermostatClient:
        """Retrun the instance of the client which enables HTTP communication with the API."""

        return self.coordinator.data.client

    @property
    def _device(self) -> Device:
        """Return the device which this entity represents."""

        return self.coordinator.data.devices[self._device_id]

    @property
    def _module(self) -> Module:
        """Return the module which this entity represents."""

        return self.coordinator.data.modules[self._module_id]

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return self._module.id

    @property
    def has_entity_name(self) -> bool:
        """Return if entity is using new entity naming conventions."""

        return True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return all device info available for this entity."""

        return {
            "identifiers": {(DOMAIN, self._module.id)},
            "name": self._module.module_name,
            "sw_version": self._module.firmware,
            "manufacturer": self._device.type,
            "via_device": (DOMAIN, self._device.id),
        }


class VaillantProgramEntity(CoordinatorEntity[VaillantData]):
    """Base class for Vaillant program entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[VaillantData],
        device_id: str,
        module_id: str,
        program_id: str,
    ):
        """Initialize."""

        super().__init__(coordinator)

        self._device_id = device_id
        self._module_id = module_id
        self._program_id = program_id

    @property
    def _client(self) -> ThermostatClient:
        """Retrun the instance of the client which enables HTTP communication with the API."""

        return self.coordinator.data.client

    @property
    def _device(self) -> Device:
        """Return the device which this entity represents."""

        return self.coordinator.data.devices[self._device_id]

    @property
    def _module(self) -> Module:
        """Return the module which this entity represents."""

        return self.coordinator.data.modules[self._module_id]

    @property
    def _program(self) -> Program:
        """Return the program which this entity represents."""

        return self.coordinator.data.programs[self._program_id]

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return self._program.id

    @property
    def has_entity_name(self) -> bool:
        """Return if entity is using new entity naming conventions."""

        return True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return all device info available for this entity."""

        return {
            "identifiers": {(DOMAIN, self._module.id)},
            "name": self._module.module_name,
            "sw_version": self._module.firmware,
            "manufacturer": self._device.type,
            "via_device": (DOMAIN, self._device.id),
        }
