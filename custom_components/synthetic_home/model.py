"""Data model for home assistant synthetic home."""

from dataclasses import dataclass, field, asdict
import hashlib
import pathlib
import logging
import importlib
from typing import Any, cast
from functools import cache

from synthetic_home.synthetic_home import (
    Device,
    load_synthetic_home,
)
from synthetic_home.device_types import (
    load_device_type_registry,
)
from synthetic_home.exceptions import SyntheticHomeError

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


@dataclass
class ParsedEntity:
    """Data about an entity used in the integration."""

    platform: str
    entity_key: str
    attributes: dict[str, Any]


@dataclass
class ParsedDevice:
    """Data about a device as used in the integration."""

    unique_id: str
    device: Device
    area_name: str | None
    entities: list[ParsedEntity]

    @property
    def friendly_name(self) -> str:
        """A friendlier display name for a device."""
        return self.device.name.replace("_", " ").title()

    @property
    def device_info(self) -> DeviceInfo:
        """Home Assistant device info for this device."""
        device_info = DeviceInfo(
            name=self.friendly_name,
            suggested_area=self.area_name,
            identifiers={(DOMAIN, self.unique_id)},
            **(asdict(self.device.device_info) if self.device.device_info else {}),  # type: ignore[typeddict-item]
        )
        return device_info  # type: ignore[no-any-return]


@dataclass
class ParsedHome:
    """Data about the synthetic home as used in the integration."""

    areas: list[str] = field(default_factory=list)
    devices: list[ParsedDevice] = field(default_factory=list)


def generate_device_id(device_name: str, area_name: str | None) -> str:
    """Generate a device id from the hash of device name and area name."""
    hash = hashlib.sha256()
    hash.update(device_name.encode())
    if area_name:
        hash.update(area_name.encode())
    return hash.hexdigest()


@cache
def _entity_feature_flag(domain: str, enum_name: str, feature_value: str) -> Any:
    """Return a cached lookup of an entity feature enum.

    This will import a module from disk and is run from an executor when
    loading the services schema files.
    """
    module = importlib.import_module(f"homeassistant.components.{domain}")
    enum = getattr(module, enum_name)
    feature = getattr(enum, feature_value)
    return feature


def _validate_supported_feature(supported_feature: str) -> Any:
    """Validate a supported feature and resolve an enum string to its value."""

    try:
        domain, enum, feature = supported_feature.split(".", 2)
    except ValueError as exc:
        raise ValueError(
            f"Invalid supported feature '{supported_feature}', expected "
            "<domain>.<enum>.<member>"
        ) from exc

    try:
        return _entity_feature_flag(domain, enum, feature)
    except (ModuleNotFoundError, AttributeError) as exc:
        raise ValueError(f"Unknown supported feature '{supported_feature}'") from exc


def parse_attributes(values: dict[str, str | list[str]]) -> dict[str, Any]:
    """Parse special string attributes as constants."""
    result = {}
    for key, value in values.items():
        new_value: str | int | None = None
        if key == "device_class" or key == "state_class":
            new_value = _validate_supported_feature(str(value))
        if key == "supported_features":
            if not isinstance(value, list):
                raise ValueError(
                    f"Expected type 'list' for 'supported_features', got: '{value}'"
                )
            flag = 0
            for subvalue in value:
                flag |= cast(int, _validate_supported_feature(subvalue).value)
            new_value = flag
        result[key] = new_value or value
    return result


def parse_home_config(
    config_file: pathlib.Path,
    device_states: dict[tuple[str | None, str], str] | None,
) -> ParsedHome:
    """Load synthetic home configuration from disk."""
    synthetic_home = load_synthetic_home(config_file)

    # Merge the default registry with any new devices specified in the home config
    registry = load_device_type_registry()
    if synthetic_home.device_type_registry:
        registry.device_types.update(synthetic_home.device_type_registry.device_types)
    synthetic_home.device_type_registry = registry

    if device_states:
        for (
            area_name,
            device_name,
        ), device_state_key in device_states.items():
            found_device = synthetic_home.find_devices_by_name(area_name, device_name)
            assert found_device
            _LOGGER.debug(
                "Assigning device state for '%s': %s", device_name, device_state_key
            )
            found_device.device_state = device_state_key

    _LOGGER.debug(
        "Loaded %s device types", len(synthetic_home.device_type_registry.device_types)
    )
    if not synthetic_home.device_type_registry.device_types:
        raise SyntheticHomeError("No device types found in the synthetic home")
    synthetic_home = synthetic_home.build()

    parsed_devices: list[ParsedDevice] = []
    pairs: list[tuple[str | None, list[Device]]] = [*synthetic_home.devices.items()]
    if synthetic_home.services:
        pairs.append((None, synthetic_home.services))
    for area_name, devices_list in pairs:
        for device in devices_list:
            parsed_entities: list[ParsedEntity] = []
            for platform, entity_entries in device.entity_entries.items():
                for entity_entry in entity_entries:
                    parsed_entities.append(
                        ParsedEntity(
                            platform=platform,
                            entity_key=entity_entry.key,
                            attributes=parse_attributes(entity_entry.attributes),
                        )
                    )

            parsed_devices.append(
                ParsedDevice(
                    unique_id=generate_device_id(device.name, area_name),
                    device=device,
                    area_name=area_name,
                    entities=parsed_entities,
                )
            )

    return ParsedHome(
        areas=list(synthetic_home.devices.keys()),
        devices=parsed_devices,
    )
