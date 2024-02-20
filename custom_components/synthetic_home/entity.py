"""Base entity class for Synthetic Home."""

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .model import generate_entity_unique_id, friendly_device_name, generate_device_id


class SyntheticEntity(Entity):
    """synthetic_home light class."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entity_id: str, device_name: str, area_name: str) -> None:
        """Initialize SyntheticHomeLight."""
        self._attr_unique_id = generate_entity_unique_id(
            entity_id, device_name, area_name
        )
        self.entity_id = entity_id
        device_id = generate_device_id(device_name, area_name)
        self._attr_device_info = DeviceInfo(
            name=friendly_device_name(device_name),
            suggested_area=area_name,
            identifiers={(DOMAIN, device_id)},
        )
