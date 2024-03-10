"""Test Synthetic Home init module."""

import pytest
from syrupy import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.synthetic_home.const import (
    DOMAIN,
    ATTR_AREA_NAME,
    ATTR_RESTORABLE_ATTRIBUTES_KEY,
    ATTR_DEVICE_NAME,
    ATTR_CONFIG_ENTRY_ID,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import FIXTURES


CAMERA_FIXTURE = f"{FIXTURES}/camera-example.yaml"


@pytest.mark.parametrize(
    ("platforms", "config_yaml_fixture", "restorable_attributes_key"),
    [
        ([Platform.BINARY_SENSOR], CAMERA_FIXTURE, attribute_key)
        for attribute_key in (
            "idle",
            "person-detected",
            "sound-detected",
            "motion-detected",
        )
    ],
)
async def test_evaluation_states(
    hass: HomeAssistant,
    setup_integration: None,
    config_entry: MockConfigEntry,
    config_yaml_fixture: str,
    restorable_attributes_key: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the loading evaluation states for a specific device."""

    await hass.services.async_call(
        DOMAIN,
        "set_synthetic_device_state",
        service_data={
            ATTR_CONFIG_ENTRY_ID: config_entry.entry_id,
            ATTR_DEVICE_NAME: "Outdoor Camera",
            ATTR_AREA_NAME: "Backyard",
            ATTR_RESTORABLE_ATTRIBUTES_KEY: restorable_attributes_key,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    states = {
        entity: hass.states.get(entity).state
        for entity in (
            "binary_sensor.outdoor_camera_motion",
            "binary_sensor.outdoor_camera_person",
            "binary_sensor.outdoor_camera_sound",
        )
    }
    assert states == snapshot

    await hass.services.async_call(
        DOMAIN,
        "clear_synthetic_device_state",
        service_data={
            ATTR_CONFIG_ENTRY_ID: config_entry.entry_id,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    # Verify all states have been restored
    states = {
        entity: hass.states.get(entity).state
        for entity in (
            "binary_sensor.outdoor_camera_motion",
            "binary_sensor.outdoor_camera_person",
            "binary_sensor.outdoor_camera_sound",
        )
    }
    assert states == {
        "binary_sensor.outdoor_camera_motion": "off",
        "binary_sensor.outdoor_camera_person": "off",
        "binary_sensor.outdoor_camera_sound": "off",
    }
