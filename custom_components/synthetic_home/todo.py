"""Todo platform for Synthetic Home."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.todo import (
    TodoListEntity,
    TodoListEntityFeature,
    TodoItem,
    TodoItemStatus,
    DOMAIN as TODO_DOMAIN,
)

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

SUPPORTED_ATTRIBUTES = set(
    {
        "supported_features",
        "todo_items",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up todo platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticTodoEntity(entity, **filter_attributes(entity, SUPPORTED_ATTRIBUTES))
        for entity in synthetic_home.entities
        if entity.platform == TODO_DOMAIN
    )


def create_todo_item(attributes: str | dict[str, Any]) -> TodoItem:
    """Create a todo item from the specified attributes."""
    if isinstance(attributes, str):
        attributes = {"summary": attributes}
    if (status_str := attributes.get("status")) and status_str == "completed":
        status = TodoItemStatus.COMPLETED
    else:
        status = TodoItemStatus.NEEDS_ACTION
    attributes.pop("status", None)
    return TodoItem(
        **attributes,
        status=status,
    )


class SyntheticTodoEntity(SyntheticEntity, TodoListEntity):
    """synthetic_home todo class."""

    _attr_reports_position = False

    def __init__(
        self,
        entity: ParsedEntity,
        *,
        supported_features: TodoListEntityFeature | None = None,
        todo_items: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the SyntheticTodoEntity."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = (
                TodoListEntityFeature(0) | supported_features
            )
        if todo_items is not None:
            self._attr_todo_items = [create_todo_item(item) for item in todo_items]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To-do list."""
        if self._attr_todo_items is None:
            self._attr_todo_items = []
        self._attr_todo_items.append(item)
        self.async_write_ha_state()
