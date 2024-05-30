"""Media platform for Synthetic Home."""

from typing import Any
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
from .entity import SyntheticDeviceEntity
from .model import ParsedDevice

VOLUME_STEP = 1

TRACKS = [
    "Neon Sunrise",
    "Whispers in the Wind",
    "City of Starlight",
    "Renegade Heart",
    "The Last Campfire",
    "Daydreamer's Escape",
    "Symphony of Rain",
    "Lost in the Algorithm",
    "Chasing Fireflies",
    "Echoes of Forever",
    "Barcode Heart",
    "Map to Nowhere",
    "Breathe in the Wild",
    "Secrets of the Deep",
    "Stardust Serenade",
    "Chasing the Sun",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up media player platform."""
    synthetic_home = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        SyntheticMediaPlayer(device, entity.entity_key, **entity.attributes)
        for device in synthetic_home.devices
        for entity in device.entities
        if entity.platform == MEDIA_PLAYER_DOMAIN
    )


class SyntheticMediaPlayer(SyntheticDeviceEntity, MediaPlayerEntity):
    """synthetic_home media player class."""

    def __init__(
        self,
        device: ParsedDevice,
        key: str,
        device_class: MediaPlayerDeviceClass,
        *,
        supported_features: MediaPlayerEntityFeature | None = None,
        state: MediaPlayerState | None = None
    ) -> None:
        """Initialize the SyntheticMediaPlayer."""
        super().__init__(device, key)
        self._attr_device_class = device_class
        if supported_features is not None:
            self._attr_supported_features = (
                MediaPlayerEntityFeature(0) | supported_features
            )
        self._track = 0
        if state:
            self._attr_state = state
            if state != MediaPlayerState.OFF:
                self._attr_media_track = TRACKS[self._track]

        self._attr_volume_level = 1.0

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        self._attr_state = MediaPlayerState.PLAYING
        self._track = 0
        self._attr_media_track = TRACKS[self._track]
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        self._attr_state = MediaPlayerState.OFF
        self._track = 0
        self._attr_media_track = None
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

    async def async_media_play(self) -> None:
        """Send play command."""
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        self._attr_state = MediaPlayerState.PAUSED
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_play_media(
        self,
        media_type: str,
        media_id: str,
        enqueue: MediaPlayerEnqueue | None = None,
        announce: bool | None = None, **kwargs: Any,
    ) -> None:
        """Play a piece of media.

        Currently does not yet track the actual media being played.
        """
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_next_track(self) -> None:
        """Send next track command.

        Currently does not yet track the actual media being played.
        """
        self._attr_state = MediaPlayerState.PLAYING
        self._track += 1
        if self._track >= len(TRACKS):
            self._track = 0
        self._attr_media_track = TRACKS[self._track]
        self.async_write_ha_state()

    async def async_media_previous_track(self) -> None:
        """Send previous track command.

        Currently does not yet track the actual media being played.
        """
        self._attr_state = MediaPlayerState.PLAYING
        self._track -= 1
        if self._track < 0:
            self._track = len(TRACKS) - 1
        self._attr_media_track = TRACKS[self._track]
        self.async_write_ha_state()
