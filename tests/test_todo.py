"""Test Synthetic Home todo."""

import pytest


from homeassistant.const import Platform
from homeassistant.components.todo import (
    DOMAIN as TODO_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.TODO]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/todo-list-example.yaml", "todo.tasks")],
)
async def test_todo_list(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test todo list."""

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "0"
    assert state.attributes == {
        "friendly_name": "Tasks",
        "supported_features": 3,
    }

    await hass.services.async_call(
        TODO_DOMAIN,
        "add_item",
        service_data={
            ATTR_ENTITY_ID: test_entity,
            "item": "New item",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "1"
