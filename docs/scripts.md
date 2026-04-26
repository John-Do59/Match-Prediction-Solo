# Guide des Scripts Utilitaires

Ce document détaille l'utilisation et le rôle des scripts Shell (`.sh`) fournis dans le projet pour simplifier le développement et la maintenance.

---

## 🚀 Développement au Quotidien

### `scripts/dev.sh`
C'est le point d'entrée principal pour lancer le projet.
- **Rôle** : Vérifie la présence du fichier `.env` (et le crée si besoin), puis lance la stack complète avec Docker Compose.
- **Usage** : 
  ```bash
  ./scripts/dev.sh
  ```
- **Quand l'utiliser ?** Dès que vous voulez démarrer l'application pour coder ou tester manuellement.

---

## 🧪 Tests & Données

### `scripts/test.sh`
Permet de lancer la suite de tests automatisés.
- **Rôle** : Exécute `pytest` à l'intérieur des conteneurs en cours d'exécution.
- **Usage** : 
  ```bash
  ./scripts/test.sh
  ```
- **Note** : Les services Docker doivent être démarrés pour que ce script fonctionne.

### `scripts/seed_teams.sh`
Initialise la base de données applicative.
- **Rôle** : Exécute le script Python de peuplement des équipes (`seed_teams.py`) à l'intérieur du conteneur `api-app`.
- **Usage** : 
  ```bash
  ./scripts/seed_teams.sh
  ```

---

## 🔧 Maintenance & Infrastructure

### `scripts/docker_clean.sh`
Réinitialise complètement l'environnement Docker.
- **Rôle** : Arrête les services, supprime les conteneurs, les réseaux et surtout les **volumes** (suppression définitive des données en base).
- **Usage** : 
  ```bash
  ./scripts/docker_clean.sh
  ```
- **Quand l'utiliser ?** En cas de bug majeur d'infrastructure ou si vous voulez repartir d'une base de données totalement vierge.

### `scripts/docker-entrypoint.sh` (Interne)
**Attention** : Ce script n'est pas destiné à être lancé manuellement.
- **Rôle** : Il est utilisé par Docker lors du démarrage des conteneurs backends. Il assure que la base de données est prête (`pg_isready`) avant de lancer les migrations Alembic et de démarrer l'application.

---

## 🗄️ Archives (Legacy)

### Dossier `legacy/`
Contient les anciens scripts utilisés avant le passage à Docker Compose (comme `run_docker_env.sh`).
- **Pourquoi les garder ?** Pour conserver un historique de l'évolution de l'infrastructure, mais ils ne doivent plus être utilisés pour le développement actuel.

---

**Astuce** : Si un script refuse de se lancer, assurez-vous qu'il possède les droits d'exécution avec : `chmod +x scripts/*.sh`.
