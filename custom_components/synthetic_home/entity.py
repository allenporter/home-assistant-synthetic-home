"""Base entity class for Synthetic Home."""

from homeassistant.helpers.entity import Entity
from homeassistant.components.conversation import DOMAIN as CONVERATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_expose_entity

from .model import ParsedDevice


class SyntheticDeviceEntity(Entity):
    """synthetic_home light class."""

    _attr_has_entity_name = True
    _attr_name: str | None = None

    def __init__(self, device: ParsedDevice, key: str) -> None:
        """Initialize SyntheticHomeLight."""
        unique_id = device.unique_id
        self._attr_unique_id = f"{unique_id}-{key}"
        self._attr_device_info = device.device_info

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        # Expose all synthetic home entities by default
        async_expose_entity(self.hass, CONVERATION_DOMAIN, self.entity_id, True)
