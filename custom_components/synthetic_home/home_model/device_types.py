"""Data model for home assistant synthetic home."""

from collections.abc import Generator
from dataclasses import dataclass, field
import pathlib
import logging
import yaml

from mashumaro.codecs.yaml import yaml_decode
from mashumaro.exceptions import MissingField


from .exceptions import SyntheticHomeError


_LOGGER = logging.getLogger(__name__)


DEVICE_TYPES_PATH = pathlib.Path(
    "./custom_components/synthetic_home/home_model/device_types/"
)


@dataclass
class EntityEntry:
    """Defines an entity type."""

    key: str
    """The entity description key"""

    supported_attributes: list[str] = field(default_factory=list)
    """Attributes supported by this entity."""

    @property
    def attribute_keys(self) -> Generator[tuple[str, str], None, None]:
        """Returns the of device attribute keys and paired entity attribute key."""
        for attribute in self.supported_attributes:
            device_attribute_key = attribute
            entity_attribute_key = attribute
            if "=" in attribute:
                parts = attribute.split("=")
                entity_attribute_key = parts[0]
                device_attribute_key = parts[1]
            yield device_attribute_key, entity_attribute_key


@dataclass
class DeviceType:
    """Defines of device type."""

    device_type: str
    """The identifier for the device e.g. 'smart-lock'"""

    desc: str
    """The human readable description of the device."""

    entities: dict[str, list[str | EntityEntry]] = field(default_factory=dict)
    """Entity platforms and their entity description keys"""

    supported_attributes: list[str] = field(default_factory=list)
    """Attributes supported by this device, mapped to entity attributes."""

    @property
    def entity_entries(self) -> dict[str, EntityEntry]:
        """Return the parsed entitty attributes for consumption."""
        result = {}
        for key, entity_entries in self.entities.items():
            updated_entries = []
            for entity_entry in entity_entries:
                # Map attributes from the device to this entity if appropriate
                if isinstance(entity_entry, str):
                    updated_entries.append(EntityEntry(key=entity_entry))
                elif isinstance(entity_entry, dict):
                    updated_entries.append(EntityEntry(**entity_entry))
                else:
                    raise SyntheticHomeError(
                        f"Unknown Entity Entry type {entity_entry}"
                    )
            result[key] = updated_entries
        return result


@dataclass
class DeviceTypeRegistry:
    """The registry of all DeviceType objects."""

    device_types: dict[str, DeviceType] = field(default_factory=dict)


def _read_device_types(device_types_path: pathlib.Path) -> Generator[DeviceType]:
    """Read device types from the device type directory."""
    _LOGGER.debug("Loading device type registry from %s", device_types_path.absolute())

    for device_type_file in DEVICE_TYPES_PATH.glob("*.yaml"):
        _LOGGER.debug("Loading %s", device_type_file)
        try:
            with device_type_file.open("r") as f:
                content = f.read()
        except FileNotFoundError:
            raise SyntheticHomeError(
                f"Configuration file '{device_type_file}' does not exist"
            )

        try:
            device_type = yaml_decode(content, DeviceType)
        except MissingField as err:
            raise SyntheticHomeError(f"Unable to decode file {device_type_file}: {err}")
        except yaml.YAMLError as err:
            raise SyntheticHomeError(f"Unable to decode file {device_type_file}: {err}")
        if device_type_file.name != f"{device_type.device_type}.yaml":
            raise SyntheticHomeError(
                f"Device type '{device_type.device_type}' name does not match filename '{device_type_file.name}'"
            )

        yield device_type


def load_device_type_registry() -> DeviceTypeRegistry:
    """Load device types from the yaml configuration files."""
    device_types = {}
    for device_type in _read_device_types(DEVICE_TYPES_PATH):
        if device_type.device_type in device_types:
            raise SyntheticHomeError(
                f"Device registry contains duplicate device type '{device_type.device_type}"
            )
        device_types[device_type.device_type] = device_type
    return DeviceTypeRegistry(device_types=device_types)
