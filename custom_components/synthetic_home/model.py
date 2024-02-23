"""Data model for home assistant synthetic home."""

from enum import StrEnum
from collections.abc import Generator
import hashlib
from typing import Any

from dataclasses import dataclass, field


@dataclass
class DeviceInfo:
    """Device model information."""

    model: str
    manufacturer: str
    firmware: str


class DeviceType(StrEnum):
    """Available device types."""

    CLIMATE_HVAC = "climate_hvac"
    CLIMATE_HEAT_PUMP = "climate_heat_pump"
    # Example of future device types:
    # LIGHT = "light"
    # SMART_TV = "smart_tv"
    # CAMERA = "camera"
    # LAPTOP = "laptop"
    # PHONE = "phone"
    # TABLET = "tablet"


@dataclass
class Device:
    """A synthetic device."""

    name: str
    unique_id: str | None = None  # Future: We can populate the device unique id after processing the home
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


def friendly_entity_name(entity_name: str) -> str:
    """Generate a friendly device name from the device id name."""
    parts = entity_name.split(".")  # Drop the domain
    return parts[1].replace("_", " ").capitalize()


def generate_device_id(device_name: str, area_name: str) -> str:
    """Generate a device id from the hash of device name and area name."""
    hash = hashlib.sha256()
    hash.update(device_name.encode())
    hash.update(area_name.encode())
    return hash.hexdigest()


def generate_entity_unique_id(entity_id: str, device_name: str, area_name: str) -> str:
    """Generate a device id from the hash of device name and area name."""
    hash = hashlib.sha256()
    hash.update(entity_id.encode())
    hash.update(device_name.encode())
    hash.update(area_name.encode())
    return hash.hexdigest()
