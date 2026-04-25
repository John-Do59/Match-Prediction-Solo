# Architecture d'Orchestration : Docker Compose

Ce document détaille l'implémentation de Docker Compose dans le projet **Match Prediction App**, expliquant les choix d'architecture et le fonctionnement interne du système.

---

## 1. Philosophie : Database-per-service

Contrairement à l'approche initiale (une seule instance Postgres avec plusieurs bases), nous avons migré vers un modèle **Database-per-service**. 

### Pourquoi ce choix ?
- **Isolation Totale** : Une corruption ou une saturation de la base ML (très sollicitée par les ingestions de données) n'impactera jamais la base Applicative (gestion des utilisateurs et de l'authentification).
- **Maintenance Indépendante** : Chaque service peut être redémarré ou mis à jour séparément.
- **Scalabilité** : Chaque instance Postgres possède son propre volume et ses propres ressources système.

### Implémentation
- `match-db-app` : Dédiée à l'API principale (Users, Auth, History).
- `match-db-ml` : Dédiée à l'IA (Matches, Stats, Predictions).

---

## 2. Le Cycle de Démarrage (Orchestration Robuste)

L'un des plus grands défis en Docker est de s'assurer qu'une application ne démarre pas avant que sa base de données ne soit prête.

### Healthchecks Postgres
Dans le fichier `docker-compose.yml`, nous utilisons des tests de santé (`healthcheck`) :
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
  interval: 5s
  timeout: 5s
  retries: 5
```
Cela permet à Docker Compose de savoir exactement quand le serveur Postgres accepte des connexions.

### Dépendances intelligentes
Les APIs utilisent la condition `service_healthy` :
```yaml
depends_on:
  db-app:
    condition: service_healthy
```

### L'Entrypoint Automatisé (`docker-entrypoint.sh`)
Chaque API utilise un script de démarrage qui réalise deux actions critiques avant de lancer l'application :
1. **Wait-for-it** : Utilise `nc` (netcat) pour vérifier que le port 5432 est bien ouvert sur l'hôte cible (`db-app` ou `db-ml`).
2. **Auto-Migrations** : Lance `alembic upgrade head` pour garantir que le schéma de la base est toujours synchronisé avec le code Python.

---

## 3. Gestion des Volumes et Persistance

Nous utilisons deux types de volumes dans cette architecture :

### Volumes Nommés (Persistance)
- `postgres_app_data` & `postgres_ml_data` : Ces volumes sont gérés par Docker. Ils garantissent que vos données (utilisateurs, matchs entraînés) ne sont pas supprimées même si vous supprimez les conteneurs.

### Bind Mounts (Partage de données)
- `./Data:/app/Data:ro` : Le dossier `Data/` de votre machine est monté dans l'image ML en **lecture seule**. Cela permet à l'IA d'accéder aux CSV sans les copier dans l'image (gain de place et de temps de build).
- `./ssl:/etc/nginx/ssl:ro` : Partage des certificats SSL avec le serveur Nginx.

---

## 4. Réseautage et Communication

Tous les services sont connectés au réseau `match-network`. 

### Résolution de noms
À l'intérieur du réseau Docker, vous n'utilisez plus d'adresses IP ou `localhost`. Vous appelez les services par leur nom défini dans le Compose :
- L'API App contacte la DB via `postgresql://.../db-app:5432`.
- L'API App contacte l'IA via `http://api-ml:8001`.

---

## 5. Commandes Utiles

| Action | Commande |
| :--- | :--- |
| **Démarrer tout** | `docker-compose up --build` |
| **Arrêter tout** | `docker-compose down` |
| **Voir les logs** | `docker-compose logs -f [nom-service]` |
| **Réinitialiser les DB** | `docker-compose down -v` (Attention : supprime les données) |

---

**Conclusion** : Cette architecture transforme le projet en un système prêt pour la production, où chaque composant est isolé, auto-réparable et facile à déployer.
