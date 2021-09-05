"""Sensor platform for Vaillant vSMART."""
from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VaillantEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([VaillantSensor(coordinator, entry)])


class VaillantSensor(VaillantEntity):
    """vaillant_vsmart Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("body")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON
