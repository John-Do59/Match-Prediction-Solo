# Infrastructure Docker Compose (Profiles & Networks)

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

## Réseaux & Isolation

| Réseau | Services | Accès externe |
| :--- | :--- | :--- |
| `frontend-network` | gateway, frontend, api-app, api-ml | Oui (via ports) |
| `backend-network` | api-app, api-ml, db-app, db-ml | **Non** |

> Les bases de données sont **invisibles** depuis l'extérieur. Seules les APIs peuvent y accéder via le réseau privé.

---

## Profils d'Utilisation (Environnements)

L'utilisation des **Docker Profiles** permet de basculer d'un environnement à l'autre proprement.

### 🛠️ Mode Développement (DEV)
```bash
cp .env.dev .env
docker compose --profile dev up --build
```
Le frontend est exposé directement sur le port **8083**.

### 🌍 Mode Production (PROD)
```bash
cp .env.prod .env
docker compose --profile prod up --build
```
Le trafic passe par **Traefik** (SSL activé).

---

## Gestion des Données (Volumes)

-   `postgres_app_data` : Données de l'API principale.
-   `postgres_ml_data` : Données de l'API Machine Learning.

Pour réinitialiser complètement les bases :
```bash
docker compose down -v
```

---

## Gestion des Variables d'Environnement

Le `docker-compose.yml` lit automatiquement le fichier `.env` à la racine.

| Variable | Exemple | Usage |
| :--- | :--- | :--- |
| `DB_USER` | `myuser` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | `secret` | Mot de passe PostgreSQL |
| `DB_NAME` | `footballapp_db` | Base de données API App |
| `DB_ML_NAME` | `footballml_db` | Base de données API ML |

---

## Commandes Essentielles

```bash
# Voir les logs
docker compose logs -f api-app

# Lancer les migrations manuellement
docker compose exec api-app alembic upgrade head
```

---

## Healthchecks & Dépendances

Démarrage ordonné :
`db-app (healthy) ──► api-app (healthy) ──► frontend`
