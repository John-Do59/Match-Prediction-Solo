# Guide d'Apprentissage : Docker et Micro-services

Ce document explique le fonctionnement de Docker et détaille l'implémentation de l'architecture micro-services dans le projet **Match Prediction App**.

---

## Introduction à Docker

### C'est quoi ?

Docker est une plateforme qui permet d'emballer une application et toutes ses dépendances (librairies, configuration, environnement) dans une unité isolée appelée **Conteneur**.

### Pourquoi Docker ?

- **"It works on my machine"** : Garanti que si ça tourne sur ton ordi, ça tournera partout (Serveur, Cloud, PC d'un collègue).
- **Isolation** : Chaque micro-service vit dans sa propre boîte. Si l'API ML plante, elle ne fait pas tomber la base de données.
- **Légèreté** : Contrairement à une machine virtuelle, Docker partage les ressources de ton ordinateur sans simuler tout un système d'exploitation.

### Lexique Essentiel

| Terme | Définition simple |
| :--- | :--- |
| **Image** | C'est le "plan" ou le moule. C'est un fichier statique qui contient ton code et tes réglages. |
| **Conteneur** | C'est l'image en train de tourner. C'est l'instance vivante de ton application. |
| **Dockerfile** | La recette de cuisine qui explique comment transformer ton code en image. |
| **Volume** | Un disque dur persistant. Sert à garder les données (ex: ta BDD) même si le conteneur est supprimé. |
| **Réseau (Network)** | Un câble invisible qui relie tes conteneurs entre eux (`match-network`). |
| **Orchestration** | L'art de coordonner le démarrage et la communication entre plusieurs conteneurs. |

---

## Cycle de Vie : Du Code au Conteneur

Pour transformer ton code Python ou Vue.js en une application qui tourne, on suit deux étapes clés :

### 1. La Construction (Build) -> L'Image
On utilise la commande `docker build`. Docker lit ton **Dockerfile** (la recette) et crée une **Image** (le plat préparé mais pas encore servi).
- **Analogy** : C'est comme compiler un programme ou imprimer un livre. L'image est figée.
- **Commande type** : `docker build -t mon-image .`

### 2. L'Exécution (Run) -> Le Conteneur
On utilise la commande `docker run`. Docker prend l'image et la lance dans un environnement isolé. C'est à ce moment-là que l'application devient "vivante".
- **Analogy** : C'est comme ouvrir le livre et commencer à le lire. Tu peux lancer plusieurs conteneurs (plusieurs lecteurs) à partir de la même image.
- **Commande type** : `docker run -d mon-image`

---

## Architecture du Projet

Notre implémentation supporte deux environnements distincts pilotés par des scripts d'automatisation.

### Composants Clés

1. **Frontend (Port 8082 / 8443)** : Interface utilisateur (Nginx + Vue.js) sécurisée par SSL en production.
2. **API App (Port 8000)** : Backend principal (FastAPI + PostgreSQL).
3. **API ML (Port 8001)** : Intelligence Artificielle (FastAPI + Modèles Pré-entraînés).
4. **PostgreSQL (Port 5432)** : Base de données relationnelle unique.

### Volumes et Persistance

- **match_prediction_pg_data** : Volume Docker persistant pour les données PostgreSQL.
- **ssl (local)** : Dossier contenant les certificats SSL, montés en lecture seule dans le frontend.

---

## Gestion des Environnements (DEV vs PROD)

Le projet sépare strictement les configurations de développement et de production.

### Les fichiers d'environnement

| Fichier | Usage | Sécurité |
| :--- | :--- | :--- |
| `.env.dev` | Développement local | Simple, HTTP |
| `.env.prod` | Simulation Production | Renforcée, HTTPS obligatoire |

**Sécurité des Secrets** : Les credentials (`POSTGRES_PASSWORD`) sont injectés via l'argument `--env-file` de Docker. Cela garantit qu'ils n'apparaissent jamais dans les logs de build ou l'inspection des conteneurs.

---

## Guide d'Utilisation

### 1. Mode Développement (Rapide)

Ce mode lance tout l'écosystème en HTTP pour faciliter le debug.

```bash
./scripts/start-dev.sh
```
*Accès : http://localhost:8082*

### 2. Mode Production (Sécurisé)

Ce mode simule un environnement de production avec HTTPS activé.

```bash
./scripts/start-prod.sh
```
*Accès : https://localhost:8443*

### 3. Nettoyage

```bash
./scripts/docker_clean.sh
```

---

## Bonnes Pratiques : Le fichier `.dockerignore`

Le fichier `.dockerignore` est crucial pour la santé de votre architecture :

1. **Isolation des Secrets** : Il empêche la copie des fichiers `.env.*` dans l'image. Les secrets sont fournis uniquement au runtime.
2. **Performance** : Il ignore les dossiers lourds (`node_modules`, `.git`, `venv`) pour accélérer le build.
3. **Intégrité des Migrations (Alembic)** : Il ne faut jamais ignorer les fichiers de migration (`alembic/versions/`).

---

## Résolution de Problèmes

| Problème | Solution |
| :--- | :--- |
| **Port already in use** | Lancez `./scripts/docker_clean.sh`. |
| **Database not initialized** | Supprimez le volume : `docker volume rm match_prediction_pg_data`. |
| **Frontend Crash (Alpine)** | Vérifiez que `docker-entrypoint.sh` utilise `#!/bin/sh`. |

---
*Dernière mise à jour : 28 Avril 2026*
