# Guide d'utilisation Docker sans Docker Compose

Ce guide explique comment lancer manuellement les conteneurs du projet **Match Prediction App**. Cette méthode est utile pour le débogage ou si vous ne souhaitez pas utiliser Docker Compose.

---

## 1. Préparation de l'Infrastructure

### Création du réseau Docker

Pour que les conteneurs puissent communiquer entre eux par leur nom :

```bash
docker network create match-network
```

### Génération des certificats SSL (si nécessaire)

Si vous n'avez pas encore généré les certificats pour Nginx :

```bash
chmod +x scripts/generate_ssl.sh
./scripts/generate_ssl.sh
```

---

## 2. Base de Données (PostgreSQL)

Nous utilisons un seul conteneur Postgres pour toutes les bases de données afin de simplifier la gestion manuelle.

```bash
docker run -d \
  --name postgres-db \
  --network match-network \
  -v postgres_data:/var/lib/postgresql/data \
  -e POSTGRES_USER=amaury \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=footballapp_db \
  -p 5432:5432 \
  postgres:15
```

Attendez quelques secondes, puis créez la base de données pour le Machine Learning :

```bash
docker exec -it postgres-db psql -U amaury -d footballapp_db -c "CREATE DATABASE footballml_db;"
```

---

## 3. Construction des Images (Build)

Lancez ces commandes depuis la racine du projet :

```bash
# Image API Application
docker build -t match-api-app -f FastAPI_App/Dockerfile .

# Image API Machine Learning
docker build -t match-api-ml -f FastAPI_ML/Dockerfile .

# Image Frontend (Nginx)
docker build -t match-frontend -f match_prediction_app-front/Dockerfile .
```

---

## 4. Lancement des Services (Run)

> [!IMPORTANT]
> Les conteneurs utilisent un script d'entrée (`entrypoint.sh`) qui vérifie la présence des variables `DB_HOST`, `DB_USER` et `DB_NAME` avant de démarrer.

### API Application (Port 8000)

```bash
docker run -d \
  --name api-app \
  --network match-network \
  -p 8000:8000 \
  --env-file .env \
  -e DB_HOST=postgres-db \
  -e DB_USER=amaury \
  -e DB_NAME=footballapp_db \
  -e DATABASE_URL=postgresql://amaury:password@postgres-db:5432/footballapp_db \
  match-api-app
```

### API Machine Learning (Port 8001)

```bash
docker run -d \
  --name api-ml \
  --network match-network \
  -p 8001:8001 \
  --env-file .env \
  -e DB_HOST=postgres-db \
  -e DB_USER=amaury \
  -e DB_NAME=footballml_db \
  -e DATABASE_ML_URL=postgresql://amaury:password@postgres-db:5432/footballml_db \
  match-api-ml
```

### Frontend Vue.js (Port 8082 / 8443)

```bash
docker run -d \
  --name frontend-vue \
  --network match-network \
  -v "$(pwd)/ssl:/etc/nginx/ssl:ro" \
  -p 8082:8080 \
  -p 8443:8443 \
  match-frontend

> [!TIP]
> **Astuce rapide (sans SSL)** : Si vous voulez tester rapidement sans configurer les certificats, vous pouvez lancer le frontend uniquement sur le port 8080 :
> ```bash
> docker run -d --name frontend-vue --network match-network -p 8082:8080 match-frontend
> ```
```

---

## 5. Initialisation et Vérification

### Migrations et Données

Les migrations Alembic sont exécutées automatiquement au démarrage des conteneurs grâce à l'entrypoint.

Pour charger les données initiales (équipes) :

```bash
docker exec api-app python -m app.seeds.seed_teams
```

### Ingestion et Entraînement ML

```bash
# Ingestion des données CSV
curl -X POST http://localhost:8001/ingest

# Entraînement initial
curl -X POST http://localhost:8001/train
```

### Accès

* **Application Web (HTTPS)** : [https://localhost:8443](https://localhost:8443)
* **Application Web (HTTP)** : [http://localhost:8082](http://localhost:8082)
* **Documentation API App** : [http://localhost:8000/docs](http://localhost:8000/docs)
* **Documentation API ML** : [http://localhost:8001/docs](http://localhost:8001/docs)

---

> [!NOTE]
> **Mentalité DevOps** : Ne jamais supprimer une configuration fonctionnelle, mais la rendre optionnelle ou configurable (Dev/Staging/Prod).
