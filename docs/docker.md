# Docker — Architecture & Bonnes Pratiques (Hardened)

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

## Sécurité & Hardening

1.  **Utilisateur Non-Root** :
    ```dockerfile
    RUN adduser --disabled-password --gecos "" appuser \
        && chown -R appuser:appuser /app
    USER appuser
    ```
    Si un attaquant compromet l'application, il n'a pas les droits root sur le système hôte.

2.  **Scan de Vulnérabilités** : Intégration de **Trivy** dans la CI/CD pour bloquer les CVE critiques (CRITICAL/HIGH).

3.  **Images de Base** : Utilisation de `python:3.12-slim` et `nginx:stable-alpine`.

4.  **Isolation Réseau** : Les bases de données sont placées sur un réseau privé (`backend-network`) et ne sont pas exposées sur l'hôte.

---

## Optimisation du Cache Docker

L'ordre des instructions est optimisé (du moins fréquent au plus fréquent) :

```dockerfile
# ✅ BON : requirements AVANT le code source
COPY requirements.prod.txt .
RUN pip install ...       ← layer caché si requirements ne change pas

COPY FastAPI_App/ .       ← invalidé seulement si le code change
```

---

## .dockerignore

Le fichier `.dockerignore` exclut : `.git/`, `__pycache__/`, `node_modules/`, et surtout les fichiers `.env*` pour éviter les fuites de secrets.

---

## Healthchecks

Chaque service déclare un healthcheck. Les services dépendants utilisent `condition: service_healthy` pour un démarrage ordonné.
