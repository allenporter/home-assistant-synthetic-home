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
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    floor_registry as fr,
)

from .const import DOMAIN, CONF_FILENAME
from .model import parse_home_config

from synthetic_home.exceptions import SyntheticHomeError

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CALENDAR,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.FAN,
    Platform.LIGHT,
    Platform.LOCK,
    Platform.MEDIA_PLAYER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TODO,
    Platform.VACUUM,
    Platform.VALVE,
    Platform.WEATHER,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    filename = entry.data[CONF_FILENAME]
    if filename.startswith("/"):
        config_file = pathlib.Path(filename)
    else:
        config_file = pathlib.Path(hass.config.path(filename))
    try:
        synthetic_home = parse_home_config(config_file)
    except SyntheticHomeError as err:
        raise ConfigEntryError from err

    hass.data[DOMAIN][entry.entry_id] = synthetic_home

    # Create all floors
    floor_registry = fr.async_get(hass)
    floor_ids = {}
    for floor_name in synthetic_home.floors:
        floor_entry = floor_registry.async_create(floor_name)
        floor_ids[floor_name] = floor_entry.floor_id
        _LOGGER.debug("Created floor %s (id=%s)", floor_name, floor_entry.floor_id)

    # Create all areas in the home and assign devices to them
    area_registry = ar.async_get(hass)
    area_ids = {}
    for area in synthetic_home.areas:
        area_entry = area_registry.async_get_or_create(area.name)
        if area.floor_name and (floor_id := floor_ids.get(area.floor_name)) is not None:
            area_registry.async_update(area_entry.id, floor_id=floor_id)
        area_ids[area.name] = area_entry.id
        _LOGGER.debug("Created area %s (id=%s)", area.name, area_entry.id)

    device_registry = dr.async_get(hass)
    for device in synthetic_home.devices:
        _LOGGER.debug(
            "Creating device %s with unique_id %s",
            device.name,
            device.unique_id,
        )
        device_entry = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            name=device.name,
            identifiers={(DOMAIN, device.unique_id)},
        )
        if device.area_name:
            area_id = area_ids[device.area_name]
            device_registry.async_update_device(device_entry.id, area_id=area_id)

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
    await hass.config_entries.async_reload(entry.entry_id)
