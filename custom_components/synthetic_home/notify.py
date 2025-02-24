"""Notify platform for Synthetic Home."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.notify import (
    NotifyEntity,
    DOMAIN as NOTIFY_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES: set[str] = set({})


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up device_tracker platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeNotifyEntity(entity)
        for entity in synthetic_home.entities
        if entity.platform == NOTIFY_DOMAIN
    )


class SyntheticHomeNotifyEntity(SyntheticEntity, NotifyEntity):
    """synthetic_home notify entity class."""

    def __init__(
        self,
        entity: ParsedEntity,
    ) -> None:
        """Initialize SyntheticHomeNotifyEntity."""
        super().__init__(entity)

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message."""
        self._attr_extra_state_attributes = {
            "last_sent_message": {
                "message": message,
                "title": title,
            }
        }
        self.async_write_ha_state()
