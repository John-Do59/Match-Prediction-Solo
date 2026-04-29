# Infrastructure Docker Compose

## Architecture des Services

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                   frontend-network                       │
│                                                          │
│   [gateway / Traefik]  ←── PROD uniquement              │
│           │                                              │
│   [frontend-dev]  ←── DEV uniquement (port 8083)        │
│   [frontend-prod] ←── PROD uniquement (via Traefik)     │
│           │                                              │
│   ┌───────┼───────┐                                     │
│   │       │       │                                      │
└───┼───────┼───────┼──────────────────────────────────────┘
    │       │       │
┌───┼───────┼───────┼──────────────────────────────────────┐
│   │  backend-network  │                                   │
│   ▼       ▼       ▼                                      │
│ [api-app] [api-ml] (accès DB)                            │
│     │         │                                           │
│  [db-app]  [db-ml]  ←── DB ISOLÉES (pas de port exposé) │
└─────────────────────────────────────────────────────────┘
```

---

## Réseaux

| Réseau | Services | Accès externe |
| :--- | :--- | :--- |
| `frontend-network` | gateway, frontend, api-app, api-ml | Oui (via ports) |
| `backend-network` | api-app, api-ml, db-app, db-ml | **Non** |

> Les bases de données sont **invisibles** depuis l'extérieur du réseau Docker. Elles ne sont accessibles que par les APIs via le réseau `backend-network`.

---

## Profiles (Environnements)

### DEV — `docker compose --profile dev up --build`

| Service | Port exposé | Notes |
| :--- | :---: | :--- |
| `db-app` | — | Backend uniquement |
| `db-ml` | — | Backend uniquement |
| `api-app` | 8000 | HTTP |
| `api-ml` | 8001 | HTTP |
| `frontend-dev` | **8083** | HTTP, hot-reload friendly |

### PROD — `docker compose --profile prod up --build`

| Service | Port exposé | Notes |
| :--- | :---: | :--- |
| `db-app` | — | Non exposé |
| `db-ml` | — | Non exposé |
| `api-app` | 8000 | HTTP (interne) |
| `api-ml` | 8001 | HTTP (interne) |
| `gateway` (Traefik) | 80, 443, 8080 | Reverse proxy + SSL |
| `frontend-prod` | — | Exposé via Traefik uniquement |

---

## Gestion des Variables d'Environnement

**Une seule approche** : fichier `.env` à la racine (copie de `.env.dev` ou `.env.prod`).

```bash
# Dev
cp .env.dev .env

# Prod
cp .env.prod .env
```

Le `docker-compose.yml` lit automatiquement le fichier `.env` sans `env_file` explicite.

**Variables requises** :

| Variable | Exemple | Usage |
| :--- | :--- | :--- |
| `DB_USER` | `myuser` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | `secret` | Mot de passe PostgreSQL |
| `DB_NAME` | `footballapp_db` | Base de données API App |
| `DB_ML_NAME` | `footballml_db` | Base de données API ML |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Connexion API App |
| `DATABASE_URL_ML` | `postgresql+asyncpg://...` | Connexion API ML |

---

## Commandes Essentielles

```bash
# Démarrer en DEV
cp .env.dev .env
docker compose --profile dev up --build

# Démarrer en PROD
cp .env.prod .env
docker compose --profile prod up --build

# Arrêter et supprimer les volumes (reset complet)
docker compose down -v

# Voir les logs d'un service
docker compose logs -f api-app

# Ouvrir un shell dans un container
docker compose exec api-app bash

# Lancer les migrations manuellement
docker compose exec api-app alembic upgrade head
```

---

## Healthchecks & Dépendances

Le démarrage des services suit l'ordre suivant grâce aux `depends_on + condition: service_healthy` :

```
db-app (healthy) ──► api-app (healthy) ──► frontend
db-ml  (healthy) ──► api-ml  (healthy) ──┘
```
