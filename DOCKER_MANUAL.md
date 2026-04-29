# Guide Docker Modernisé (Compose & Profiles)

Ce projet utilise désormais **Docker Compose** avec des **Profiles** pour gérer les environnements de manière professionnelle et sécurisée.

---

## 1. Préparation de l'Environnement

Le système repose sur un fichier `.env` à la racine.

```bash
# Copier l'un des exemples pour créer votre .env
cp .env.dev .env
```

---

## 2. Commandes de Lancement

Nous n'utilisons plus de scripts shell (`.sh`). Tout passe par `docker compose`.

### 🚀 Mode DÉVELOPPEMENT (Local)
* **Port** : [http://localhost:8083](http://localhost:8083)
* **Accès** : HTTP simple, idéal pour le debug.

```bash
docker compose --profile dev up --build
```

### 🔐 Mode PRODUCTION (Sécurisé)
* **Accès** : [https://localhost](https://localhost) (via Traefik)
* **Sécurité** : HTTPS automatique, DB isolée (non accessible depuis l'hôte).

```bash
docker compose --profile prod up --build
```

---

## 3. Initialisation du Projet (Schémas & Données)

Une fois les conteneurs lancés pour la première fois, vous devez initialiser la base de données :

```bash
# 1. Appliquer les migrations Alembic (Schémas SQL)
docker compose exec api-app alembic upgrade head
docker compose exec api-ml alembic upgrade head

# 2. Charger les référentiels (Équipes)
docker compose exec api-app python -m app.seeds.seed_teams

# 3. Ingestion et Entraînement du modèle ML
curl -X POST http://localhost:8001/ingest
curl -X POST http://localhost:8001/train
```

---

## 4. Gestion et Maintenance

| Action | Commande |
| :--- | :--- |
| **Arrêter proprement** | `docker compose down` |
| **Nettoyage complet** | `docker compose down --remove-orphans -v` (supprime aussi les données) |
| **Voir les logs** | `docker compose logs -f [nom-service]` |
| **Vérifier la santé** | `docker compose ps` |

---

## 5. Architecture de Sécurité (Infrastructure Hardening)

*   **Réseaux Isolés** :
    *   `frontend-network` : Uniquement pour le trafic web.
    *   `backend-network` : Uniquement pour la communication entre APIs et Bases de données.
*   **Traefik (Reverse Proxy)** : Gère le routage et les certificats SSL automatiquement en mode PROD.
*   **Database Hardening** : Les bases de données ne sont plus exposées sur les ports de l'hôte (5432) en mode production. Elles sont uniquement accessibles par les APIs via le réseau interne.
*   **Healthchecks** : Les services attendent que PostgreSQL soit `Healthy` (via `pg_isready`) avant de démarrer, évitant les crashs au boot.

---

## 6. Dépannage (Troubleshooting)

### Port 8083 ou 8080 déjà utilisé ?
Sur Mac, Docker Desktop peut parfois garder des ports réservés.
1. `docker compose down --remove-orphans`
2. Si le problème persiste, changez le port dans le fichier `docker-compose.yml`.

### La DB ne se crée pas ?
Le script d'initialisation `init-db.sql` ne s'exécute **que si le volume est neuf**.
Si vous devez réinitialiser :
`docker compose down -v`
