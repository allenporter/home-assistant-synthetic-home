"""Data model for home assistant synthetic home."""

from collections.abc import Generator
import hashlib

from dataclasses import dataclass


@dataclass
class Device:
    """A synthetic device."""

    name: str
    entities: list[str]

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
