"""Test Synthetic Home initialization."""

import slugify
import pathlib
import enum
from typing import Any

import pytest
from syrupy import SnapshotAssertion
from synthetic_home import inventory, common

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    entity_registry as er,
    device_registry as dr,
    area_registry as ar,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.synthetic_home import PLATFORMS

from .conftest import HOMES

ORIG_PLATFORMS = [*PLATFORMS]
CONFIG_GLOB = list(pathlib.Path(HOMES).glob("*.yaml"))


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return ORIG_PLATFORMS


@pytest.mark.parametrize(
    "config_yaml_fixture",
    CONFIG_GLOB,
    ids=[str(filename) for filename in CONFIG_GLOB],
)
async def test_inventory(
    hass: HomeAssistant,
    setup_integration: None,
    config_entry: MockConfigEntry,
    area_registry: ar.AreaRegistry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test examining the created areas, devices, floors, etc."""

    area_data = [
        inventory.Area(
            name=area_entry.name,
            id=area_entry.id,
            floor=area_entry.floor_id,
        )
        for area_entry in area_registry.async_list_areas()
    ]

    device_data = []
    for device_entry in dr.async_entries_for_config_entry(
        device_registry, config_entry.entry_id
    ):
        device = inventory.Device(
            name=device_entry.name,
            area=device_entry.area_id,
        )
        if device_entry.model or device_entry.manufacturer or device_entry.sw_version:
            info = common.DeviceInfo()
            if device_entry.model:
                info.model = device_entry.model
            if device_entry.manufacturer:
                info.model = device_entry.manufacturer
            if device_entry.sw_version:
                info.model = device_entry.sw_version
            device.info = info
        device_data.append(device)

    def attribute_value(v: Any) -> Any:
        if isinstance(v, enum.IntFlag):
            # Friendly name like todo.TodoListEntityFeature.CREATE_TODO_ITEM
            flag_type = type(v)
            module_parts = flag_type.__module__.split(".")
            if module_parts[-1] == "const":
                module_parts.pop()
            return [
                f"{module_parts[-1]}.{flag_type.__name__}.{flag.name}"
                for flag in type(v)
                if v & flag == flag
            ]
        if isinstance(v, bool) or isinstance(v, float) or isinstance(v, list):
            return v
        return str(v)

    entity_data = []
    for entity_entry in er.async_entries_for_config_entry(
        entity_registry, config_entry.entry_id
    ):
        state = hass.states.get(entity_entry.entity_id)
        device_entry = device_registry.async_get(entity_entry.device_id)
        device_id = slugify.slugify(device_entry.name, separator="_")
        entity_data.append(
            inventory.Entity(
                name=state.attributes.get("friendly_name"),
                id=entity_entry.entity_id,
                area=device_entry.area_id,
                device=device_id,
                state=state.state,
                attributes={
                    k: attribute_value(v)
                    for k, v in state.attributes.items()
                    if v is not None and k not in ("friendly_name")
                },
            )
        )

    inv = inventory.Inventory()
    inv.areas = area_data
    inv.devices = device_data
    inv.entities = entity_data
    assert inv.yaml() == snapshot
