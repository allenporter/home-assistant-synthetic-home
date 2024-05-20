"""Library for services related to the synthetic home."""

import logging
import voluptuous as vol


from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import (
    config_validation as cv,
)

from .const import (
    DOMAIN,
    ATTR_AREA_NAME,
    ATTR_DEVICE_NAME,
    ATTR_DEVICE_STATE_KEY,
    ATTR_CONFIG_ENTRY_ID,
    DATA_DEVICE_STATES,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


DATA_SERVICES = "services"


def async_register_services(hass: HomeAssistant) -> None:
    """Set up this integration using UI."""
    if DATA_SERVICES in hass.data:
        return

    async def async_set_synthetic_device_state(call: ServiceCall) -> None:
        """Update the device state."""
        _LOGGER.debug("Evaluation state: %s", call.data)
        entry_id = call.data[ATTR_CONFIG_ENTRY_ID]
        area_name = call.data.get(ATTR_AREA_NAME)
        device_name = call.data[ATTR_DEVICE_NAME]
        device_state_key = call.data[ATTR_DEVICE_STATE_KEY]

        state_data = hass.data[DOMAIN][DATA_DEVICE_STATES].get(entry_id, {})
        state_data[(area_name, device_name)] = device_state_key
        hass.data[DOMAIN][DATA_DEVICE_STATES][entry_id] = state_data

        await hass.config_entries.async_reload(entry_id)

    async def async_clear_synthetic_device_state(call: ServiceCall) -> None:
        """Reset the device state."""
        entry_id = call.data[ATTR_CONFIG_ENTRY_ID]
        hass.data[DOMAIN][DATA_DEVICE_STATES][entry_id] = {}
        await hass.config_entries.async_reload(entry_id)

    hass.services.async_register(
        DOMAIN,
        "set_synthetic_device_state",
        service_func=async_set_synthetic_device_state,
        schema=vol.Schema(
            {
                vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
                vol.Optional(ATTR_AREA_NAME): cv.string,
                vol.Required(ATTR_DEVICE_NAME): cv.string,
                vol.Required(ATTR_DEVICE_STATE_KEY): cv.string,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "clear_synthetic_device_state",
        service_func=async_clear_synthetic_device_state,
        schema=vol.Schema(
            {
                vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
            }
        ),
    )
    hass.data[DATA_SERVICES] = True
