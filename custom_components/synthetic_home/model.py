"""Data model for home assistant synthetic home."""

from collections.abc import Generator

from dataclasses import dataclass


@dataclass
class Device:
    """A synthetic device."""

    name: str
    entities: list[str]


@dataclass
class SyntheticHome:
    """Data about a synthetic home."""

    # Devices by area
    device_entities: dict[str, list[Device]]

    def entities_by_domain(self, domain: str) -> Generator[tuple[str, str, str]]:
        for area_name, device_list in self.device_entities.items():
            for device in device_list:
                for entity_id in device.entities:
                    if not entity_id.startswith(f"{domain}."):
                        continue
                    yield entity_id, device.name, area_name
