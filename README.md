# MCZ Maestro — Intégration Home Assistant

[![CI](https://github.com/Knetus56/ha-mcz-maestro/actions/workflows/ci.yml/badge.svg)](https://github.com/Knetus56/ha-mcz-maestro/actions/workflows/ci.yml)

Intégration `custom_component` pour piloter un poêle à granulés **MCZ Maestro** via MQTT.

⚠️ **Usage personnel, non distribuable** : ce plugin dépend d'un pont MQTT
maison à base de deux ESP32-S3 (firmware perso) — il ne fonctionnera pas
sans ce matériel spécifique. Pas destiné à d'autres utilisateurs.

## Entités

climate, sensors (température ambiante/fumées, état texte), binary_sensors
(en ligne, bac vide), bouton reboot, switches (marche/arrêt, mode contrôle,
son, démarrage auto), numbers (puissance, consigne, température minimum),
selects (ventilateur, sortie).


