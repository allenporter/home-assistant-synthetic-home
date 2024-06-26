"""Cover platform for Synthetic Home."""

import datetime
from typing import Any
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, CALLBACK_TYPE
from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
    ATTR_POSITION,
    DOMAIN as COVER_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

# Used for eval to override behavior
COVER_INSTANT = False
COVER_STEP = 10
COVER_STEP_TIME = datetime.timedelta(seconds=1)
SUPPORTED_ATTRIBUTES = {"supported_features", "device_class", "current_position"}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up cover platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticCover(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == COVER_DOMAIN
    )


class SyntheticCover(SyntheticEntity, CoverEntity):
    """synthetic_home cover class."""

    # These are the attributes that represent the cover state
    _attr_is_closing = False
    _attr_is_closed = True
    _attr_is_opening = False
    # The position is used to infer the other attributes (0 is closed, 100 is open)
    _attr_current_cover_position: int = 0

    _target_cover_position: int | None = None
    _timer_unsub: CALLBACK_TYPE | None = None

    def __init__(
        self,
        entity: ParsedEntity,
        state: str | None = None,
        *,
        supported_features: CoverEntityFeature | None = None,
        device_class: CoverDeviceClass | None = None,
        current_position: int | None = None,
    ) -> None:
        """Initialize the SyntheticCover."""
        super().__init__(entity)
        if supported_features is not None:
            self._attr_supported_features = CoverEntityFeature(0) | supported_features
        if device_class:
            self._attr_device_class = device_class
        if current_position is not None:
            self._attr_current_cover_position = current_position
        elif state is not None:
            self._attr_current_cover_position = 100 if (state == "open") else 0
        self._attr_is_closed = self._attr_current_cover_position == 0

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        if self._timer_unsub is not None:
            self._timer_unsub()
            self._timer_unsub = None

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        if self._attr_current_cover_position == 0:
            # Already closed
            return
        self._attr_is_closing = True
        self._attr_is_opening = False
        self._target_cover_position = 0
        await self._start_moving()
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""

        if self._attr_current_cover_position == 100:
            # Already open
            return

        # The following attributes are set
        self._attr_is_closing = False
        self._attr_is_opening = True
        self._target_cover_position = 100
        await self._start_moving()
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position: int = kwargs[ATTR_POSITION]
        if self._attr_current_cover_position == position:
            # Nothing to do
            return
        self._target_cover_position = position
        self._attr_is_closing = (
            self._target_cover_position < self._attr_current_cover_position
        )
        self._attr_is_opening = (
            self._target_cover_position > self._attr_current_cover_position
        )
        await self._start_moving()
        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self._is_closing = False
        self._is_opening = False
        if self._timer_unsub is not None:
            self._timer_unsub()
            self._timer_unsub = None
            self._target_cover_position = None

    async def _start_moving(self) -> None:
        """Start moving the cover."""
        if COVER_INSTANT:
            await self._move_cover(datetime.datetime.now())
        elif self._timer_unsub is None:
            self._timer_unsub = async_track_time_interval(
                self.hass,
                action=self._move_cover,
                interval=COVER_STEP_TIME,
            )

    async def _move_cover(self, now: datetime.datetime) -> None:
        """Track time changes."""
        if COVER_INSTANT and self._target_cover_position is not None:
            # Jump to destination
            self._attr_current_cover_position = self._target_cover_position
        if (
            self._target_cover_position is not None
            and self._attr_current_cover_position > self._target_cover_position
        ):
            _LOGGER.debug("Cover moving down")
            self._attr_current_cover_position -= COVER_STEP
            self._attr_current_cover_position = max(
                self._attr_current_cover_position, self._target_cover_position
            )
        elif (
            self._target_cover_position is not None
            and self._attr_current_cover_position < self._target_cover_position
        ):
            _LOGGER.debug("Cover moving up")
            self._attr_current_cover_position += COVER_STEP
            self._attr_current_cover_position = min(
                self._attr_current_cover_position, self._target_cover_position
            )
        else:
            # Reached target
            _LOGGER.debug("Cover reached target")
            self._attr_is_closing = False
            self._attr_is_opening = False
            self._attr_is_closed = self._attr_current_cover_position == 0
            await self.async_stop_cover()
        self.async_write_ha_state()
