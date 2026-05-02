# 🚀 Optimisation des Images Docker (Ultra-Light)

Ce document explique pourquoi et comment les images Docker du projet **Match Prediction** ont été optimisées pour passer d'images lourdes (> 1 Go) à des versions "Ultra-Light".

## 1. Pourquoi alléger les images ?

L'optimisation des images Docker n'est pas seulement une question d'espace disque. Elle apporte trois avantages majeurs :

*   **Vitesse (CI/CD & Déploiement)** : Des images plus légères sont poussées (push) vers la GitHub Container Registry (GHCR) et récupérées (pull) beaucoup plus rapidement.
*   **Sécurité (Réduction de la surface d'attaque)** : En utilisant des images `slim` ou `alpine`, on supprime des centaines d'outils et de bibliothèques inutiles (compilateurs, shells, etc.) qui pourraient être exploités par un attaquant.
*   **Performance Runtime** : Moins de fichiers signifie moins de mémoire utilisée par le système de fichiers Docker et un démarrage des conteneurs plus rapide.

---

## 2. Stratégies d'implémentation

Nous avons utilisé quatre piliers pour l'optimisation :

### A. Multi-stage Builds (Construction Multi-étapes)
C'est la technique la plus efficace. Elle consiste à utiliser une image "Builder" pour compiler les dépendances, puis à copier uniquement les fichiers nécessaires dans une image "Runtime" finale.
*   *Exemple :* Le compilateur `gcc` est nécessaire pour installer `psycopg2` (PostgreSQL), mais il est inutile pour faire tourner l'API. On l'utilise dans l'étape 1 et on l'oublie dans l'étape 2.

### B. Images de base Minimalistes
*   **Python (`-slim`)** : Utilisation de `python:3.12-slim` au lieu de `python:3.12`. On économise environ 600 Mo dès le départ.
*   **Nginx/Node (`-alpine`)** : Utilisation de `alpine` (basé sur une distribution Linux de seulement 5 Mo).

### C. Dépendances de Production uniquement
Séparation des fichiers `requirements.txt` (développement) et `requirements.prod.txt` (production). On exclut les outils comme `pytest`, `black`, ou `flake8` de l'image finale.

### D. Nettoyage des caches
Utilisation de `--no-cache-dir` pour `pip` et suppression des listes d'index `apt` après installation :
```dockerfile
RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*
```

---

## 3. Détails par Service

### 🐍 FastAPI (App & ML)
*   **Builder Stage** : Installe `gcc` et `libpq-dev`, installe les packages Python dans `/install` via `--prefix`.
*   **Runtime Stage** : Récupère uniquement `/install` vers `/usr/local`. N'installe que `libpq5` (le strict nécessaire pour communiquer avec Postgres).
*   **Résultat** : Réduction drastique de la taille et amélioration de la sécurité via un utilisateur non-root (`appuser`).

### 🖼️ Frontend (Vue.js)
*   **Builder Stage** : Image `node:18-alpine` pour compiler le code source en fichiers statiques (`npm run build`).
*   **Production Stage** : Image `nginx:stable-alpine`.
*   **Révolution** : Le runtime Node.js (très lourd) est totalement absent de l'image finale. Seuls Nginx et les fichiers HTML/JS/CSS sont présents.

---

## 4. Comparaison (Estimation)

| Service | Image Standard | Image Ultra-Light | Gain |
| :--- | :--- | :--- | :--- |
| **FastAPI App** | ~950 Mo | ~180 Mo | **-80%** |
| **FastAPI ML** | ~1.2 Go | ~450 Mo | **-60%** |
| **Frontend** | ~1.1 Go | ~45 Mo | **-95%** |

---
> [!TIP]
> Ces images optimisées sont automatiquement construites et publiées via le workflow GitHub Actions `.github/workflows/docker-publish.yml`.
