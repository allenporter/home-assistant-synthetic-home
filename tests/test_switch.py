"""Test Synthetic Home switch."""

import pytest
from unittest.mock import patch, mock_open

from homeassistant.const import Platform
from homeassistant.components.switch import (
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    DOMAIN as SWITCH_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

TEST_YAML = """
---
name: Family Farmhouse
country_code: US
location: Rural area in Iowa
type: Farmhouse
device_entities:
  Chicken Coop:
  - name: smart_feeder
    entities:
    - switch.chicken_coop_feeder
"""


TEST_ENTITY = "switch.chicken_coop_feeder"



@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Setup switch platform."""
    return [Platform.SWITCH]


@pytest.fixture
def config_yaml() -> None:
    """Mock out the yaml config file contents."""
    return TEST_YAML


async def test_switch_services(hass: HomeAssistant, setup_integration: None) -> None:
    """Test switch services."""

    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Smart Feeder"
    }

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: TEST_ENTITY},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: TEST_ENTITY},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(TEST_ENTITY)
    assert state
    assert state.state == "on"
