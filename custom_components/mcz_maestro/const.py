"""Constantes du plugin MCZ Maestro.

Toutes les valeurs viennent de PLUGIN_NOTES.md et du firmware ESP32
(Maestro2-mqtt / shared/mcz_protocol.h) — un seul endroit à modifier ici si
le format ou les topics changent côté firmware.
"""

DOMAIN = "mcz_maestro"

CONF_TOPIC_PREFIX = "topic_prefix"
DEFAULT_TOPIC_PREFIX = "maestroESP"
DEFAULT_NAME = "Maestro"

# Suffixes des topics d'état publiés par ESP2 (Maestro2-mqtt), tous en
# retain=true sauf mention contraire. Ordre sans importance ici (contrairement
# au tableau topic[] côté firmware qui l'utilise comme index) : chaque
# plateforme s'abonne au suffixe qui la concerne.
TOPIC_ONLINE = "online"
TOPIC_INFOS = "infos"
TOPIC_ON_OFF = "on_off"
TOPIC_FAN = "fan"
TOPIC_SORTIE = "sortie"
TOPIC_TEMPERATURE_FUMEE = "temperature_fumee"
TOPIC_TEMPERATURE_AMBIANTE = "temperature_ambiante"
TOPIC_TEMPERATURE_CONSIGNE = "temperature_consigne"
TOPIC_CONTROL_MODE = "control_mode"
TOPIC_PUISSANCE = "puissance"
TOPIC_BAC_VIDE = "bac_vide"
TOPIC_SON = "son"

# Suffixes des topics de commande (souscrits par ESP2 sous "<prefix>/Set/").
CMD_REBOOT = "Set/reboot"
CMD_CONTROL_MODE = "Set/control_mode"
CMD_PUISSANCE = "Set/puissance"
CMD_SORTIE = "Set/sortie"
CMD_FAN = "Set/fan"
CMD_TEMPERATURE_CONSIGNE = "Set/temperature_consigne"
CMD_ON_OFF = "Set/on_off"
CMD_SON = "Set/son"

# Valeurs magiques du protocole poêle pour Set/on_off (cf. PLUGIN_NOTES.md).
ON_OFF_ON = "1"
ON_OFF_OFF = "40"

# fan / sortie : 0-5 = valeur directe, 6 = mode "A" (auto) côté HA.
FAN_SORTIE_AUTO_RAW = "6"
FAN_SORTIE_AUTO_LABEL = "A"
FAN_SORTIE_OPTIONS = ["0", "1", "2", "3", "4", "5", FAN_SORTIE_AUTO_LABEL]

# Bornes des entités locales pures (pas de topic firmware, cf. notes ⚠️).
TEMPERATURE_MINIMUM_DEFAULT = 16.0
TEMPERATURE_MINIMUM_MIN = 5.0
TEMPERATURE_MINIMUM_MAX = 30.0
TEMPERATURE_MINIMUM_STEP = 0.5

# Source unique des translation_key attendues par domaine, utilisée par la CI
# (job python-and-json) pour vérifier que strings.json/translations/*.json ne
# dérivent pas silencieusement des entités réellement créées. Le climate n'a
# pas de translation_key exploitée (nom = None, utilise le nom de l'appareil).
ENTITY_TRANSLATION_KEYS = {
    "sensor": ["temperature_fumee", "temperature_ambiante", "infos"],
    "binary_sensor": ["online", "bac_vide"],
    "button": ["reboot"],
    "switch": ["on_off", "control_mode", "son", "demarrage_automatique"],
    "number": ["puissance", "temperature_consigne", "temperature_minimum"],
    "select": ["fan", "sortie"],
}
