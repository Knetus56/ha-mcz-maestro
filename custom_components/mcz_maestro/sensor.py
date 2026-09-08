"""Sensors for MCZ Maestro (températures + texte d'état)."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_TOPIC_PREFIX,
    DOMAIN,
    TOPIC_INFOS,
    TOPIC_TEMPERATURE_AMBIANTE,
    TOPIC_TEMPERATURE_FUMEE,
)
from .entity import MczMqttEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MCZ Maestro sensors from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities(
        [
            MczTemperatureSensor(
                entry, "temperature_fumee", "temperature_fumee", prefix, TOPIC_TEMPERATURE_FUMEE
            ),
            MczTemperatureSensor(
                entry,
                "temperature_ambiante",
                "temperature_ambiante",
                prefix,
                TOPIC_TEMPERATURE_AMBIANTE,
            ),
            MczInfosSensor(entry, "infos", "infos", prefix, TOPIC_INFOS),
        ]
    )


class MczTemperatureSensor(MczMqttEntity, SensorEntity):
    """Sensor de température (fumée ou ambiante), publié déjà en °C réels."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def _handle_state(self, payload: str) -> None:
        try:
            self._attr_native_value = float(payload)
        except ValueError:
            return


class MczInfosSensor(MczMqttEntity, SensorEntity):
    """État textuel du poêle (ex: "Eteint", "Puissance 3", "Error A01 - ...")."""

    def _handle_state(self, payload: str) -> None:
        self._attr_native_value = payload
