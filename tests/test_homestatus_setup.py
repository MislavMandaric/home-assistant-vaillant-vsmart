"""Setup test: the integration loads all platforms with homestatus entities."""

import json
from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_TOKEN
from pytest_homeassistant_custom_component.common import MockConfigEntry
from vaillant_netatmo_api import Device, Home

from custom_components.vaillant_vsmart.const import DOMAIN

DEVICE_ID = "70:ee:50:00:00:01"

HOMESTATUS = {
    "status": "ok",
    "body": {
        "home": {
            "id": "home1",
            "modules": [
                {
                    "id": DEVICE_ID,
                    "type": "NAVaillant",
                    "boiler_error": ["water_pressure"],
                    "ebus_error": False,
                    "boiler_status": True,
                    "dhw_setpoint_temperature": 50,
                    "oem_serial": "123",
                }
            ],
        }
    },
}


async def test_setup_with_homestatus(hass):
    """All homestatus entities are created and reflect the response."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CLIENT_ID: "id",
            CONF_CLIENT_SECRET: "secret",
            CONF_TOKEN: json.dumps(
                {"access_token": "a", "refresh_token": "r", "expires_at": 9e12}
            ),
        },
    )
    entry.add_to_hass(hass)
    device = Device(
        _id=DEVICE_ID,
        type="NAVaillant",
        station_name="Heizung",
        outdoor_temperature={"te": 10},
        system_mode="winter",
        modules=[{"_id": "04:00:00:00:00:02", "module_name": "Thermostat"}],
    )
    target = "custom_components.vaillant_vsmart.ThermostatClient"
    with patch(target) as client_cls:
        client = client_cls.return_value
        client.async_get_homes_data = AsyncMock(return_value=[Home(id="home1")])
        client.async_get_thermostats_data = AsyncMock(return_value=[device])
        client.async_get_measure = AsyncMock(return_value=[])
        client._post = AsyncMock(return_value=HOMESTATUS)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    states = {s.entity_id: s.state for s in hass.states.async_all()}
    assert states["binary_sensor.heizung_water_pressure_low"] == "on"
    assert states["binary_sensor.heizung_maintenance_required"] == "off"
    assert states["binary_sensor.heizung_boiler_problem"] == "on"
    assert states["binary_sensor.heizung_ebus_error"] == "off"
    assert states["binary_sensor.heizung_boiler_active"] == "on"
    assert states["sensor.heizung_hot_water_setpoint"] == "50"
    assert states["sensor.heizung_boiler_serial_number"] == "123"
