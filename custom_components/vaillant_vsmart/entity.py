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


class VaillantData:
    """Class holding data which coordinator provides to the entity."""

    def __init__(
        self,
        client: ThermostatClient,
        devices: dict[str, Device],
        modules: dict[tuple[str, str], Module],
        programs: dict[tuple[str, str, str], Program],
        gas_heating_measurements: dict[str, MeasurementItem],
        gas_water_measurements: dict[str, MeasurementItem],
        elec_heating_measurements: dict[str, MeasurementItem],
        elec_water_measurements: dict[str, MeasurementItem],
    ) -> None:
        """Initialize."""

        self.client = client
        self.devices = devices
        self.modules = modules
        self.programs = programs
        self.gas_heating_measurements = gas_heating_measurements
        self.gas_water_measurements = gas_water_measurements
        self.elec_heating_measurements = elec_heating_measurements
        self.elec_water_measurements = elec_water_measurements


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
            devices = await self._get_devices()
            modules = await self._get_modules(devices.values())
            programs = await self._get_programs(devices.values())
            gas_heating_measurements = await self._get_measurements(devices.values(), MeasurementType.SUM_ENERGY_GAS_HEATING)
            gas_water_measurements = await self._get_measurements(devices.values(), MeasurementType.SUM_ENERGY_GAS_WATER)
            elec_heating_measurements = await self._get_measurements(devices.values(), MeasurementType.SUM_ENERGY_ELEC_HEATING)
            elec_water_measurements = await self._get_measurements(devices.values(), MeasurementType.SUM_ENERGY_ELEC_WATER)

            print(programs)

            return VaillantData(
                self._client,
                devices,
                modules,
                programs,
                gas_heating_measurements,
                gas_water_measurements,
                elec_heating_measurements,
                elec_water_measurements,
            )
        except RequestUnauthorizedException as ex:
            raise ConfigEntryAuthFailed from ex
        except ApiException as ex:
            _LOGGER.exception(ex)
            raise UpdateFailed(f"Error communicating with API: {ex}") from ex

    async def _get_devices(self) -> dict[str, Device]:
        devices = await self._client.async_get_thermostats_data()
        return {
            device.id: device
            for device in devices
        }

    async def _get_modules(self, devices: list[Device]) -> dict[tuple[str, str], Module]:
        return {
            (device.id, module.id): module
            for device in devices for module in device.modules
        }

    async def _get_programs(self, devices: list[Device]) -> dict[tuple[str, str, str], Program]:
        return {
            (device.id, module.id, program.id): program
            for device in devices for module in device.modules for program in module.therm_program_list
        }

    async def _get_measurements(self, devices: list[Device], type: MeasurementType) -> dict[str, MeasurementItem]:
        return {
            device.id: await self._get_measurement(device.id, device.modules[0].id, type)
            for device in devices
        }

    async def _get_measurement(self, device_id: str, module_id: str, type: MeasurementType) -> MeasurementItem:
        measurements = await self._client.async_get_measure(
                device_id,
                module_id,
                type,
                MeasurementScale.DAY,
                datetime.now() - timedelta(days=7),
            )
        if len(measurements) > 0:
            return measurements[-1]
        return None


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

        return self.coordinator.data.modules[(self._device_id, self._module_id)]

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

        return self.coordinator.data.modules[(self._device_id, self._module_id)]

    @property
    def _program(self) -> Program:
        """Return the program which this entity represents."""

        return self.coordinator.data.programs[(self._device_id, self._module_id, self._program_id)]

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
