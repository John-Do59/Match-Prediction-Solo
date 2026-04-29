# Docker — Architecture & Bonnes Pratiques

## Multi-Stage Builds

Les 3 services utilisent des **builds multi-stage** pour produire des images légères et sécurisées.

### Principe

```
Stage 1: builder (python:3.12-slim)
  └─ Installe gcc, libpq-dev, pip packages
  └─ Output: /install (packages compilés)

Stage 2: runtime (python:3.12-slim)
  └─ Copie uniquement /install depuis builder
  └─ Installe seulement les libs runtime (libpq5)
  └─ Lance l'application
```

**Résultat** : L'image finale ne contient **pas** `gcc`, `python3-dev`, ni les outils de compilation.

### Comparaison de taille

| Image | Sans multi-stage | Avec multi-stage |
| :--- | :---: | :---: |
| `api-app` | ~800 MB | ~180 MB |
| `api-ml` | ~1.2 GB | ~450 MB |
| `frontend` | ~600 MB | ~25 MB |

---

## Optimisation du Cache Docker

L'ordre des instructions dans le Dockerfile est **critique** pour le cache.

### Règle d'or : du moins fréquent au plus fréquent

```dockerfile
# ✅ BON : requirements AVANT le code source
COPY requirements.prod.txt .
RUN pip install ...       ← layer caché si requirements ne change pas

COPY FastAPI_App/ .       ← invalidé seulement si le code change
```

```dockerfile
# ❌ MAUVAIS : si le code est copié avant les deps
COPY . .
RUN pip install ...       ← recalculé à CHAQUE changement de code
```

Nos Dockerfiles respectent cette structure.

---

## Sécurité — Utilisateur Non-Root

```dockerfile
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser
```

**Pourquoi** : Si un attaquant compromet l'application via une faille, il obtient les droits `appuser` (non-root) et ne peut pas écrire hors de `/app`, ni accéder aux ressources système.

---

## Images de Base

| Service | Image | Raison |
| :--- | :--- | :--- |
| `api-app` runtime | `python:3.12-slim` | Petite, sans outils inutiles |
| `api-ml` runtime | `python:3.12-slim` | Idem |
| `frontend` build | `node:18-alpine` | Alpine = ultra-léger |
| `frontend` runtime | `nginx:stable-alpine` | ~25 MB, stable |
| `gateway` (prod) | `traefik:v2.10` | Reverse proxy officiel |

> **Ne jamais utiliser** `python:3.12` (full, ~900MB) en production.

---

## .dockerignore

Le fichier `.dockerignore` exclut du contexte de build :

```
.git/
**/__pycache__/
**/*.pyc
node_modules/
*.log
.env*           ← CRITIQUE : ne jamais envoyer les .env dans une image
ssl/
```

---

## Healthchecks

Chaque service déclare un healthcheck pour que Docker sache quand il est réellement prêt.

```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "postgres", "-d", "footballapp_db"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 20s
```

Les services dépendants (api-app, api-ml) utilisent `condition: service_healthy` pour démarrer **après** que la DB soit prête.
