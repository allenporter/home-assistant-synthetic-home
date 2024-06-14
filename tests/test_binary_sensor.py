"""Test Synthetic Home sensor."""

import pytest
from syrupy import SnapshotAssertion


from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up binary_sensor platform."""
    return [Platform.BINARY_SENSOR]


@pytest.mark.parametrize(
    ("config_yaml_fixture"), [(f"{FIXTURES}/motion-sensor-example.yaml")]
)
async def test_motion_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a binary sensor that detects motion."""

    state = hass.states.get("binary_sensor.front_yard_motion")
    assert state
    assert state.state == "on"
    assert state.attributes == {
        "friendly_name": "Front Yard Motion",
        "device_class": "motion",
    }

    state = hass.states.get("binary_sensor.front_yard_motion_battery")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Front Yard Motion Battery",
        "device_class": "battery",
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture"), [(f"{FIXTURES}/smart-lock-example.yaml")]
)
async def test_smart_lock(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a binary sensors for a smart lock."""

    state = hass.states.get("binary_sensor.front_door_lock")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Front Door Lock",
        "device_class": "lock",
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture"), [(f"{FIXTURES}/door-sensor-example.yaml")]
)
async def test_door_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a binary sensors for a smart lock."""

    state = hass.states.get("binary_sensor.front_door_sensor")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Front Door Sensor",
        "device_class": "door",
    }

    state = hass.states.get("binary_sensor.front_door_sensor_battery")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Front Door Sensor Battery",
        "device_class": "battery",
    }


@pytest.mark.parametrize(
    ("config_yaml_fixture"), [(f"{FIXTURES}/window-sensor-example.yaml")]
)
async def test_window_sensor(hass: HomeAssistant, setup_integration: None) -> None:
    """Test a binary sensors for a smart lock."""

    state = hass.states.get("binary_sensor.left_window_sensor")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Left Window Sensor",
        "device_class": "window",
    }

    state = hass.states.get("binary_sensor.left_window_sensor_battery")
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Left Window Sensor Battery",
        "device_class": "battery",
    }


@pytest.mark.parametrize(
    "config_yaml_fixture",
    [
        (f"{FIXTURES}/camera-idle.yaml"),
        (f"{FIXTURES}/camera-person-detected.yaml"),
        (f"{FIXTURES}/camera-sound-detected.yaml"),
        (f"{FIXTURES}/camera-motion-detected.yaml"),
    ],
)
async def test_camera_device_states(
    hass: HomeAssistant,
    setup_integration: None,
    config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the loading device states for a specific device."""

    for entity in (
        "binary_sensor.outdoor_camera_motion",
        "binary_sensor.outdoor_camera_person",
        "binary_sensor.outdoor_camera_sound",
    ):
        assert hass.states.get(entity), f"Entity {entity} not found"

    states = {
        entity: hass.states.get(entity).state
        for entity in (
            "binary_sensor.outdoor_camera_motion",
            "binary_sensor.outdoor_camera_person",
            "binary_sensor.outdoor_camera_sound",
        )
    }
    assert states == snapshot
