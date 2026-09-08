# MCZ Maestro — Intégration Home Assistant

[![CI](https://github.com/Knetus56/ha-mcz-maestro/actions/workflows/ci.yml/badge.svg)](https://github.com/Knetus56/ha-mcz-maestro/actions/workflows/ci.yml)

Intégration `custom_component` pour piloter un poêle à granulés **MCZ Maestro** via MQTT.

⚠️ **Usage personnel, non distribuable** : ce plugin dépend d'un pont MQTT
maison à base de deux ESP32-S3 (firmware perso, voir `PLUGIN_NOTES.md`) —
il ne fonctionnera pas sans ce matériel spécifique. Pas destiné à d'autres
utilisateurs.

## Entités

climate, sensors (température ambiante/fumées, état texte), binary_sensors
(en ligne, bac vide), bouton reboot, switches (marche/arrêt, mode contrôle,
son, démarrage auto), numbers (puissance, consigne, température minimum),
selects (ventilateur, sortie).

Détails du protocole/architecture : [`PLUGIN_NOTES.md`](PLUGIN_NOTES.md).

## Installation

Copier `custom_components/mcz_maestro/` dans le dossier `custom_components`
de Home Assistant, redémarrer, puis ajouter l'intégration "MCZ Maestro"
depuis Réglages → Appareils et services.
