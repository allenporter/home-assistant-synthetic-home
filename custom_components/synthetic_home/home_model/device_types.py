"""Data model for home assistant synthetic home."""

from collections.abc import Generator
from dataclasses import dataclass, field
import pathlib
import logging
import yaml
from typing import Any

from mashumaro.codecs.yaml import yaml_decode
from mashumaro.exceptions import MissingField


from .exceptions import SyntheticHomeError


_LOGGER = logging.getLogger(__name__)


DEVICE_TYPES_PATH = pathlib.Path(
    "./custom_components/synthetic_home/home_model/device_types/"
)


@dataclass
class EntityEntry:
    """Defines an entity type.

    An entity is the lowest level object that maps to a device. The supported
    attributes are used to map device level attributes to entity level attributes
    used in the platforms when creating Home Assistant entities.
    """

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
class RestorableAttributes:
    """Represents a device state that can be used to save a pre-canned restore state.

    This is used as a grouping of state values representing the "interesting"
    states of the device that can be enumerated during evaluation. For example,
    instead of explicitly specifying specific temperature values, a restorable
    state could implement "warm" and "cool".
    """

    key: str
    """An identifier for this set of attributes used for labeling"""

    attributes: dict[str, Any] = field(default_factory=dict)
    """The key/values that map to the device `supported_state_attributes` for this evaluation state."""


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

    supported_state_attributes: list[str] = field(default_factory=list)
    """State values that can be set on this device, mapped to entity attributes."""

    restorable_attributes: list[RestorableAttributes] = field(default_factory=list)
    """A series of different attribute values that are most interesting to use during evaluation."""

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

    @property
    def all_restore_attribute_keys(self) -> list[str]:
        """Return all restorable attribute keys supported."""
        return [state.key for state in self.restorable_attributes]

    def get_restorable_attributes_by_key(
        self, restore_attribute_key: str
    ) -> RestorableAttributes | None:
        """Get the set of restorable attributes by the specified key."""
        for restore_attribute in self.restorable_attributes:
            if restore_attribute.key == restore_attribute_key:
                return restore_attribute
        return None


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


def load_restorable_attributes(device_type: str) -> list[str]:
    """Enumerate the evaluation states for the specified device type."""
    device_type_registry = load_device_type_registry()
    camera_device_type = device_type_registry.device_types[device_type]
    return [eval_state.key for eval_state in camera_device_type.restorable_attributes]
