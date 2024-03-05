"""Data model for home assistant synthetic home."""

from collections.abc import Generator
from dataclasses import dataclass, field, asdict
import hashlib
import pathlib
import logging
from typing import Any
import yaml

from mashumaro.codecs.yaml import yaml_decode
from mashumaro.exceptions import MissingField

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .exceptions import SyntheticHomeError

_LOGGER = logging.getLogger(__name__)


DEVICE_TYPES_PATH = pathlib.Path("./custom_components/synthetic_home/device_types/")


@dataclass
class DeviceType:
    """Defines of device type."""

    device_type: str
    """The identifier for the device e.g. 'smart-lock'"""

    desc: str
    """The human readable description of the device."""

    entities: dict[str, list[str]]
    """Entity platforms and their entity description keys"""


@dataclass
class DeviceTypeRegistry:
    """The registry of all DeviceType objects."""

    device_types: dict[str, DeviceType] = field(default_factory=dict)


@dataclass
class SyntheticDeviceInfo:
    """Device model information."""

    model: str | None = None
    """The model name of the device e.g. 'Learning Thermostat'."""

    manufacturer: str | None = None
    """The manufacturer of the device e.g. 'Nest'."""

    sw_version: str | None = None
    """The firmware version string of the device e.g. '1.0.2'."""


@dataclass
class Device:
    """A synthetic device."""

    name: str
    device_type: str | None = None
    device_info: SyntheticDeviceInfo | None = None

    # Future we can expand with these instead of entities:
    # features: list[str] | None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class SyntheticHome:
    """Data about a synthetic home."""

    # Devices by area
    device_entities: dict[str, list[Device]]

    # Device types supported by the home.
    device_type_registry: DeviceTypeRegistry | None = None


@dataclass
class ParsedEntity:
    """Data about an entity used in the integration."""

    platform: str
    entity_key: str
    attributes: str


@dataclass
class ParsedDevice:
    """Data about a device as used in the integration."""

    unique_id: str
    device: Device
    area_name: str
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
            **(asdict(self.device.device_info) if self.device.device_info else {}),
        )


@dataclass
class ParsedHome:
    """Data about the synthetic home as used in the integration."""

    areas: list[str] = field(default_factory=list)
    devices: list[ParsedDevice] = field(default_factory=list)


def generate_device_id(device_name: str, area_name: str) -> str:
    """Generate a device id from the hash of device name and area name."""
    hash = hashlib.sha256()
    hash.update(device_name.encode())
    hash.update(area_name.encode())
    return hash.hexdigest()


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


def read_config_content(config_file: pathlib.Path) -> str:
    """Read the configuration file contents, exposed for easier patching."""
    try:
        with config_file.open("r") as f:
            return f.read()
    except FileNotFoundError:
        raise SyntheticHomeError(f"Configuration file '{config_file}' does not exist")


def load_synthetic_home(config_file: pathlib.Path) -> ParsedHome:
    """Load synthetic home configuration from disk."""
    content = read_config_content(config_file)

    synthetic_home = yaml_decode(content, SyntheticHome)

    # Merge the default registry with any new devices specified in the home config
    registry = load_device_type_registry()
    if synthetic_home.device_type_registry:
        registry.device_types.update(synthetic_home.device_type_registry.device_types)
    synthetic_home.device_type_registry = registry

    _LOGGER.debug(
        "Loaded %s device types", len(synthetic_home.device_type_registry.device_types)
    )

    parsed_devices: list[ParsedDevice] = []
    for area_name, devices_list in synthetic_home.device_entities.items():
        for device in devices_list:
            if not (device_type := registry.device_types.get(device.device_type)):
                raise SyntheticHomeError(
                    f"Device {device} has device_type {device.device_type} not found in registry"
                )

            parsed_entities: list[ParsedEntity] = []
            for platform, entity_keys in device_type.entities.items():
                for entity_key in entity_keys:
                    parsed_entities.append(
                        ParsedEntity(
                            platform=platform,
                            entity_key=entity_key,
                            # TODO: This is incorrect and needs to be fixed
                            attributes=device.attributes,
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
        areas=synthetic_home.device_entities.keys(),
        devices=parsed_devices,
    )
