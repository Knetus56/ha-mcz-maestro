# Notes pour le plugin Home Assistant — MCZ Maestro

Document de référence rassemblant tout ce qui a été découvert/construit avant
d'attaquer le plugin. Objectif du plugin : remplacer la découverte MQTT
générique (JSON codé en dur, supprimée du firmware) par un vrai
`custom_component` Python qui définit les entités proprement, **en gardant
MQTT comme transport** (décision prise après comparaison technique — cf.
section Architecture).

## Accès Home Assistant (test / prod)

Les URL MCP donnant accès complet en lecture/écriture aux deux instances HA
sont dans `/mnt/tower/appdata/claude-ha/.mcp-ha-keys.md` (fichier parent,
volontairement non dupliqué ici — contient des jetons d'authentification en
clair). Résumé sans les jetons :

- **ha-prod** : `/mnt/tower/appdata/HA`, HA sur port 8123, MCP sur port 9584
- **ha-test** : `/mnt/tower/appdata/HA_test`, HA sur port 8124, MCP sur port 9585
- Accessibles uniquement depuis le réseau local (192.168.1.100 = Tower NAS)
- Développer/tester le plugin sur **ha-test** en premier

## Le matériel réel derrière tout ça

- Poêle à granulés **MCZ Maestro**, carte mère réf. **41451904300**
- MCU carte mère : **ATSAM3X8E** (ARM Cortex-M3), firmware développé par
  **Fluidsoft** (société italienne, éditeur du logiciel MCZ)
- Firmware de la carte mère extrait par SWD et sauvegardé (pour référence,
  pas nécessaire au plugin) : `mcz bin/mcz_maestro_41451904300_firmware_dump_20260907.bin`
  + désassemblage complet dans le même dossier
- Le port USB natif de la carte mère (classe CDC "AT-commands") **ne répond
  pas** au protocole `C|Commande|...` — testé et confirmé négatif. Le module
  WiFi du poêle sert de pont entre son port série interne et le WebSocket
  externe ; il n'y a pas de raccourci matériel direct.

## Architecture actuelle (déjà fonctionnelle)

Deux ESP32-S3 soudés sur une même carte, reliés par UART (impossible de
fusionner en un seul : un radio WiFi ne peut être connecté qu'à un seul
réseau infrastructure à la fois, et il faut rejoindre à la fois le WiFi du
poêle ET le WiFi maison).

```
Poêle (WiFi propre "MCZ-0142F520200B6B", 192.168.120.1)
  │  WebSocket ws://192.168.120.1:81
  ▼
ESP1 — Maestro2-mcz (code: mcz bin/Maestro2-mcz/)
  │  UART 115200 baud, pins TX=43/RX=44 (attention : ce sont aussi les pins
  │  de boot UART0 par defaut de l'ESP32-S3, du bruit de boot y transite
  │  brievement a chaque reset, filtre par le prefixe "MCZ")
  ▼
ESP2 — Maestro2-mqtt (code: mcz bin/Maestro2-mqtt/)
  │  MQTT vers broker local
  ▼
Home Assistant (aujourd'hui : rien, MqttRecovery supprimee — c'est le travail du plugin)
```

Header partagé des constantes/protocole : `mcz bin/shared/mcz_protocol.h`

## Broker MQTT

- Host : `192.168.1.100`, port `1883`
- Identifiants : voir `mcz bin/Maestro2-mqtt/src/secrets.h` (non commité,
  gitignored) — `knetus` / mot de passe dans ce fichier
- Le plugin doit utiliser **la même intégration MQTT que celle déjà
  configurée dans Home Assistant** (`homeassistant.components.mqtt`,
  `mqtt.async_subscribe` / `mqtt.async_publish`), pas une connexion MQTT
  séparée avec ses propres identifiants — c'est le pattern standard pour un
  custom_component MQTT et ça évite de dupliquer la config broker.

## Topics d'état (publiés par ESP2, tous en `retain=true` sauf mention contraire)

| Topic | Valeurs / format | Notes |
|---|---|---|
| `maestroESP/online` | `1` ou `0` | **Heartbeat** : republié à chaque cycle (~10s), sans dédup, même si la valeur ne change pas — sert à détecter une liaison figée, pas juste un état statique. Complété par un **LWT MQTT** côté ESP2 (`setWill("maestroESP/online","0",retain=true)`) : si ESP2 disparaît sans prévenir, le broker publie `0` à sa place automatiquement. |
| `maestroESP/infos` | texte (ex: `"Eteint"`, `"Puissance 3"`, `"Error A01 - Allumage rate"`, ...) | Table complète des ~45 états dans `Maestro2-mcz/src/main.h` (`etatMCZ[]`) — inclut tous les codes d'erreur A01-A23 |
| `maestroESP/on_off` | `0` ou `1` | Dérivé de l'état (`etatMCZ[index].status`), pas une commande directe du poêle |
| `maestroESP/fan` | `0`-`6` | `6` = mode "A" (auto) côté select HA |
| `maestroESP/sortie` | `0`-`6` | Idem, `6` = "A" |
| `maestroESP/temperature_fumee` | entier, °C | |
| `maestroESP/temperature_ambiante` | décimal (`.00`), °C | valeur brute / 2 |
| `maestroESP/temperature_consigne` | décimal (`.00`), °C | valeur brute / 2 |
| `maestroESP/control_mode` | entier | |
| `maestroESP/puissance` | `1`-`5` | valeur brute - 10 |
| `maestroESP/bac_vide` | `0`/`1` | capteur bouton local sur l'ESP1 (`BUTTON_PIN`), pas une donnée du poêle |
| `maestroESP/son` | `0`/`1` | |

## Topics de commande (`maestroESP/Set/...`, souscrits par ESP2)

| Topic | Relayé vers le poêle en | Notes |
|---|---|---|
| `Set/reboot` | redémarre ESP1+ESP2 | ne touche pas le poêle lui-même |
| `Set/control_mode` | `WriteParametri\|40\|valeur` | |
| `Set/puissance` | `WriteParametri\|36\|valeur` | |
| `Set/sortie` | `WriteParametri\|38\|valeur` + `WriteParametri\|39\|valeur` | deux écritures pour ce champ |
| `Set/fan` | `WriteParametri\|37\|valeur` | |
| `Set/temperature_consigne` | `WriteParametri\|42\|valeur×2` | ESP2 multiplie par 2 avant envoi (unité demi-degré côté poêle) |
| `Set/on_off` | `WriteParametri\|34\|1` (on) ou `WriteParametri\|34\|40` (off) | valeurs magiques du protocole poêle |
| `Set/son` | `WriteParametri\|50\|valeur` | |

## Entités déjà pensées côté MCZ (ancien JSON MqttRecovery, pour référence)

Climate (mode chauffage + température), 2 sensors (temp ambiante/fumée) + 1
sensor texte (infos), 2 binary_sensor (online, bac_vide), bouton reboot, 4
switch (on_off, control_mode, son, demarrage_automatique), 3 number
(temperature_consigne, temperature_minimum, puissance), 2 select (fan,
sortie).

⚠️ **`demarrage_automatique` et `temperature_minimum` ne sont PAS des
données du poêle** — ce sont des entités créées manuellement dans HA par
l'utilisateur pour ses propres automatisations, à réintégrer telles quelles
côté plugin (pas de topic firmware réel derrière, à traiter comme des
helpers/inputs locaux à HA plutôt que des capteurs du poêle).

De même, le `mode_state_topic`/`mode_command_topic` du climate pointait vers
`maestroESP/state`, qui **n'existe pas** dans les topics réellement publiés
par le firmware (bug de l'ancien JSON, jamais alimenté) — utiliser
`maestroESP/on_off` à la place pour l'état marche/arrêt du climate.

## Décisions d'architecture déjà prises (ne pas reproposer)

- **MQTT gardé comme transport**, pas d'API HTTP/WebSocket directe sur
  l'ESP32 — comparaison technique faite, MQTT gagne sur tous les points
  (retain, LWT, découplage, simplicité côté ESP32)
- **Pas de cloud MCZ** (`app.mcz.it` / `s.maestro.mcz.it`) — tout doit
  fonctionner en local, sans dépendance internet
- Le firmware ESP32 est considéré **stable et terminé** pour l'instant (voir
  `mcz bin/Maestro2-mcz/` et `mcz bin/Maestro2-mqtt/`) — le plugin ne doit
  pas nécessiter de nouveaux changements firmware sauf besoin explicite
