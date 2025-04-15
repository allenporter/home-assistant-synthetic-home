"""Calendar platform for Synthetic Home."""

import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityFeature,
    CalendarEvent,
    DOMAIN as CALENDAR_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES = set(
    {
        "supported_features",
        "events",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up calendar platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticCalendarEntity(
            entity, **filter_attributes(entity, SUPPORTED_ATTRIBUTES)
        )
        for entity in synthetic_home.entities
        if entity.platform == CALENDAR_DOMAIN
    )


def parse_date_or_datetime(value: str) -> datetime.date | datetime.datetime:
    """Parse a date or datetime value from an isoformat string."""
    if len(value) > 10 or "T" in value:
        return datetime.datetime.fromisoformat(value)
    return datetime.date.fromisoformat(value)


DATETIME_FIELDS = {
    "start": "start",
    "end": "end",
    "dtstart": "start",
    "dtend": "end",
}


def create_event(attributes: dict[str, Any]) -> CalendarEvent:
    """Create a calendar event from the specified attributes."""
    fields = {}
    for attribute in ("summary", "description", "location"):
        if value := attributes.get(attribute):
            fields[attribute] = value
    for from_field, to_field in DATETIME_FIELDS.items():
        if value := attributes.get(from_field):
            if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                fields[to_field] = value
            else:
                fields[to_field] = parse_date_or_datetime(value)
    _LOGGER.debug("create_event1=%s", attributes)
    _LOGGER.debug("create_event2=%s", fields)
    return CalendarEvent(**fields)


class SyntheticCalendarEntity(SyntheticEntity, CalendarEntity):
    """synthetic_home calendar class."""

    _attr_reports_position = False

    def __init__(
        self,
        entity: ParsedEntity,
        *,
        supported_features: CalendarEntityFeature | None = None,
        events: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the SyntheticCalendarEntity."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = (
                CalendarEntityFeature(0) | supported_features
            )
        self._events = [create_event(event) for event in events or []]

    @property
    def event(self) -> CalendarEvent | None:
        """Get the nextactive or upcoming calendar event."""
        now = dt_util.now()
        for event in self._events:
            if event.end_datetime_local < now:
                return event
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        result = []
        for event in self._events:
            if event.end_datetime_local < start_date:
                continue
            if end_date < event.start_datetime_local:
                continue
            result.append(event)
        return result

    async def async_create_event(self, **kwargs: Any) -> None:
        """Add a new event to calendar."""
        self._events.append(create_event(kwargs))
