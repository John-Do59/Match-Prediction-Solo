# Documentation : GitHub Container Registry (GHCR)

Ce document explique l'utilité du GitHub Container Registry (GHCR) pour notre projet **Match-Prediction-Solo** et détaille le plan pour son implémentation.

---

## 1. Qu'est-ce que GHCR ?

Le **GitHub Container Registry (GHCR)** est un service d'hébergement d'images Docker (et d'autres packages) directement intégré à GitHub. Il remplace avantageusement Docker Hub pour les projets hébergés sur GitHub.

### Pourquoi l'utiliser ?

1.  **Intégration Native** : Authentification simplifiée via `GITHUB_TOKEN` dans les GitHub Actions.
2.  **Visibilité et Permissions** : Gestion fine des accès (public/privé) liée à l'organisation ou à l'utilisateur GitHub.
3.  **Performance** : Temps de build et de pull réduits car les images restent dans l'écosystème GitHub.
4.  **Centralisation** : Votre code et vos images de production sont au même endroit.
5.  **Microservices** : Idéal pour stocker séparément les images de nos trois composants : API App, API ML, et Frontend.

---

## 2. Analyse du Projet Actuel

Actuellement, le projet nécessite un build local :
*   `FastAPI_App` -> Image `match-api-app`
*   `FastAPI_ML` -> Image `match-api-ml`
*   `match_prediction_app-front` -> Image `match-frontend`

Le déploiement en production ou sur un nouveau poste nécessite de re-build chaque image, ce qui est chronophage et source d'incohérences (différences de versions de dépendances entre les builds).

---

## 3. Plan d'Implémentation

L'objectif est d'automatiser le build et le push des images vers GHCR à chaque mise à jour de la branche principale (`main`).

### Étape 1 : Création du Workflow GitHub Actions
Créer un fichier `.github/workflows/docker-publish.yml` qui :
*   Se déclenche sur un `push` sur `main`.
*   S'authentifie à `ghcr.io` avec le jeton automatique du repo.
*   Construit les 3 images Docker.
*   Les taggue avec `latest` et le hash du commit.
*   Les pousse sur le registre.

### Étape 2 : Standardisation du Naming des Images
Les images seront nommées selon la convention GHCR :
*   `ghcr.io/john-do59/match-prediction-solo/api-app:latest`
*   `ghcr.io/john-do59/match-prediction-solo/api-ml:latest`
*   `ghcr.io/john-do59/match-prediction-solo/frontend:latest`

### Étape 3 : Mise à jour du `docker-compose.yml`
Créer (ou modifier) une configuration de production qui utilise ces images distantes au lieu de faire un `build` local.
Cela permettra de déployer l'application complète avec une seule commande :
```bash
docker-compose pull && docker-compose up -d
```

### Étape 4 : Gestion des Permissions
Vérifier que le `GITHUB_TOKEN` a les droits d'écriture sur les packages dans les paramètres du repository GitHub.

---

## 4. Bénéfices Attendus

*   **Temps de déploiement réduit** : Plus besoin de build en production.
*   **Fiabilité** : L'image testée en CI est exactement celle qui tourne en production.
*   **Historique** : Possibilité de revenir à une version précédente (rollback) en changeant simplement le tag de l'image.
*   **Professionnalisme** : Utilisation des standards DevOps modernes.
