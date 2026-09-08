"""Climate entity for MCZ Maestro (chauffage + température).

S'abonne à 3 topics d'état (on_off, temperature_ambiante,
temperature_consigne) + online pour la disponibilité : ne réutilise pas
MczMqttEntity (pensée pour un seul topic d'état) mais reste basée sur
MczEntity pour le device_info/unique_id communs.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_ON_OFF,
    CMD_TEMPERATURE_CONSIGNE,
    CONF_TOPIC_PREFIX,
    DOMAIN,
    ON_OFF_OFF,
    ON_OFF_ON,
    TOPIC_ON_OFF,
    TOPIC_ONLINE,
    TOPIC_TEMPERATURE_AMBIANTE,
    TOPIC_TEMPERATURE_CONSIGNE,
)
from .entity import MczEntity

MIN_TEMP = 15.0
MAX_TEMP = 30.0
TEMP_STEP = 0.5


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the climate entity from a config entry."""
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX]
    async_add_entities([MczClimate(entry, prefix)])


class MczClimate(MczEntity, ClimateEntity):
    """Le poêle, vu comme un climate HA (marche/arrêt + consigne)."""

    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP

    def __init__(self, entry: ConfigEntry, prefix: str) -> None:
        super().__init__(entry, "climate", "climate")
        self._prefix = prefix
        self._attr_available = False
        self._attr_hvac_mode = HVACMode.OFF
        self._unsubs: list[Callable[[], None]] = []

    async def async_added_to_hass(self) -> None:
        @callback
        def _online(msg: Any) -> None:
            self._attr_available = msg.payload == "1"
            self.async_write_ha_state()

        @callback
        def _on_off(msg: Any) -> None:
            self._attr_hvac_mode = (
                HVACMode.HEAT if msg.payload == "1" else HVACMode.OFF
            )
            self.async_write_ha_state()

        @callback
        def _current_temperature(msg: Any) -> None:
            try:
                self._attr_current_temperature = float(msg.payload)
            except ValueError:
                return
            self.async_write_ha_state()

        @callback
        def _target_temperature(msg: Any) -> None:
            try:
                self._attr_target_temperature = float(msg.payload)
            except ValueError:
                return
            self.async_write_ha_state()

        subscriptions = (
            (f"{self._prefix}/{TOPIC_ONLINE}", _online),
            (f"{self._prefix}/{TOPIC_ON_OFF}", _on_off),
            (f"{self._prefix}/{TOPIC_TEMPERATURE_AMBIANTE}", _current_temperature),
            (f"{self._prefix}/{TOPIC_TEMPERATURE_CONSIGNE}", _target_temperature),
        )
        for topic, cb in subscriptions:
            self._unsubs.append(await mqtt.async_subscribe(self.hass, topic, cb))

    async def async_will_remove_from_hass(self) -> None:
        for unsub in self._unsubs:
            unsub()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        payload = ON_OFF_ON if hvac_mode == HVACMode.HEAT else ON_OFF_OFF
        await mqtt.async_publish(self.hass, f"{self._prefix}/{CMD_ON_OFF}", payload)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await mqtt.async_publish(
            self.hass, f"{self._prefix}/{CMD_TEMPERATURE_CONSIGNE}", str(temperature)
        )
