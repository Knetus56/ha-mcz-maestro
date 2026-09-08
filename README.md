# MCZ Maestro — Intégration Home Assistant

[![CI](https://github.com/Knetus56/ha-mcz-maestro/actions/workflows/ci.yml/badge.svg)](https://github.com/Knetus56/ha-mcz-maestro/actions/workflows/ci.yml)

Une intégration [Home Assistant](https://www.home-assistant.io/) pour contrôler et monitorer un poêle à granulés **MCZ Maestro**, via MQTT et un pont ESP32 maison (pas de cloud MCZ, tout en local).

## 🌟 Fonctionnalités

- 🔥 **Climate** : marche/arrêt et température de consigne
- 📊 **Monitoring** : température ambiante, température fumées, état textuel du poêle
- 🛜 **Disponibilité** : suit la liaison ESP1↔ESP2 (heartbeat + LWT MQTT)
- 🎛️ **Contrôle complet** : puissance, ventilateur, sortie fumées, mode de contrôle, son
- 🧺 **Bac à granulés** : capteur bac vide
- 🔁 **Bouton reboot** : redémarre le pont ESP32 (pas le poêle)
- 🏠 **Entités locales** : démarrage automatique et température minimum, pour vos propres automatisations (pas des données du poêle)
- 🔐 **Connexion locale** : réutilise l'intégration `mqtt` déjà configurée dans Home Assistant, pas de connexion broker séparée
- 🇫🇷 **Interface localisée** : français et anglais

## 📋 Entités

| Domaine | Entité | Description |
|---|---|---|
| climate | `climate.maestro` | Marche/arrêt + température de consigne |
| sensor | `temperature_ambiante`, `temperature_fumees`, `infos` | Températures et état textuel |
| binary_sensor | `online`, `bac_vide` | Liaison ESP1↔ESP2, bac à granulés |
| button | `reboot` | Redémarre le pont ESP32 |
| switch | `on_off`, `control_mode`, `son`, `demarrage_automatique`* | Commandes + helper local |
| number | `puissance`, `temperature_consigne`, `temperature_minimum`* | Réglages + helper local |
| select | `fan`, `sortie` | 0-5 ou "A" (auto) |

\* Entités locales pures, sans topic firmware : créées pour les automatisations de l'utilisateur, pas des données réelles du poêle.

## 🧩 Architecture

Le poêle communique via son propre WiFi avec un premier ESP32-S3 (WebSocket),
relié en UART à un second ESP32-S3 qui expose tout en MQTT vers le broker
local. Cette intégration ne parle qu'au broker MQTT (déjà configuré dans
Home Assistant) — le détail complet (topics, firmware, décisions
d'architecture) est dans [`PLUGIN_NOTES.md`](PLUGIN_NOTES.md).

## 📦 Installation

Pas encore publiée sur le store HACS officiel. Installation via dépôt personnalisé HACS :

1. HACS → ⋮ → Dépôts personnalisés
2. URL : `https://github.com/Knetus56/ha-mcz-maestro`, catégorie **Intégration**
3. Installer, redémarrer Home Assistant
4. Paramètres → Appareils et services → Ajouter une intégration → **MCZ Maestro**
