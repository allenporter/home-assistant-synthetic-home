"""Adds config flow for Synthetic Home."""
from homeassistant import config_entries

from .const import DOMAIN


class SyntheticHomeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for synthetic_home."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return self.async_create_entry(title="Synthetic Home", data={})
