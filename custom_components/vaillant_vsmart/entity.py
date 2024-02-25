"""Vaillant vSMART entity classes."""
import copy
import datetime
from datetime import timedelta
import logging
from typing import Any

import jsonpickle
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
    Module,
    Program,
    ThermostatClient,
    RequestUnauthorizedException, MeasurementScale, MeasurementItem,
)

from .const import DOMAIN, MEASUREMENT_SENSORS, VaillantSensorEntityDescription

UPDATE_INTERVAL = timedelta(minutes=5)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class VaillantDataMeasure:
    def __init__(self, device: Device, module: Module, sensor: VaillantSensorEntityDescription,
                 measures: list[MeasurementItem] | None,
                 last_reset: datetime.datetime | None):
        self.last_reset = last_reset
        self.device = device
        self.module = module
        self.sensor = sensor
        self.measures = measures


class VaillantData:
    """Class holding data which coordinator provides to the entity."""

    def __init__(self, client: ThermostatClient, devices: list[Device],
                 measurements: list[VaillantDataMeasure]) -> None:
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
        self.measurements = measurements


class VaillantCoordinator(DataUpdateCoordinator[VaillantData]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: ThermostatClient) -> None:
        """Initialize."""

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

        self._client = client
        self.sensors: list[VaillantSensorEntityDescription] = []

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            devices = await self._client.async_get_thermostats_data()
            measurements: list[VaillantDataMeasure] = []
            for device in devices:
                for module in device.modules:
                    # Add measurements of gaz consumption (list defined in const.py)
                    _LOGGER.debug("Vaillant update")
                    try:
                        for measurement_sensor in MEASUREMENT_SENSORS:
                            sensor: VaillantSensorEntityDescription | None = None
                            for local_sensor in self.sensors:
                                if (local_sensor.key == measurement_sensor.key
                                        and local_sensor.device.id == device.id
                                        and local_sensor.module.id == module.id):
                                    sensor = local_sensor
                                    break
                            new_sensor = False
                            if sensor is None:
                                sensor = copy.copy(measurement_sensor)
                                sensor.device = device
                                sensor.module = module
                                self.sensors.append(sensor)
                                new_sensor = True
                            # Don't extract sensor information if it is disabled and it is not the first refresh of the sensor
                            if new_sensor is False and sensor.enabled is False:
                                _LOGGER.debug("Vaillant sensor %s is disabled, data won't be extracted",
                                              measurement_sensor.sensor_name)
                                measurements.append(VaillantDataMeasure(device, module, sensor, None, None))
                                continue
                            # Range : from the start of the current day until the end of the day
                            date_begin = datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                         microsecond=0)
                            date_end = date_begin + datetime.timedelta(days=1)
                            measured = await self._client.async_get_measure(device_id=device.id, module_id=module.id,
                                                                            type=sensor.measurement_type,
                                                                            scale=MeasurementScale.DAY,
                                                                            date_begin=date_begin,
                                                                            date_end=date_end)

                            _LOGGER.debug("Vaillant update measure for %s (%s -> %s): %s", sensor.sensor_name,
                                          date_begin.strftime("%m/%d/%Y %H:%M:%S"),
                                          date_end.strftime("%m/%d/%Y %H:%M:%S"),
                                          jsonpickle.encode(measured))
                            measurements.append(VaillantDataMeasure(device, module, sensor, measured, date_begin))
                            # Store the result in the module measured field
                            # setattr(module.measured, MeasurementType.SUM_ENERGY_GAS_HEATING.value, measured)
                    except Exception as ex:
                        _LOGGER.debug("Vaillant error during extraction of measures", exc_info=ex)

            return VaillantData(self._client, devices, measurements)
        except RequestUnauthorizedException as ex:
            raise ConfigEntryAuthFailed from ex
        except ApiException as ex:
            _LOGGER.exception(ex)
            raise UpdateFailed(f"Error communicating with API: {ex}") from ex


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
