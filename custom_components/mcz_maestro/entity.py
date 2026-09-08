"""Entités de base du plugin MCZ Maestro.

MQTT est un flux push (le poêle/ESP2 publie, rien à interroger) : pas de
DataUpdateCoordinator ici. Chaque entité s'abonne à son topic dans
async_added_to_hass et se désabonne dans async_will_remove_from_hass,
comme le fait la plateforme mqtt native de Home Assistant.
"""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, TOPIC_ONLINE

_LOGGER = logging.getLogger(__name__)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    """Appareil HA unique représentant le poêle (un seul par config entry)."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="MCZ",
        model="Maestro",
    )


class MczEntity(Entity):
    """Base commune : appareil, unique_id, nom traduit (has_entity_name)."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, key: str, translation_key: str) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = translation_key
        self._attr_device_info = _device_info(entry)


class MczMqttEntity(MczEntity):
    """Entité liée à un topic d'état MQTT du poêle.

    La disponibilité suit `<prefix>/online` : si ESP2 signale le poêle (ou
    la liaison série ESP1<->ESP2) hors-ligne, l'entité bascule
    indisponible. `track_availability = False` désactive ce comportement
    (utilisé par le binary_sensor "online" lui-même, qui représente cette
    information et doit rester toujours disponible).
    """

    track_availability = True

    def __init__(
        self,
        entry: ConfigEntry,
        key: str,
        translation_key: str,
        prefix: str,
        state_suffix: str,
    ) -> None:
        super().__init__(entry, key, translation_key)
        self._prefix = prefix
        self._state_topic = f"{prefix}/{state_suffix}"
        self._online_topic = f"{prefix}/{TOPIC_ONLINE}"
        self._attr_available = not self.track_availability
        self._unsub_state: Callable[[], None] | None = None
        self._unsub_online: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        @callback
        def _state_received(msg: Any) -> None:
            self._handle_state(msg.payload)
            self.async_write_ha_state()

        self._unsub_state = await mqtt.async_subscribe(
            self.hass, self._state_topic, _state_received
        )

        if self.track_availability:

            @callback
            def _online_received(msg: Any) -> None:
                self._attr_available = msg.payload == "1"
                self.async_write_ha_state()

            self._unsub_online = await mqtt.async_subscribe(
                self.hass, self._online_topic, _online_received
            )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_state:
            self._unsub_state()
        if self._unsub_online:
            self._unsub_online()

    def _handle_state(self, payload: str) -> None:
        """Traduit le payload MQTT brut reçu en état de l'entité HA."""
        raise NotImplementedError

    async def _async_publish(self, cmd_suffix: str, payload: str) -> None:
        await mqtt.async_publish(self.hass, f"{self._prefix}/{cmd_suffix}", payload)


class MczLocalEntity(MczEntity):
    """Entité locale pure, sans topic firmware (demarrage_automatique,
    temperature_minimum — cf. PLUGIN_NOTES.md ⚠️ : créées manuellement par
    l'utilisateur pour ses propres automatisations, pas des données du
    poêle). Toujours disponible. Chaque sous-classe se combine avec le mixin
    restore adapté à son domaine (RestoreEntity pour switch, RestoreNumber
    pour number, ...) pour restaurer son état au redémarrage de HA.
    """

    _attr_available = True
