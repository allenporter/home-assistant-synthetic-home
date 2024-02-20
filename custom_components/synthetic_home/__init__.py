"""Custom integration to integrate Synthetic Home with Home Assistant.

For more details about this integration, please refer to
https://github.com/allenporter/synthetic-home
"""

import logging
from datetime import timedelta
import pathlib

from mashumaro.codecs.yaml import yaml_decode

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .const import DOMAIN, CONF_FILENAME
from .model import SyntheticHome

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


def read_config_content(config_file: pathlib.Path) -> str:
    """Read the configuration file contents, exposed for easier patching."""
    try:
        with config_file.open("r") as f:
            return f.read()
    except FileNotFoundError:
        raise ConfigEntryError(f"Configuration file '{config_file}' does not exist")


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    config_file = hass.config.path(entry.data[CONF_FILENAME])
    content = read_config_content(config_file)

    synthetic_home = yaml_decode(content, SyntheticHome)
    hass.data[DOMAIN][entry.entry_id] = synthetic_home

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

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
