"""Data model for home assistant synthetic home."""

from dataclasses import dataclass, field
import pathlib
import logging
from typing import Any

from mashumaro.codecs.yaml import yaml_decode

from .exceptions import SyntheticHomeError
from .device_types import DeviceTypeRegistry

_LOGGER = logging.getLogger(__name__)


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
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class SyntheticHome:
    """Data about a synthetic home."""

    # Devices by area
    device_entities: dict[str, list[Device]]

    # Device types supported by the home.
    device_type_registry: DeviceTypeRegistry | None = None

    def validate(self) -> None:
        """Validate a SyntheticHome configuration."""
        for devices_list in self.device_entities.values():
            for device in devices_list:
                if not (
                    device_type := self.device_type_registry.device_types.get(
                        device.device_type
                    )
                ):
                    raise SyntheticHomeError(
                        f"Device {device} has device_type {device.device_type} not found in registry"
                    )
                for attribute in device.attributes:
                    if attribute not in device_type.supported_attributes:
                        raise SyntheticHomeError(
                            f"Device {device.name} has attribute '{attribute}' not supported by device type {device_type}"
                        )


def read_config_content(config_file: pathlib.Path) -> str:
    """Create configuration file content, exposed for patching."""
    with config_file.open("r") as f:
        return f.read()


def load_synthetic_home(config_file: pathlib.Path) -> SyntheticHome:
    """Load synthetic home configuration from disk."""
    try:
        content = read_config_content(config_file)
    except FileNotFoundError:
        raise SyntheticHomeError(f"Configuration file '{config_file}' does not exist")

    return yaml_decode(content, SyntheticHome)
