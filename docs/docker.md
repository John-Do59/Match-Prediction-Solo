# Guide d'Apprentissage : Docker Multi-Environnement

Ce document explique le fonctionnement de Docker et détaille l'implémentation de l'architecture micro-services dans le projet **Match Prediction App**.

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
- **ssl (local)** : Dossier contenant les certificats SSL, monté en lecture seule dans le frontend.

---

## Gestion des Environnements (DEV vs PROD)

Le projet sépare strictement les configurations de développement et de production.

### Les fichiers d'environnement

| Fichier | Usage | Sécurité |
| :--- | :--- | :--- |
| `.env.dev` | Développement local | HTTP, ports standards |
| `.env.prod` | Simulation Production | HTTPS obligatoire, secrets renforcés |

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

Le fichier `.dockerignore` est crucial pour la sécurité :

1. **Isolation des Secrets** : Il empêche la copie des fichiers `.env.*` dans l'image. Les secrets sont fournis uniquement au runtime.
2. **Performance** : Il ignore les dossiers lourds (`node_modules`, `.git`, `venv`) pour accélérer le build.
3. **Persistance** : Les données volumineuses (datasets ML) ne sont pas incluses dans l'image mais montées via des volumes.

---

## Résolution de Problèmes

| Problème | Solution |
| :--- | :--- |
| **Port already in use** | Lancez `./scripts/docker_clean.sh`. |
| **Database not initialized** | Supprimez le volume : `docker volume rm match_prediction_pg_data`. |
| **Frontend Crash (Alpine)** | Vérifiez que `docker-entrypoint.sh` utilise `#!/bin/sh`. |

---
*Dernière mise à jour : 28 Avril 2026*
