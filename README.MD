# crous-accommodation-notifier

Ce bot Python permet de notifier par Telegram la disponibilité de logements Crous.

## Description

Le bot parse le site [Trouver un logement](https://trouverunlogement.lescrous.fr/) des Crous et envoie une notification Telegram si de nouveaux logements sont disponibles.

Les fonctionnalités :

- Se connecte au site "Trouver un logement" avec les identifiants MSE
- Pour chaque utilisateur Telegram et sa zone choisie :
  - Récupère les logements disponibles dans la zone
  - Envoie un message Telegram avec le nombre et les descriptions des logements

### Exemple

<img src="docs/img/example_notification.jpg" alt= “” width="400">

## Pré-requis

- Python 3.8+

### Bot télégram

- Un bot télégram qui enverra les notifications
- Votre id utilisateur télégram

### Url de recherche

L'url de recherche sur [trouverunlogement.lescrous.fr](https://trouverunlogement.lescrous.fr).

Celle-ci doit faire référence à une zone géographique dans laquelle effectuer la recherche. Elle contient deux coordonnées géographiques qui définissent un rectangle.

**Exemple** : https://trouverunlogement.lescrous.fr/tools/32/search?bounds=2.8265889_42.7488722_2.9825668_42.6492606

Elle peut être obtenue en effectuant une recherche par ville, ou en cliquant sur `Rechercher dans la zone` lors d'une recherche sur la carte.

Elle peut contenir des filtres ou non.

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/SuperMuel/crous-accommodation-notifier.git
cd crous-accommodation-notifier
```

Installer les dépendances :

```bash
poetry install
```

Copier le fichier `.env.template` vers `.env` et le remplir correctement. Il contiendra les informations
nécessaires pour se connecter à [trouverunlogement.lescrous.fr](https://trouverunlogement.lescrous.fr/),
le token du bot Telegram, ainsi que d'autres paramètres.

# Utilisation

Lancer le script :

```bash
poetry run python main.py
```
