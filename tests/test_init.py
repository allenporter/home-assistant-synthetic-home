"""Test Synthetic Home initialization."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    floor_registry as fr,
    entity_registry as er,
)
from homeassistant.const import Platform


INVENTORY = """
---
areas:
- name: Backyard
  id: backyard
  floor: Ground
- name: Living Room
  id: living_room
  floor: Ground
- name: Loft
  id: loft
  floor: Upstairs
- name: Garage
  id: garage
  floor: Ground
- name: Basement
  id: basement
entities:
- name: Garage Door
  id: light.garage_door
  area: garage
  state: false
  attributes:
    supported_color_modes:
    - onoff
    color_mode:
    - onoff
"""


@pytest.mark.parametrize(("config_yaml"), [(INVENTORY)], ids=["yaml"])
async def test_areas(
    hass: HomeAssistant, setup_integration: None, area_registry: ar.AreaRegistry
) -> None:
    """Test that areas are created as defined in the inventory."""

    area_entries = area_registry.async_list_areas()
    assert {entry.name for entry in area_entries} == {
        "Backyard",
        "Living Room",
        "Loft",
        "Basement",
        "Garage",
    }


@pytest.mark.parametrize(("config_yaml"), [(INVENTORY)], ids=["yaml"])
async def test_floors(
    hass: HomeAssistant, setup_integration: None, floor_registry: fr.FloorRegistry
) -> None:
    """Test that areas are created as defined in the inventory."""

    floor_entries = floor_registry.async_list_floors()
    assert {entry.name for entry in floor_entries} == {"Ground", "Upstairs"}


@pytest.mark.parametrize(("config_yaml"), [(INVENTORY)], ids=["yaml"])
@pytest.mark.parametrize(("platforms"), [([Platform.LIGHT])])
async def test_entities(
    hass: HomeAssistant,
    setup_integration: None,
    entity_registry: er.EntityRegistry,
    area_registry: ar.AreaRegistry,
) -> None:
    """Test that areas for entities without devices are assigned properly."""

    area_entry = area_registry.async_get_or_create("Garage")
    entity_entries = er.async_entries_for_area(entity_registry, area_entry.id)
    assert {entry.entity_id for entry in entity_entries} == {"light.garage_door"}
