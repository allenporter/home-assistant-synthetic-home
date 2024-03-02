"""Data model for home assistant synthetic home."""

from enum import StrEnum
from collections.abc import Generator
import hashlib
from typing import Any

from dataclasses import dataclass, field


@dataclass
class DeviceInfo:
    """Device model information."""

    model: str | None = None
    """The model name of the device e.g. 'Learning Thermostat'."""

    manufacturer: str | None = None
    """The manufacturer of the device e.g. 'Nest'."""

    firmware: str | None = None
    """The firmware version string of the device e.g. '1.0.2'."""


class DeviceType(StrEnum):
    """Available device types.

    A device type a physical device in Home Assistant and may additionally
    be represented by multiple entities. For example, a climate-hvac device
    may be represented by a climage entity and a temperature sensor.

    Device types are defined to represent common configured household devices,
    but may not support every single feature in the smart home. New device types
    may be added as new use cases are needed.
    """

    CLIMATE_HVAC = "climate-hvac"
    """A climate device that supports HVAC Cool and Heat modes."""

    CLIMATE_HEAT_PUMP = "climate-heat-pump"
    """A climate devie that only supports heating."""

    COVER = "cover"
    """A basic cover device that supports open and close such as a door.

    Supports a 'device_class' attribute with values such as 'gate', 'garage', etc.
    """

    COVER_POSITIONABLE = "cover-positionable"
    """A cover that can be set to a specific position like a shade or a curtain.

    Supports a 'device_class' attribute with values such as 'awning',
    'shutter', 'shade', 'window'.
    """

    LIGHT = "light"
    """A generic light that can be turned on/off."""

    LIGHT_DIMMABLE = "light-dimmable"
    """A light that has adjustable brightness.

    Supports a 'brightness' attribute.
    """

    LIGHT_RGBW = "light-rgbw"
    """A light with rgbw color support.

    Supports a 'rgbw-color' attribute.
    """

    SWITCH = "switch"
    """A generic switch."""

    SMART_PLUG = "smart-plug"
    """A smart plug allows remote on/off of electrical devices."""

    SMART_LOCK = "smart-lock"
    """A smart lock device that can be remotely monitored."""

    DOOR_SENSOR = "door-sensor"
    """A device attached to a door that can detect if it is opened or closed."""

    WINDOW_SENSOR = "window-sensor"
    """A device attached to a window that can detect if it is opened or closed."""

    MOTION_SENSOR = "motion-sensor"
    """A device that detects motion of a person or object."""


@dataclass
class Device:
    """A synthetic device."""

    name: str
    unique_id: str | None = (
        None  # Future: We can populate the device unique id after processing the home
    )
    device_type: DeviceType | None = None
    device_info: DeviceInfo | None = None

    # These should be replaced with features
    entities: list[str] | None = None

    # Future we can expand with these instead of entities:
    # features: list[str] | None
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def friendly_name(self) -> str:
        """A friendlier display name for a device."""
        return friendly_device_name(self.name)

    def compute_unique_id(self, area_name: str) -> str:
        """Use defined unique id or generate a unique id based on name and area."""
        if self.unique_id:
            return self.unique_id
        return generate_device_id(self.name, area_name)


@dataclass
class SyntheticHome:
    """Data about a synthetic home."""

    # Devices by area
    device_entities: dict[str, list[Device]]

    @property
    def areas(self) -> list[str]:
        """Area names for the home."""
        return list(self.device_entities.keys())

    @property
    def devices(self) -> list[str]:
        """Device names for the home."""
        return [
            device.name
            for devices in self.device_entities.values()
            for device in devices
        ]

    def devices_and_areas(
        self, device_types: set[DeviceType]
    ) -> Generator[tuple[Device, str]]:
        """Provide all devices and area names for the specified device types."""
        for area_name, device_list in self.device_entities.items():
            for device in device_list:
                if device.device_type in device_types:
                    yield device, area_name

    def entities_by_domain(self, domain: str) -> Generator[tuple[str, str, str]]:
        """Provide all entities with their device and area names."""
        for area_name, device_list in self.device_entities.items():
            for device in device_list:
                for entity_id in device.entities:
                    if not entity_id.startswith(f"{domain}."):
                        continue
                    yield entity_id, device.name, area_name


def friendly_device_name(device_name: str) -> str:
    """Generate a friendly device name from the device id name."""
    return device_name.replace("_", " ").title()


def generate_device_id(device_name: str, area_name: str) -> str:
    """Generate a device id from the hash of device name and area name."""
    hash = hashlib.sha256()
    hash.update(device_name.encode())
    hash.update(area_name.encode())
    return hash.hexdigest()
