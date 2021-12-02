"""
Custom integration to integrate Vaillant vSMART with Home Assistant.

For more details about this integration, please refer to
https://github.com/MislavMandaric/home-assistant-vaillant-vsmart
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_TOKEN
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from vaillant_netatmo_api import ThermostatClient, Token, TokenStore

from .const import (
    DOMAIN,
    PLATFORMS,
)
from .entity import VaillantCoordinator

from .websockets import async_register_websockets


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up Vaillant vSMART component."""

    hass.data.setdefault(DOMAIN, {})

    await async_register_websockets(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vaillant vSMART from a config entry."""

    def handle_token_update(token: Token) -> None:
        data = entry.data.copy()
        data[CONF_TOKEN] = token.serialize()

        hass.config_entries.async_update_entry(entry, data=data)

    client_id = entry.data.get(CONF_CLIENT_ID)
    client_secret = entry.data.get(CONF_CLIENT_SECRET)
    token = Token.deserialize(entry.data.get(CONF_TOKEN))

    client = ThermostatClient(
        get_async_client(hass),
        TokenStore(client_id, client_secret, token, handle_token_update),
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
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
