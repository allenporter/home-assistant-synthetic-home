"""Custom integration to integrate Synthetic Home with Home Assistant.

For more details about this integration, please refer to
https://github.com/allenporter/synthetic-home
"""

import logging
from datetime import timedelta
import pathlib


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import area_registry as ar, device_registry as dr

from .const import DOMAIN, CONF_FILENAME, DATA_RESTORABLE_ATTRIBUTES
from .model import parse_home_config
from .home_model.exceptions import SyntheticHomeError
from .services import async_register_services

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.COVER,
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.SENSOR,
    Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_RESTORABLE_ATTRIBUTES, {})

    config_file = pathlib.Path(hass.config.path(entry.data[CONF_FILENAME]))
    states = hass.data[DOMAIN][DATA_RESTORABLE_ATTRIBUTES].get(entry.entry_id)
    try:
        synthetic_home = parse_home_config(config_file, states)
    except SyntheticHomeError as err:
        raise ConfigEntryError from err

    hass.data[DOMAIN][entry.entry_id] = synthetic_home

    # Create all areas in the home and assign devices to them
    area_registry = ar.async_get(hass)
    device_registry = dr.async_get(hass)
    for device in synthetic_home.devices:
        _LOGGER.debug(
            "Creating device %s with unique_id %s",
            device.friendly_name,
            device.unique_id,
        )
        device_entry = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            name=device.friendly_name,
            identifiers={(DOMAIN, device.unique_id)},
        )
        if device.area_name:
            area_entry = area_registry.async_get_or_create(device.area_name)
            device_registry.async_update_device(device_entry.id, area_id=area_entry.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
