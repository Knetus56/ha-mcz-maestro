"""Binary sensors for MCZ Maestro (liaison en ligne, bac à granulés vide)."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_TOPIC_PREFIX, DOMAIN, TOPIC_BAC_VIDE, TOPIC_ONLINE
from .entity import MczMqttEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MCZ Maestro binary sensors from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities(
        [
            MczOnlineBinarySensor(entry, "online", "online", prefix, TOPIC_ONLINE),
            MczBacVideBinarySensor(entry, "bac_vide", "bac_vide", prefix, TOPIC_BAC_VIDE),
        ]
    )


class MczOnlineBinarySensor(MczMqttEntity, BinarySensorEntity):
    """Heartbeat ESP1<->ESP2 (republié ~10s même sans changement) + LWT MQTT.

    Toujours disponible : c'est cette entité qui représente la
    disponibilité de la liaison, elle ne peut pas dépendre d'elle-même.
    """

    track_availability = False
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_registry_enabled_default = True

    def _handle_state(self, payload: str) -> None:
        self._attr_is_on = payload == "1"


class MczBacVideBinarySensor(MczMqttEntity, BinarySensorEntity):
    """Capteur bouton local sur l'ESP1 (pas une donnée du poêle).

    Pas de device_class : le texte "Vide"/"Plein" vient de
    strings.json/translations (state.binary_sensor.bac_vide), plus
    explicite que le générique "Problème détecté"/"OK" de device_class
    PROBLEM. Icône dynamique assortie (tasse vide/pleine).
    """

    def _handle_state(self, payload: str) -> None:
        self._attr_is_on = payload == "1"

    @property
    def icon(self) -> str:
        return "mdi:cup-outline" if self.is_on else "mdi:cup"
