"""Data model for home assistant synthetic home."""

from dataclasses import dataclass, field, asdict
import hashlib
import pathlib
import logging
from typing import Any

from synthetic_home.synthetic_home import (
    Device,
    load_synthetic_home,
)
from synthetic_home.device_types import (
    load_device_type_registry,
    DeviceType,
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
        return DeviceInfo(
            name=self.friendly_name,
            suggested_area=self.area_name,
            identifiers={(DOMAIN, self.unique_id)},
            **(asdict(self.device.device_info) if self.device.device_info else {}),  # type: ignore[typeddict-item]
        )


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


def _restore_attributes(
    device_type: DeviceType,
    device: Device,
) -> None:
    """Apply an evaluation state update to the specified device."""
    if device.restorable_attribute_keys:
        # Clear any existing state values and overwrite from the evaluation state
        for state_value in device_type.supported_state_attributes:
            if state_value in device.attributes:
                del device.attributes[state_value]

    # Find the evaluation states from the device registry
    for restore_attribute_key in device.restorable_attribute_keys:
        if not (
            restorable_attributes := device_type.get_restorable_attributes_by_key(
                restore_attribute_key
            )
        ):
            raise SyntheticHomeError(
                f"Device type '{device_type.device_type}' does not support restorable attribute key '{restore_attribute_key}'. Options are: {device_type.all_restore_attribute_keys}"
            )
        _LOGGER.debug(
            "Applying attribute overrides: %s", restorable_attributes.attributes
        )
        device.attributes.update(restorable_attributes.attributes)


def parse_home_config(
    config_file: pathlib.Path,
    restorable_attributes: dict[tuple[str | None, str], str] | None,
) -> ParsedHome:
    """Load synthetic home configuration from disk."""
    synthetic_home = load_synthetic_home(config_file)

    # Merge the default registry with any new devices specified in the home config
    registry = load_device_type_registry()
    if synthetic_home.device_type_registry:
        registry.device_types.update(synthetic_home.device_type_registry.device_types)
    synthetic_home.device_type_registry = registry

    if restorable_attributes:
        for (
            area_name,
            device_name,
        ), restorable_attribute_key in restorable_attributes.items():
            found_device = synthetic_home.find_devices_by_name(area_name, device_name)
            assert found_device
            found_device.restorable_attribute_keys.append(restorable_attribute_key)

    _LOGGER.debug(
        "Loaded %s device types", len(synthetic_home.device_type_registry.device_types)
    )
    if not synthetic_home.device_type_registry.device_types:
        raise SyntheticHomeError("No device types found in the synthetic home")
    synthetic_home.validate()

    parsed_devices: list[ParsedDevice] = []
    pairs: list[tuple[str | None, list[Device]]] = [*synthetic_home.devices.items()]
    if synthetic_home.services:
        pairs.append((None, synthetic_home.services))
    for area_name, devices_list in pairs:
        for device in devices_list:
            assert device.device_type
            if (device_type := registry.device_types.get(device.device_type)) is None:
                raise SyntheticHomeError(
                    f"Device '{device.name}' device_type '{device.device_type}' not found in registry"
                )

            # Populate pre-canned restorable attributes
            _restore_attributes(device_type, device)

            parsed_entities: list[ParsedEntity] = []
            for platform, entity_entries in device_type.entity_entries.items():
                for entity_entry in entity_entries:
                    attributes = {
                        entity_attribute_key: device.attributes[device_attribute_key]
                        for device_attribute_key, entity_attribute_key in entity_entry.attribute_keys
                        if device_attribute_key in device.attributes
                    }
                    parsed_entities.append(
                        ParsedEntity(
                            platform=platform,
                            entity_key=entity_entry.key,
                            attributes=attributes,
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
