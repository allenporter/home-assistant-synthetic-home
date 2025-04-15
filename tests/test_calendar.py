"""Test Synthetic Home calendar."""

import pytest
from typing import Any

from homeassistant.const import Platform
from homeassistant.components.calendar import (
    DOMAIN as CALENDAR_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import FIXTURES


@pytest.fixture(name="platforms")
def mock_platforms() -> list[Platform]:
    """Set up platform."""
    return [Platform.CALENDAR]


@pytest.mark.parametrize(
    ("config_yaml_fixture", "test_entity"),
    [(f"{FIXTURES}/calendar-example.yaml", "calendar.personal")],
)
async def test_calendar(
    hass: HomeAssistant, setup_integration: None, test_entity: str
) -> None:
    """Test calendar."""

    async def get_events(**kwargs: Any) -> dict[str, Any]:
        response = await hass.services.async_call(
            CALENDAR_DOMAIN,
            "get_events",
            service_data={
                ATTR_ENTITY_ID: test_entity,
                "duration": "24:00",  # 1 day
                **kwargs,
            },
            blocking=True,
            return_response=True,
        )
        return response

    state = hass.states.get(test_entity)
    assert state
    assert state.state == "off"
    assert state.attributes == {
        "friendly_name": "Personal",
        "all_day": False,
        "description": "",
        "message": "Bastille Day",
        "location": "",
        "start_time": "1997-07-14 10:00:00",
        "end_time": "1997-07-14 21:00:00",
        "supported_features": 7,
    }

    response = await get_events()
    assert response == {
        "calendar.personal": {
            "events": [],
        }
    }
    response = await get_events(start_date_time="1997-07-14 00:00:00")
    assert response == {
        "calendar.personal": {
            "events": [
                {
                    "summary": "Bastille Day",
                    "start": "1997-07-14T17:00:00+00:00",
                    "end": "1997-07-15T04:00:00+00:00",
                },
            ],
        }
    }
    response = await get_events(start_date_time="1997-07-15 00:00:00")
    assert response == {
        "calendar.personal": {
            "events": [],
        }
    }

    await hass.services.async_call(
        CALENDAR_DOMAIN,
        "create_event",
        service_data={
            ATTR_ENTITY_ID: test_entity,
            "summary": "New item",
            "start_date": "2025-04-01",
            "end_date": "2025-04-02",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    response = await get_events(start_date_time="2025-04-01 00:00:00")
    assert response == {
        "calendar.personal": {
            "events": [
                {
                    "summary": "New item",
                    "start": "2025-04-01",
                    "end": "2025-04-02",
                },
            ],
        }
    }
