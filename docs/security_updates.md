# Rapport de Sécurisation et Hardening Docker

Ce document récapitule les mesures de sécurité implémentées pour renforcer la protection du backend et de l'infrastructure de déploiement.

## Sécurisation Applicative (FastAPI)

### 1. Politique de Mots de Passe

- **Validation Renforcée** : Ajout d'une logique de validation dans le schéma `UserRegister` (Pydantic).
- **Critères requis** :
  - Longueur minimale de 8 caractères.
  - Présence d'au moins une lettre majuscule.
  - Présence d'au moins une lettre minuscule.
  - Présence d'au moins un chiffre.

### Protection Anti-Brute Force (Rate Limiting)

- **Outil** : Utilisation de `SlowAPI` (basé sur limits).
- **Configuration** :
  - Un limiteur global est initialisé dans `app/core/limiter.py`.
  - Les routes d'authentification (`/auth/login` et `/auth/register`) sont limitées à **5 requêtes par minute** par adresse IP.
  - Un gestionnaire d'exception global a été ajouté dans `main.py` pour renvoyer une erreur `429 Too Many Requests` propre.

### Gestion des Secrets et Emails

- **Secret Key** : La variable `SECRET_KEY` (JWT) est désormais obligatoire. L'application ne démarre pas si elle est absente ou vide (Fail-Fast).
- **Réinitialisation de mot de passe** : Intégration du service **Resend** pour l'envoi d'emails réels.
- **Sécurité Dev** : En mode développement (sans clé API), le lien de réinitialisation est affiché dans les logs du serveur de manière sécurisée.

### Observabilité Sécurisée (Logging)

- **Format JSON** : En production, les logs sont générés au format JSON structuré. Cela facilite l'analyse par des outils tiers (SIEM, ELK) sans exposer de données sensibles via des `print` non contrôlés.
- **Contextualisation** : Chaque log contient le nom du service et le niveau de sévérité, permettant un traçage précis des incidents.

---

## Hardening de l'Infrastructure Docker

### Exécution Non-Root

Pour respecter les bonnes pratiques de sécurité (Least Privilege), les conteneurs ne s'exécutent plus en tant que `root`.

- **Backends (App & ML)** :
  - Création d'un utilisateur système `appuser`.
  - Changement de propriétaire des fichiers (`chown`) vers `appuser`.
  - Utilisation de l'instruction `USER appuser` dans le Dockerfile.
- **Frontend (Nginx)** :
  - Migration du port interne de **80** vers **8080** (les ports < 1024 nécessitent les droits root).
  - Exécution sous l'utilisateur `nginx`.
  - Ajustement des permissions sur `/var/cache/nginx` et `/var/run/nginx.pid`.

### Orchestration et Chiffrement

- **HTTPS/SSL** : Tout le trafic frontend est désormais chiffré via SSL (TLS 1.2+).
- **Redirection Forcée** : Le port HTTP (8080) redirige systématiquement vers le port HTTPS (8443).
- **HSTS** : Activation de l'en-tête `Strict-Transport-Security` pour empêcher les attaques de type "downgrade".
- **Isolation** : Les certificats sont montés via des volumes `ro` (read-only) pour que le conteneur ne puisse pas les modifier.

---

## Sécurisation des Secrets et Multi-Environnement

### 1. Centralisation des Identifiants de Base de Données

Afin d'éviter que des credentials ne soient exposés dans l'historique des commandes shell (`ps -aux`, `docker inspect` ou historique bash), nous avons centralisé toute la configuration sensible.

- **Fichiers `.env`** : Les variables `POSTGRES_USER`, `POSTGRES_PASSWORD` et `POSTGRES_DB` sont désormais stockées exclusivement dans `.env.dev` et `.env.prod`.
- **Injection Propre** : Utilisation de `docker run --env-file <file>`. Cette méthode est préférable au passage de variables via `-e` car elle ne laisse pas de trace dans la liste des processus du système hôte.

### 2. Gestion des Environnements (Isolation)

- **Mode DEV** : Utilise `.env.dev`, expose les services sur les ports standards (8000, 8001, 8082) en HTTP.
- **Mode PROD** : Utilise `.env.prod`, force l'usage de HTTPS (8443) et utilise des secrets renforcés.

### 3. Protection contre les Injections de Secrets dans les Images

- **.dockerignore** : Les fichiers `.env`, `.env.dev` et `.env.prod` sont systématiquement ignorés lors du build. Les secrets ne sont **jamais** intégrés à l'image statique. Ils sont fournis dynamiquement au conteneur lors de son démarrage.

---
*Dernière mise à jour : 28 Avril 2026*
