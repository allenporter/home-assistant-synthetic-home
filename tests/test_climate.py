"""Test Synthetic Home climate entity."""

import pytest
from syrupy import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.components.climate import (
    SERVICE_SET_HVAC_MODE,
    DOMAIN as CLIMATE_DOMAIN,
    ATTR_HVAC_MODE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import HOMES

TEST_ENTITY = "climate.family_room"


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up switch platform."""
    return [Platform.CLIMATE]


@pytest.mark.parametrize(
    ("config_yaml_fixture"),
    [(f"{HOMES}/hvac-example.yaml")],
)
async def test_climate_hvac_entity(
    hass: HomeAssistant, setup_integration: None
) -> None:
    """Test an HVAC device."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Family Room",
        "current_temperature": 16.7,
        "fan_mode": None,
        "fan_modes": ["low", "high", "off"],
        "hvac_action": "off",
        "hvac_modes": ["off", "cool", "heat", "auto"],
        "max_temp": 35,
        "min_temp": 7,
        "supported_features": 394,
        "target_temp_high": None,
        "target_temp_low": None,
    }
    attributes = dict(state.attributes)

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: TEST_ENTITY, ATTR_HVAC_MODE: "heat"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "heat"
    assert state.attributes == attributes

    device_registry = dr.async_get(hass)
    assert len(device_registry.devices) == 1
    device = next(iter(device_registry.devices.values()))
    assert device.suggested_area == "Family room"
    assert device.name == "Family Room"
    assert device.manufacturer == "Nest"
    assert device.sw_version == "1.0.0"


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{HOMES}/heat-pump-example.yaml", "climate.family_room")],
)
async def test_heat_pump(
    hass: HomeAssistant,
    setup_integration: None,
    test_entity: str,
) -> None:
    """Test a heat pump climate entity."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Family Room",
        "current_temperature": 15.6,
        "fan_mode": None,
        "fan_modes": ["low", "high", "off"],
        "hvac_action": "off",
        "hvac_modes": ["heat", "off"],
        "max_temp": 35,
        "min_temp": 7,
        "supported_features": 392,
    }
    attributes = dict(state.attributes)

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: TEST_ENTITY, ATTR_HVAC_MODE: "heat"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "heat"
    assert state.attributes == attributes


@pytest.mark.parametrize(
    ("config_yaml_fixture"),
    [
        (f"{HOMES}/hvac-cooling.yaml"),
        (f"{HOMES}/hvac-off.yaml"),
        (f"{HOMES}/hvac-very-low.yaml"),
    ],
)
async def test_hvac_device_state(
    hass: HomeAssistant,
    setup_integration: None,
    config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test an HVAC device with restorable state."""
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert (state.state, state.attributes) == snapshot
