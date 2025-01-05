"""Constants for Vaillant vSMART."""
from vaillant_netatmo_api import MeasurementType

# Base component constants
NAME = "Vaillant vSMART"
DOMAIN = "vaillant_vsmart"

# Platforms
CLIMATE = "climate"
NUMBER = "number"
SELECT = "select"
SENSOR = "sensor"
SWITCH = "switch"
WATER_HEATER = "water_heater"
PLATFORMS = [CLIMATE, NUMBER, SELECT, SENSOR, SWITCH, WATER_HEATER]

# Configuration and options
CONF_APP_VERSION = "app_version"
CONF_USER_PREFIX = "user_prefix"

SUPPORTED_ENERGY_MEASUREMENT_TYPES = [MeasurementType.SUM_ENERGY_GAS_HEATING, MeasurementType.SUM_ENERGY_GAS_WATER,
                                      MeasurementType.SUM_ENERGY_ELEC_HEATING, MeasurementType.SUM_ENERGY_ELEC_WATER]

SUPPORTED_DURATION_MEASUREMENT_TYPES = [MeasurementType.SUM_BOILER_ON]
