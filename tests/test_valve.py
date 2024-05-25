"""Test Synthetic Home valve."""

import pytest


from homeassistant.const import Platform
from homeassistant.components.valve import (
    DOMAIN as VALVE_DOMAIN,
    SERVICE_OPEN_VALVE,
    SERVICE_CLOSE_VALVE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.VALVE]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/valve-example.yaml", "valve.back_yard_water_valve")],
)
async def test_water_valve(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test water valve."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closed"
    assert state.attributes == {
        "friendly_name": "Back Yard Water Valve",
        "supported_features": 3,
    }

    await hass.services.async_call(
        VALVE_DOMAIN,
        SERVICE_OPEN_VALVE,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "open"

    await hass.services.async_call(
        VALVE_DOMAIN,
        SERVICE_CLOSE_VALVE,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "closed"
