"""Test Synthetic Home media player."""

import datetime

import pytest


from homeassistant.const import Platform
from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_MEDIA_PLAY,
    SERVICE_MEDIA_STOP,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    SERVICE_VOLUME_SET,
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_VOLUME_MUTED,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.MEDIA_PLAYER]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-speaker-example.yaml", "media_player.smart_speaker")],
)
async def test_smart_speaker(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test smart speaker as a media player."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 1.0,
        "supported_features": 21900,
    }

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_TURN_OFF,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"


    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_TURN_ON,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_VOLUME_SET,
        service_data={ATTR_ENTITY_ID: test_entity, ATTR_MEDIA_VOLUME_LEVEL: 0.5},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 0.5,
        "supported_features": 21900,
    }

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MEDIA_STOP,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"