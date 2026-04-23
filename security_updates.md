# Rapport de Sécurisation et Hardening Docker

Ce document récapitule les mesures de sécurité implémentées pour renforcer la protection du backend et de l'infrastructure de déploiement.

## 🛡️ Sécurisation Applicative (FastAPI)

### 1. Politique de Mots de Passe
- **Validation Renforcée** : Ajout d'une logique de validation dans le schéma `UserRegister` (Pydantic).
- **Critères requis** :
    - Longueur minimale de 8 caractères.
    - Présence d'au moins une lettre majuscule.
    - Présence d'au moins une lettre minuscule.
    - Présence d'au moins un chiffre.

### 2. Protection Anti-Brute Force (Rate Limiting)
- **Outil** : Utilisation de `SlowAPI` (basé sur limits).
- **Configuration** :
    - Un limiteur global est initialisé dans `app/core/limiter.py`.
    - Les routes d'authentification (`/auth/login` et `/auth/register`) sont limitées à **5 requêtes par minute** par adresse IP.
    - Un gestionnaire d'exception global a été ajouté dans `main.py` pour renvoyer une erreur `429 Too Many Requests` propre.

### 3. Gestion des Secrets et Emails
- **Secret Key** : La variable `SECRET_KEY` (JWT) est désormais obligatoire. L'application ne démarre pas si elle est absente ou vide (Fail-Fast).
- **Réinitialisation de mot de passe** : Intégration du service **Resend** pour l'envoi d'emails réels.
- **Sécurité Dev** : En mode développement (sans clé API), le lien de réinitialisation est affiché dans les logs du serveur de manière sécurisée.

---

## 🐳 Hardening de l'Infrastructure Docker

### 1. Exécution Non-Root
Pour respecter les bonnes pratiques de sécurité (Least Privilege), les conteneurs ne s'exécutent plus en tant que `root`.

- **Backends (App & ML)** :
    - Création d'un utilisateur système `appuser`.
    - Changement de propriétaire des fichiers (`chown`) vers `appuser`.
    - Utilisation de l'instruction `USER appuser` dans le Dockerfile.
- **Frontend (Nginx)** :
    - Migration du port interne de **80** vers **8080** (les ports < 1024 nécessitent les droits root).
    - Exécution sous l'utilisateur `nginx`.
    - Ajustement des permissions sur `/var/cache/nginx` et `/var/run/nginx.pid`.

### 2. Orchestration de Déploiement
- Le script `scripts/run_docker_env.sh` a été mis à jour pour mapper le port externe **8082** vers le nouveau port interne **8080**.
- Suppression des résidus de fichiers sensibles dans les conteneurs via `.dockerignore`.

---

## 🚀 Comment vérifier ?

1. **Test Rate Limit** : Tentez de vous connecter 6 fois de suite rapidement. Vous recevrez une erreur `429`.
2. **Test Mot de Passe** : Essayez de créer un compte avec "123456". La validation Pydantic bloquera la requête avec une erreur `422`.
3. **Test Docker User** :
   ```bash
   docker exec -it api-app whoami
   # Devrait retourner : appuser
   ```

---
*Dernière mise à jour : 23 Avril 2026*
