"""Binary sensor platform for Synthetic Home."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from .const import DOMAIN
from .model import DeviceType, Device
from .entity import SyntheticDeviceEntity

SUPPORTED_DEVICE_TYPES = [DeviceType.BINARY_SENSOR]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up binary_sensor platform."""

    synthetic_home = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        SyntheticHomeBinarySensor(device, area_name, **device.attributes)
        for device, area_name in synthetic_home.devices_and_areas(
            SUPPORTED_DEVICE_TYPES
        )
    )


class SyntheticHomeBinarySensor(SyntheticDeviceEntity, BinarySensorEntity):
    """synthetic_home binary_sensor class."""

    def __init__(
        self,
        device: Device,
        area_name: str,
        *,
        state: bool | None = None,
        device_class: BinarySensorDeviceClass | None = None
    ) -> None:
        """Initialize SyntheticHomeSensor."""
        super().__init__(device, area_name, "binary-sensor")
        self._state = state if state is not None else False
        self._attr_device_class = device_class

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._state
