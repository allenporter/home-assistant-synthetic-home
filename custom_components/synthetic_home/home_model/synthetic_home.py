"""Data model for home assistant synthetic home."""

import itertools
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
    """A human readable name for the device."""

    device_type: str | None = None
    """The type of the device in the device registry that determines how it maps to entities."""

    device_info: SyntheticDeviceInfo | None = None
    """Device make and model information."""

    attributes: dict[str, Any] = field(default_factory=dict)
    """Attributes that determine how the entities are configured or their state"""

    restorable_attribute_keys: list[str] = field(default_factory=list)
    """A list of pre-canned RestorableStateAttributes specified by the key.

    These are used for restoring a device into a specific state supported by the
    device type. This is used to use a label rather than specifying low level
    entity details. This is an alternative to specifying low level attributes above.

    Restorable attributes overwrite normal attributes since they can be reloaded
    at runtime.
    """


@dataclass
class SyntheticHome:
    """Data about a synthetic home."""

    # Devices by area
    devices: dict[str, list[Device]] = field(default_factory=dict)

    # Services for the home not for a specific area
    services: list[Device] = field(default_factory=list)

    # Device types supported by the home.
    device_type_registry: DeviceTypeRegistry | None = None

    def validate(self) -> None:
        """Validate a SyntheticHome configuration."""
        for devices_list in self.devices.values():
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
                    if (
                        attribute not in device_type.supported_attributes
                        and attribute not in device_type.supported_state_attributes
                    ):
                        raise SyntheticHomeError(
                            f"Device {device.name} has attribute '{attribute}' not supported by device type {device_type}"
                        )

    def find_devices_by_name(
        self, area_name: str | None, device_name: str
    ) -> Device | None:
        """Find devices by optional area and device name."""
        devices = list(
            itertools.chain.from_iterable(
                [
                    area_devices
                    for area, area_devices in self.devices.items()
                    if area_name is None or area == area_name
                ]
            )
        )
        if area_name is not None and not devices:
            raise SyntheticHomeError(f"Area name '{area_name}' matched no devices")
        found_devices = [device for device in devices if device.name == device_name]
        if len(found_devices) == 0:
            raise SyntheticHomeError(f"Device name '{device_name}' matched no devices")
        if len(found_devices) > 1:
            raise SyntheticHomeError(
                f"Device name '{device_name}' matched multiple devices, must specify an area"
            )
        return found_devices[0]


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
    try:
        return yaml_decode(content, SyntheticHome)
    except ValueError as err:
        raise SyntheticHomeError(f"Could not parse config file '{config_file}': {err}")
