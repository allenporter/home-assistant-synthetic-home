"""Todo platform for Synthetic Home."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.todo import (
    TodoListEntity,
    TodoListEntityFeature,
    TodoItem,
    DOMAIN as TODO_DOMAIN,
)

from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

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
        SyntheticTodoEntity(
            entity, **filter_attributes(entity.attributes, SUPPORTED_ATTRIBUTES)
        )
        for entity in synthetic_home.entities
        if entity.platform == TODO_DOMAIN
    )


class SyntheticTodoEntity(SyntheticEntity, TodoListEntity):
    """synthetic_home fan class."""

    _attr_reports_position = False

    def __init__(
        self,
        entity: ParsedEntity,
        *,
        supported_features: TodoListEntityFeature | None = None,
        todo_items: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the SyntheticFan."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = (
                TodoListEntityFeature(0) | supported_features
            )
        if todo_items is not None:
            self._attr_todo_items = [TodoItem(**item) for item in todo_items]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To-do list."""
        if self._attr_todo_items is None:
            self._attr_todo_items = []
        self._attr_todo_items.append(item)
        self.async_write_ha_state()
