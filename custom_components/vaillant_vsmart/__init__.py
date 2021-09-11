"""
Custom integration to integrate Vaillant vSMART with Home Assistant.

For more details about this integration, please refer to
https://github.com/MislavMandaric/home-assistant-vaillant-vsmart
"""
from __future__ import annotations

from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_TOKEN
from homeassistant.core import Config, HomeAssistant
from vaillant_netatmo_api import ThermostatClient, deserialize_token, serialize_token

from .const import (
    DOMAIN,
    PLATFORMS,
)
from .entity import VaillantCoordinator


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up Vaillant vSMART component."""

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vaillant vSMART from a config entry."""

    async def async_token_updater(
        token: OAuth2Token, refresh_token: str = None, access_token: str = None
    ) -> None:
        data = entry.data.copy()
        data[CONF_TOKEN] = serialize_token(token)

        hass.config_entries.async_update_entry(entry, data=data)

    client_id = entry.data.get(CONF_CLIENT_ID)
    client_secret = entry.data.get(CONF_CLIENT_SECRET)
    token = deserialize_token(entry.data.get(CONF_TOKEN))

    client = ThermostatClient(
        client_id,
        client_secret,
        token,
        async_token_updater,
    )

    coordinator = VaillantCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: VaillantCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()

    return unload_ok
