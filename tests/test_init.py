"""Test Synthetic Home initialization."""

import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from homeassistant.helpers import area_registry as ar, floor_registry as fr


from .conftest import FIXTURES


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
- name: Basement
  id: basement
"""

@pytest.mark.parametrize(("config_yaml"), [(INVENTORY)], ids=["yaml"])
async def test_areas(hass: HomeAssistant, setup_integration: None, area_registry: ar.AreaRegistry) -> None:
    """Test that areas are created as defined in the inventory."""

    area_entries = area_registry.async_list_areas()
    assert [ entry.name for entry in area_entries ] == [ "Backyard", "Living Room", "Loft", "Basement"]



@pytest.mark.parametrize(("config_yaml"), [(INVENTORY)], ids=["yaml"])
async def test_floors(hass: HomeAssistant, setup_integration: None, floor_registry: fr.FloorRegistry) -> None:
    """Test that areas are created as defined in the inventory."""

    floor_entries = floor_registry.async_list_floors()
    assert [ entry.name for entry in floor_entries ] == [ "Ground", "Upstairs"]
