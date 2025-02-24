"""Data model for home assistant synthetic home."""

from dataclasses import dataclass, field, asdict
import pathlib
import logging
import importlib
from typing import Any, cast
from functools import cache

from synthetic_home import inventory

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


@dataclass
class ParsedDevice:
    """Data about a device as used in the integration."""

    unique_id: str
    name: str
    area_name: str | None


def parse_device_info(
    inv_device: inventory.Device, area: inventory.Area | None
) -> DeviceInfo:
    """Convert inventory device into into a home assistant device info."""
    device_info: DeviceInfo = DeviceInfo(
        name=inv_device.name,
        identifiers={(DOMAIN, inv_device.id)},
        **(asdict(inv_device.info) if inv_device.info else {}),  # type: ignore[typeddict-item]
    )
    if area:
        device_info["suggested_area"] = area.name
    return device_info


@dataclass
class ParsedEntity:
    """Data about an entity used in the integration."""

    platform: str
    entity_id: str
    name: str
    device_info: DeviceInfo | None
    area_name: str | None
    state: Any
    attributes: dict[str, str | list[str]]


def parse_entity(
    inv_entity: inventory.Entity,
    device_info: DeviceInfo | None,
    area_name: str | None = None,
) -> ParsedEntity:
    """Prepare an inventory entity for the synthetic home assistant model."""
    if inv_entity.id is None:
        raise ValueError("Inventory entity was missing an id")
    if inv_entity.name is None:
        raise ValueError(f"Inventory entity '{inv_entity.id}' was missing a name")
    (platform, entity_slug) = inv_entity.id.split(".", maxsplit=1)
    if platform == "fan":
        _LOGGER.debug("FAN inv_entity = %s", inv_entity)
    return ParsedEntity(
        platform=platform,
        entity_id=inv_entity.id,
        name=inv_entity.name,
        area_name=area_name,
        state=inv_entity.state,
        attributes=parse_attributes(inv_entity.attributes or {}),
        device_info=device_info,
    )


@dataclass
class ParsedArea:
    """Data about an area."""

    name: str
    floor_name: str | None = None


@dataclass
class ParsedHome:
    """Data about the synthetic home as used in the integration."""

    floors: list[str] = field(default_factory=list)
    areas: list[ParsedArea] = field(default_factory=list)
    devices: list[ParsedDevice] = field(default_factory=list)
    parsed_inventory: inventory.Inventory | None = None
    entities: list[ParsedEntity] = field(default_factory=list)


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
        domain, enum, feature = supported_feature.split(".", maxsplit=2)
    except ValueError as exc:
        raise ValueError(
            f"Invalid supported feature '{supported_feature}', expected "
            "<domain>.<enum>.<member>"
        ) from exc

    try:
        return _entity_feature_flag(domain, enum, feature)
    except (ModuleNotFoundError, AttributeError) as exc:
        raise ValueError(f"Unknown supported feature '{supported_feature}'") from exc


def parse_attributes(
    values: dict[str, str | int | float | bool | list[str]],
) -> dict[str, Any]:
    """Parse special string attributes as constants."""
    result = {}
    for key, value in values.items():
        new_value: str | int | None = None
        if key == "device_class" or key == "state_class":
            if isinstance(value, str) and "." in value:
                new_value = _validate_supported_feature(str(value))
        if key == "supported_features":
            if isinstance(value, int):
                # Do nothing
                new_value = value
            elif not isinstance(value, list):
                raise ValueError(
                    f"Expected type 'list' for 'supported_features', got: '{value}'"
                )
            else:
                flag = 0
                for subvalue in value:
                    flag |= cast(int, _validate_supported_feature(subvalue).value)
                new_value = flag
        result[key] = new_value or value
    return result


def parse_home_config(config_file: pathlib.Path) -> ParsedHome:
    """Load synthetic home configuration from disk."""

    inv = inventory.load_inventory(config_file)

    inv_area_dict = inv.area_dict()
    inv_device_dict = inv.device_dict()

    parsed_devices = []
    for inv_device in inv_device_dict.values():
        if inv_device.id is None:
            raise ValueError(f"Expected inventory device to have an id: {inv_device}")
        if inv_device.area:
            device_area_name = inv_area_dict[inv_device.area].name
        else:
            device_area_name = None
        parsed_device = ParsedDevice(
            unique_id=inv_device.id,
            name=inv_device.name,
            area_name=device_area_name,
        )
        parsed_devices.append(parsed_device)

    parsed_entities = []
    for inv_entity in inv.entities:
        device_info: DeviceInfo | None = None
        if inv_entity.device is not None:
            inv_device = inv_device_dict[inv_entity.device]
            device_info = parse_device_info(
                inv_device, inv_area_dict.get(inv_device.area or "")
            )
        entity_area_name: str | None = None
        if inv_entity.area is not None:
            entity_area_name = inv_area_dict[inv_entity.area].name
        parsed_entity = parse_entity(inv_entity, device_info, entity_area_name)
        parsed_entities.append(parsed_entity)

    return ParsedHome(
        floors=list(inv.floors),
        areas=[ParsedArea(area.name, area.floor) for area in inv.areas],
        devices=parsed_devices,
        parsed_inventory=inv,
        entities=parsed_entities,
    )


def filter_attributes(
    entity: ParsedEntity,
    supported: set[str],
) -> dict[str, Any]:
    """Filter attributes to just the supported list."""
    attributes = entity.attributes
    supported_attributes = {k: v for k, v in attributes.items() if k in supported}
    unsupported_attributes = {k: v for k, v in attributes.items() if k not in supported}
    if unsupported_attributes:
        _LOGGER.info(
            "Entity %s specified unsupported attributes %s (supported=%s)",
            entity.entity_id,
            list(unsupported_attributes.keys()),
            supported,
        )
    return supported_attributes
