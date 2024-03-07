"""Base entity class for Synthetic Home."""

from homeassistant.helpers.entity import Entity

from .model import ParsedDevice


class SyntheticDeviceEntity(Entity):
    """synthetic_home light class."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, device: ParsedDevice, key: str) -> None:
        """Initialize SyntheticHomeLight."""
        unique_id = device.unique_id
        self._attr_unique_id = f"{unique_id}-{key}"
        self._attr_device_info = device.device_info
