"""Base entity class for Synthetic Home."""

import logging

from homeassistant.helpers import entity_registry as er, area_registry as ar
from homeassistant.helpers.entity import Entity
from homeassistant.components.conversation import DOMAIN as CONVERATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_expose_entity

from .model import ParsedEntity

_LOGGER = logging.getLogger(__name__)


class SyntheticEntity(Entity):
    """synthetic_home entity class."""

    _attr_has_entity_name = False

    def __init__(self, entity: ParsedEntity) -> None:
        """Initialize InventoryEntity."""
        self._attr_unique_id = entity.entity_id
        self.entity_id = entity.entity_id
        self._attr_name = entity.name
        self._attr_device_info = entity.device_info
        self._entity = entity

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        # Expose all synthetic home entities by default
        async_expose_entity(self.hass, CONVERATION_DOMAIN, self.entity_id, True)
        # Add areas for entities that specify an area without a device
        if self._attr_device_info is None and self._entity.area_name:
            area_registry = ar.async_get(self.hass)
            area_entry = area_registry.async_get_or_create(self._entity.area_name)
            entity_registry = er.async_get(self.hass)
            entity_registry.async_update_entity(self.entity_id, area_id=area_entry.id)
