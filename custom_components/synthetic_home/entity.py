"""Base entity class for Synthetic Home."""

from homeassistant.helpers.entity import Entity
from homeassistant.components.conversation import DOMAIN as CONVERATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_expose_entity

from .model import ParsedEntity


class SyntheticEntity(Entity):
    """synthetic_home entity class."""

    _attr_has_entity_name = False

    def __init__(self, entity: ParsedEntity) -> None:
        """Initialize InventoryEntity."""
        self._attr_unique_id = entity.entity_id
        self.entity_id = entity.entity_id
        self._attr_name = entity.name
        self._attr_device_info = entity.device_info

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        # Expose all synthetic home entities by default
        async_expose_entity(self.hass, CONVERATION_DOMAIN, self.entity_id, True)
