"""Test Synthetic Home media player."""

import pytest


from homeassistant.const import Platform
from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_MEDIA_STOP,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    SERVICE_VOLUME_SET,
    SERVICE_MEDIA_NEXT_TRACK,
    SERVICE_MEDIA_PREVIOUS_TRACK,
    ATTR_MEDIA_VOLUME_LEVEL,
    SERVICE_MEDIA_PLAY,
    SERVICE_PLAY_MEDIA,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

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
        "volume_level": 0.5,
        "supported_features": 22461,
        "media_track": 0,
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
    assert state.state == "idle"

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MEDIA_PLAY,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 0.5,
        "supported_features": 22461,
        "media_track": 0,
    }

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_VOLUME_SET,
        service_data={ATTR_ENTITY_ID: test_entity, ATTR_MEDIA_VOLUME_LEVEL: 0.6},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 0.6,
        "supported_features": 22461,
        "media_track": 0,
    }

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MEDIA_NEXT_TRACK,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 0.6,
        "supported_features": 22461,
        "media_track": 1,
    }

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MEDIA_PREVIOUS_TRACK,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 0.6,
        "supported_features": 22461,
        "media_track": 0,
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
    assert state.state == "idle"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "supported_features": 22461,
        "volume_level": 0.6,
        "media_track": 0,
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
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "supported_features": 22461,
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/smart-speaker-example.yaml", "media_player.smart_speaker")],
)
async def test_smart_speaker_play_media(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test smart speaker playing media."""

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MEDIA_STOP,
        service_data={ATTR_ENTITY_ID: test_entity},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "idle"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "supported_features": 22461,
        "volume_level": 0.5,
        "media_track": 0,
    }

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_PLAY_MEDIA,
        service_data={
            ATTR_ENTITY_ID: test_entity,
            ATTR_MEDIA_CONTENT_TYPE: "audio",
            ATTR_MEDIA_CONTENT_ID: "media-source://foo",
        },
        blocking=True,
    )
    state = hass.states.get(test_entity)
    assert state
    assert state.state == "playing"
    assert state.attributes == {
        "friendly_name": "Smart Speaker",
        "device_class": "speaker",
        "volume_level": 0.5,
        "supported_features": 22461,
        "media_track": 0,
    }
