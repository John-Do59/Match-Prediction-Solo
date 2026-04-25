# Architecture d'Orchestration : Docker Compose

Ce document détaille l'implémentation de Docker Compose dans le projet **Match Prediction App**, expliquant les choix d'architecture et le fonctionnement interne du système.

---

## 1. Schéma Mental de l'Architecture

Voici comment les services interagissent entre eux :

```mermaid
graph TD
    User((Utilisateur)) -->|HTTPS/8443| Frontend[match-frontend]
    Frontend -->|Proxy /api/v1| API_App[match-api-app]
    Frontend -->|Proxy /ml/v1| API_ML[match-api-ml]
    
    API_App -->|SQL| DB_App[(match-db-app)]
    API_App -->|HTTP| API_ML
    
    API_ML -->|SQL| DB_ML[(match-db-ml)]
    API_ML -->|Volume| Data[./Data]
```

---

## 2. Philosophie : Database-per-service (Découplage)

Nous utilisons une approche **Database-per-service**. Chaque microservice possède sa propre instance PostgreSQL isolée.

### Pourquoi ce choix ?

- **Isolation des pannes** : Une saturation du service ML n'impacte pas l'authentification des utilisateurs.
- **Maintenance Indépendante** : Possibilité de mettre à jour les versions de base de données séparément.
- **Zéro Script Custom** : Pas besoin de scripts complexes pour créer plusieurs bases dans une seule instance.

---

## 3. Pourquoi Docker Compose plutôt que des scripts Shell ?

Passer de `run_docker_env.sh` à `docker-compose.yml` est une montée en gamme technique :

| Caractéristique | Script Shell | Docker Compose |
| :--- | :--- | :--- |
| **Paradigme** | Impératif (fait ceci, puis cela) | Déclaratif (voici l'état souhaité) |
| **Gestion des erreurs** | Complexe et manuelle | Native (restarts, healthchecks) |
| **Réseau** | Création manuelle requise | Réseau par défaut automatique |
| **Idempotence** | Difficile à garantir | Native (ne recrée que ce qui a changé) |
| **CI/CD** | Difficile à intégrer | Standard de l'industrie |

---

## 4. Le Cycle de Démarrage (Orchestration Robuste)

### Healthchecks Postgres

Nous utilisons l'outil natif `pg_isready` pour garantir que Postgres est prêt :

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
```

### L'Entrypoint Intelligent (`docker-entrypoint.sh`)

Chaque API utilise un script de démarrage qui :

1. **Vérifie la disponibilité** : Utilise `pg_isready` pour attendre que SA base spécifique soit prête.
2. **Auto-Migrations** : Lance `alembic upgrade head` avant le démarrage de l'application.

### Healthchecks Applicatifs

En plus des bases de données, les APIs disposent de leur propre monitoring Docker :

- **Endpoint** : `/health`
- **Mécanisme** : Docker exécute un `curl` toutes les 30 secondes. Si l'API ne répond plus (deadlock, crash), Docker le détecte et peut tenter une action de récupération.

---

## 5. Sécurité Inter-Services

Dans une architecture pro, on ne laisse pas les APIs ouvertes, même en réseau interne.

- **Service Token** : Une clé partagée (`SERVICE_TOKEN`) est exigée par l'API ML pour chaque requête provenant de l'API App (via le header `X-Service-Token`).
- **Isolation** : Cela garantit que seul votre backend légitime peut solliciter le moteur de prédiction.

---

## 6. Réseautage et Communication

### Résolution de noms

Les services communiquent via leurs noms de services définis dans le Compose.
Format de l'URL PostgreSQL :
`postgresql://USER:PASSWORD@HOST:PORT/DB_NAME`

*Exemple pour l'API App* : `postgresql://amaury:password@db-app:5432/footballapp_db`

### Nginx en Reverse Proxy

Le conteneur `frontend` joue le rôle de point d'entrée unique. Il gère la terminaison SSL et redirige les requêtes vers les bons backends, isolant ainsi les APIs du monde extérieur.

---

## 6. Commandes Utiles

| Action | Commande |
| :--- | :--- |
| **Démarrer tout** | `docker-compose up --build` |
| **Arrêter tout** | `docker-compose down` |
| **Réinitialiser les DB** | `docker-compose down -v` |

---

**Conclusion** : Cette architecture transforme le projet en un système microservices crédible, aligné sur les meilleures pratiques d'infrastructure actuelles.
