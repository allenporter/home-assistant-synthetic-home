"""Base entity class for Synthetic Home."""

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .model import (
    friendly_device_name,
    Device,
)


class SyntheticDeviceEntity(Entity):
    """synthetic_home light class."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, device: Device, area_name: str, key: str) -> None:
        """Initialize SyntheticHomeLight."""
        unique_id = device.compute_unique_id(area_name)
        self._attr_unique_id = f"{unique_id}-{key}"
        self._attr_device_info = DeviceInfo(
            name=friendly_device_name(device.name),
            suggested_area=area_name,
            identifiers={(DOMAIN, unique_id)},
        )
