# Guide des Commandes Manuelles Docker

Ce guide vous permet de reconstruire et de lancer l'intégralité de l'infrastructure **Match Prediction App** étape par étape, sans utiliser les scripts d'automatisation.

---

## 1. Nettoyage initial
Avant de commencer, assurez-vous qu'aucun ancien conteneur ou réseau ne porte le même nom.

```bash
# Arrêter et supprimer les conteneurs s'ils existent
docker stop frontend-vue api-app api-ml postgres-db 2>/dev/null
docker rm frontend-vue api-app api-ml postgres-db 2>/dev/null

# Supprimer le réseau
docker network rm match-network 2>/dev/null
```

---

## 2. Infrastructure (Réseau & SSL)

### Création du réseau
C'est ce qui permet aux conteneurs de communiquer entre eux via leurs noms.
```bash
docker network create match-network
```

### Génération des certificats SSL (Une seule fois)
Si vous n'avez pas de dossier `ssl/` avec des fichiers `.pem`, lancez :
```bash
chmod +x scripts/generate_ssl.sh
./scripts/generate_ssl.sh
```

---

## 3. Base de Données (PostgreSQL)

### Lancer le conteneur
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

### Créer les bases de données secondaires
Attendez 5 secondes que Postgres démarre, puis créez la base ML et la base de Test :
```bash
docker exec -it postgres-db psql -U amaury -d footballapp_db -c "CREATE DATABASE footballml_db;"
docker exec -it postgres-db psql -U amaury -d footballapp_db -c "CREATE DATABASE footballapp_app_test;"
```

---

## 4. Construction des Images (Build)
Exécutez ces commandes depuis la **racine** du projet.

```bash
# Image API Application
docker build -t match-api-app -f FastAPI_App/Dockerfile .

# Image API Machine Learning
docker build -t match-api-ml -f FastAPI_ML/Dockerfile .

# Image Frontend (Nginx + Vue)
docker build -t match-frontend -f match_prediction_app-front/Dockerfile .
```

---

## 5. Lancement des Services (Run)

### API Application (Port 8000)
```bash
docker run -d \
  --name api-app \
  --network match-network \
  -p 8000:8000 \
  --env-file .env \
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
  -e DATABASE_ML_URL=postgresql://amaury:password@postgres-db:5432/footballml_db \
  match-api-ml
```

### Frontend Vue.js (HTTP 8082 / HTTPS 8443)
```bash
docker run -d \
  --name frontend-vue \
  --network match-network \
  -v "$(pwd)/ssl:/etc/nginx/ssl:ro" \
  -p 8082:8080 \
  -p 8443:8443 \
  match-frontend
```

---

## 6. Initialisation des Données & ML

### Migrations et Seeds
```bash
# Appliquer les schémas SQL
docker exec api-app alembic upgrade head
docker exec api-ml alembic upgrade head

# Charger les équipes
docker exec api-app python -m app.seeds.seed_teams
```

### Ingestion et Entraînement du Modèle
```bash
# Ingestion des données CSV
curl -X POST http://localhost:8001/ingest

# Entraînement initial du modèle ML
curl -X POST http://localhost:8001/train
```

---

## 7. Vérification
*   **Frontend (HTTPS)** : [https://localhost:8443](https://localhost:8443)
*   **Documentation API App** : [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Documentation API ML** : [http://localhost:8001/docs](http://localhost:8001/docs)
