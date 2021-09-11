"""Adds config flow for Vaillant vSMART."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from vaillant_netatmo_api import auth_client, serialize_token
import voluptuous as vol

from .const import (
    CONF_APP_VERSION,
    CONF_USER_PREFIX,
    DOMAIN,
    SCOPE,
)

_LOGGER = logging.getLogger(__name__)


class VaillantFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for vaillant_vsmart."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is None:
            return await self._show_config_form()

        errors = {}

        try:
            data = await self._get_config_storage_data(user_input)
        # except CannotConnect:
        #     errors["base"] = "cannot_connect"
        # except InvalidAuth:
        #     errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if errors:
            return await self._show_config_form(user_input, errors)

        await self.async_set_unique_id(user_input[CONF_USERNAME])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input[CONF_USERNAME], data=data)

    async def _show_config_form(
        self, user_input: dict[str, Any] = {}, errors: dict[str, str] = None
    ):
        """Show the configuration form to edit location data."""

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CLIENT_ID, default=user_input.get(CONF_CLIENT_ID)
                    ): str,
                    vol.Required(
                        CONF_CLIENT_SECRET,
                        default=user_input.get(CONF_CLIENT_SECRET),
                    ): str,
                    vol.Required(
                        CONF_USERNAME, default=user_input.get(CONF_USERNAME)
                    ): str,
                    vol.Required(
                        CONF_PASSWORD, default=user_input.get(CONF_PASSWORD)
                    ): str,
                    vol.Required(
                        CONF_USER_PREFIX, default=user_input.get(CONF_USER_PREFIX)
                    ): str,
                    vol.Required(
                        CONF_APP_VERSION, default=user_input.get(CONF_APP_VERSION)
                    ): str,
                }
            ),
            errors=errors,
        )

    async def _get_config_storage_data(
        self, user_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Get config storage data from user input form data."""

        async with auth_client(
            user_input[CONF_CLIENT_ID],
            user_input[CONF_CLIENT_SECRET],
            SCOPE,
        ) as client:
            token = await client.async_get_token(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_USER_PREFIX],
                user_input[CONF_APP_VERSION],
            )

            return {
                CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
                CONF_USER_PREFIX: user_input[CONF_USER_PREFIX],
                CONF_APP_VERSION: user_input[CONF_APP_VERSION],
                CONF_TOKEN: serialize_token(token),
            }
