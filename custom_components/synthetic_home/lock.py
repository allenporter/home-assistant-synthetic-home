"""Lock platform for Synthetic Home."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_CODE
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.lock import (
    LockEntity,
    LockEntityFeature,
    DOMAIN as LOCK_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up lock platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticHomeLock(entity, state=entity.state, **entity.attributes)
        for entity in synthetic_home.entities
        if entity.platform == LOCK_DOMAIN
    )


class SyntheticHomeLock(SyntheticEntity, LockEntity):
    """synthetic_home lock class."""

    _code: str | None = None

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None = None,
        *,
        supported_features: LockEntityFeature | None = None,
        is_locked: bool | None = None,
        is_locking: bool | None = None,
        is_open: bool | None = None,
        is_opening: bool | None = None,
        is_jammed: bool | None = None,
        code_format: str | None = None,
        code: str | None = None,
    ) -> None:
        """Initialize SyntheticHomeLock."""
        super().__init__(entity)
        if supported_features:
            self._attr_supported_features = LockEntityFeature(0) | supported_features
        if state is not None:
            self._attr_is_locked = state == "locked"
            self._attr_is_locking = state == "locking"
            self._attr_is_open = state == "open"
            self._attr_is_opening = state == "opening"
            self._attr_is_jammed = state == "jammed"
        if is_locked is not None:
            self._attr_is_locked = is_locked
        if is_locking is not None:
            self._attr_is_locking = is_locking
        if is_open is not None:
            self._attr_is_open = is_open
        if is_opening is not None:
            self._attr_is_opening = is_opening
        if is_jammed is not None:
            self._attr_is_jammed = is_jammed
        if code_format is not None:
            self._attr_code_format = code_format
        if code is not None:
            self._code = code

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the lock.

        This implementation does not require a code to lock.
        """
        # Implementation
        self._attr_is_locked = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the lock.

        This implementation may optionally require a code to unlock.
        """
        if self._code is not None:
            if kwargs.get(ATTR_CODE) != self._code:
                raise HomeAssistantError("Invalid lock code")
        self._attr_is_locked = False
        self.async_write_ha_state()

    async def async_open(self, **kwargs: Any) -> None:
        """Open the door latch."""
        if self._code is not None:
            if kwargs.get(ATTR_CODE) != self._code:
                raise HomeAssistantError("Invalid lock code")
        self._attr_is_open = True
        self._attr_is_locked = False
        self.async_write_ha_state()
