"""Adds config flow for Synthetic Home."""

import pathlib
from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, CONF_FILENAME

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_FILENAME): str,
    }
)


def read_config(config_file: pathlib.Path) -> str:
    """Read config filename from disk."""
    with config_file.open("r") as f:
        return f.read()


class SyntheticHomeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for synthetic_home."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            config_file = pathlib.Path(self.hass.config.path(user_input[CONF_FILENAME]))
            try:
                read_config(config_file)
            except FileNotFoundError:
                errors[CONF_FILENAME] = "does_not_exist"
            else:
                return self.async_create_entry(  # type: ignore[no-any-return]
                    title=user_input[CONF_FILENAME], data=user_input
                )

        return self.async_show_form(  # type: ignore[no-any-return]
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
