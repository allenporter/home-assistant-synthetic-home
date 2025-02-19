"""Media platform for Synthetic Home."""

from typing import Any
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaPlayerDeviceClass,
    MediaPlayerEnqueue,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SyntheticEntity
from .model import ParsedEntity, filter_attributes

_LOGGER = logging.getLogger(__name__)

VOLUME_STEP = 1

TRACKS = 20

SUPPORTED_ATTRIBUTES = set(
    {
        "device_class",
        "supported_features",
        "media_track",
        "volume_level",
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up media player platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticMediaPlayer(
            entity,
            state=entity.state,
            **filter_attributes(entity, SUPPORTED_ATTRIBUTES),
        )
        for entity in synthetic_home.entities
        if entity.platform == MEDIA_PLAYER_DOMAIN
    )


class SyntheticMediaPlayer(SyntheticEntity, MediaPlayerEntity):
    """synthetic_home media player class."""

    def __init__(
        self,
        entity: ParsedEntity,
        state: MediaPlayerState | None = None,
        *,
        device_class: MediaPlayerDeviceClass | None = None,
        supported_features: MediaPlayerEntityFeature | None = None,
        media_track: int = 0,
        volume_level: float = 0.5,
    ) -> None:
        """Initialize the SyntheticMediaPlayer."""
        super().__init__(entity)
        self._attr_device_class = device_class
        if supported_features is not None:
            self._attr_supported_features = (
                MediaPlayerEntityFeature(0) | supported_features
            )
        self._track = media_track
        if state:
            self._attr_state = state
            self._update_track()

        self._attr_volume_level = volume_level

    def _update_track(self) -> None:
        if (
            self._attr_state != MediaPlayerState.OFF
            and self._attr_device_class != MediaPlayerDeviceClass.TV
        ):
            self._attr_media_track = self._track
        else:
            self._attr_media_track = None

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        self._attr_state = MediaPlayerState.IDLE
        self._track = 0
        self._update_track()
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        self._attr_state = MediaPlayerState.OFF
        self._track = 0
        self._update_track()
        self.async_write_ha_state()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        self._attr_is_volume_muted = mute
        self.async_write_ha_state()

    async def async_volume_up(self) -> None:
        """Increase volume."""
        assert self.volume_level is not None
        self._attr_volume_level = min(1.0, self.volume_level + 0.1)
        self.async_write_ha_state()

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        assert self.volume_level is not None
        self._attr_volume_level = max(0.0, self.volume_level - 0.1)
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the volume level, range 0..1."""
        self._attr_volume_level = volume
        self.async_write_ha_state()

    async def async_play_media(
        self,
        media_type: str,
        media_id: str,
        enqueue: MediaPlayerEnqueue | None = None,
        announce: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Play a piece of media.

        Currently does not yet track the actual media being played.
        """
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Stop the media from playing."""
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Stop the media from playing."""
        self._attr_state = MediaPlayerState.IDLE
        self.async_write_ha_state()

    async def async_media_next_track(self) -> None:
        """Send next track command.

        Currently does not yet track the actual media being played.
        """
        self._attr_state = MediaPlayerState.PLAYING
        self._track += 1
        if self._track >= TRACKS:
            self._track = 0
        self._update_track()
        self.async_write_ha_state()

    async def async_media_previous_track(self) -> None:
        """Send previous track command.

        Currently does not yet track the actual media being played.
        """
        self._attr_state = MediaPlayerState.PLAYING
        self._track -= 1
        if self._track < 0:
            self._track = TRACKS - 1
        self._update_track()
        self.async_write_ha_state()
