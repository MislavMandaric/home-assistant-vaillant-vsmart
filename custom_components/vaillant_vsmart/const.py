"""Constants for Vaillant vSMART."""
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass
from vaillant_netatmo_api import MeasurementType

# Base component constants
NAME = "Vaillant vSMART"
DOMAIN = "vaillant_vsmart"

# Platforms
CLIMATE = "climate"
SELECT = "select"
SENSOR = "sensor"
SWITCH = "switch"
WATER_HEATER = "water_heater"
PLATFORMS = [CLIMATE, SELECT, SENSOR, SWITCH, WATER_HEATER]

# Configuration and options
CONF_APP_VERSION = "app_version"
CONF_USER_PREFIX = "user_prefix"


# Sensor entity descriptions for measurements
class VaillantSensorEntityDescription:
    def __init__(self, key: str, measurement_type: MeasurementType, sensor_name: str, device_class: SensorDeviceClass,
                 icon: str,
                 unit: str, conversion: float = 1, enabled=True):
        self.key = key
        self.measurement_type = measurement_type
        self.sensor_name: str = sensor_name
        self.device_class = device_class
        self.icon = icon
        self.unit = unit
        self.conversion = conversion
        self.enabled = enabled


# List of measurement sensors to create
MEASUREMENT_SENSORS: list[VaillantSensorEntityDescription] = [
    VaillantSensorEntityDescription(key="gaz_heating",
                                    measurement_type=MeasurementType.SUM_ENERGY_GAS_HEATING,
                                    sensor_name="Gaz heating",
                                    icon="mdi:radiator",
                                    device_class=SensorDeviceClass.ENERGY,
                                    unit="kWh",
                                    conversion=0.001),
    VaillantSensorEntityDescription(key="water_heating",
                                    measurement_type=MeasurementType.SUM_ENERGY_GAS_WATER,
                                    sensor_name="Gaz water heating",
                                    icon="mdi:bathtub",
                                    device_class=SensorDeviceClass.ENERGY,
                                    unit="kWh",
                                    conversion=0.001),
    VaillantSensorEntityDescription(key="elec_heating",
                                    measurement_type=MeasurementType.SUM_ENERGY_ELEC_HEATING,
                                    sensor_name="Electricity heating",
                                    icon="mdi:meter-electric",
                                    device_class=SensorDeviceClass.ENERGY,
                                    unit="Wh",
                                    enabled=False),
    VaillantSensorEntityDescription(key="elec_water__heating",
                                    measurement_type=MeasurementType.SUM_ENERGY_ELEC_WATER,
                                    sensor_name="Electricity water heating",
                                    icon="mdi:bathtub-outline",
                                    device_class=SensorDeviceClass.ENERGY,
                                    unit="Wh",
                                    enabled=False)
]
