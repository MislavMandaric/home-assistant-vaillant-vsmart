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
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.httpx_client import get_async_client
from vaillant_netatmo_api import (
    ApiException,
    AuthClient,
    RequestClientException,
    TokenStore,
)
import voluptuous as vol

from .const import (
    CONF_APP_VERSION,
    CONF_USER_PREFIX,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class VaillantFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for vaillant_vsmart."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        return await self._async_step_all("user", "already_configured", user_input)

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a reauth flow initialized when token used for API requests is invalid."""

        return await self._async_step_all("reauth", "reauth_successful", user_input)

    async def _async_step_all(
        self, step_id: str, abort_reason: str, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Generic flow step that handles both user and reauth steps."""

        if user_input is None:
            user_input = self._init_user_input()
            return self._show_config_form(step_id, user_input)

        errors = {}

        try:
            data = await self._get_config_storage_data(user_input)
        except RequestClientException as ex:
            _LOGGER.exception(ex)
            errors["base"] = "invalid_auth"
        except ApiException as ex:
            _LOGGER.exception(ex)
            errors["base"] = "cannot_connect"
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.exception(ex)
            errors["base"] = "unknown"

        if errors:
            return self._show_config_form(step_id, user_input, errors)

        existing_entry = await self.async_set_unique_id(user_input[CONF_USERNAME])
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason=abort_reason)

        return self.async_create_entry(title=user_input[CONF_USERNAME], data=data)

    def _show_config_form(
        self,
        step_id: str,
        user_input: dict[str, Any],
        errors: dict[str, str] = None,
    ) -> FlowResult:
        """Show the configuration form to edit location data."""

        return self.async_show_form(
            step_id=step_id,
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

    def _init_user_input(self) -> dict[str, Any]:
        """Initializes user input data from configs init data."""

        data = self.init_data

        if data is None:
            return {}

        return {
            CONF_CLIENT_ID: data.get(CONF_CLIENT_ID),
            CONF_CLIENT_SECRET: data.get(CONF_CLIENT_SECRET),
            CONF_USER_PREFIX: data.get(CONF_USER_PREFIX),
            CONF_APP_VERSION: data.get(CONF_APP_VERSION),
        }

    async def _get_config_storage_data(
        self, user_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Get config storage data from user input form data."""

        token_store = TokenStore(
            user_input.get(CONF_CLIENT_ID),
            user_input.get(CONF_CLIENT_SECRET),
            None,
            None,
        )

        client = AuthClient(
            get_async_client(self.hass),
            token_store,
        )

        await client.async_token(
            user_input.get(CONF_USERNAME),
            user_input.get(CONF_PASSWORD),
            user_input.get(CONF_USER_PREFIX),
            user_input.get(CONF_APP_VERSION),
        )

        return {
            CONF_CLIENT_ID: user_input.get(CONF_CLIENT_ID),
            CONF_CLIENT_SECRET: user_input.get(CONF_CLIENT_SECRET),
            CONF_USER_PREFIX: user_input.get(CONF_USER_PREFIX),
            CONF_APP_VERSION: user_input.get(CONF_APP_VERSION),
            CONF_TOKEN: token_store.token.serialize(),
        }
