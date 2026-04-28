#!/bin/bash
# Lancement de l'environnement DEV (SANS SSL)

echo "🚀 Lancement de Match Prediction App en mode DEV..."

# 1. Nettoyage
docker stop frontend-vue api-app api-ml postgres-db 2>/dev/null
docker rm frontend-vue api-app api-ml postgres-db 2>/dev/null
docker network rm match-network 2>/dev/null

# 2. Réseau
docker network create match-network

# 3. Base de données
# Utilisation du volume init-db.sql pour créer les bases secondaires automatiquement
docker run -d \
  --name postgres-db \
  --network match-network \
  -v match_prediction_pg_data:/var/lib/postgresql/data \
  -v "$(pwd)/scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql" \
  --env-file .env.dev \
  -p 5432:5432 \
  postgres:15

echo "⏳ Attente du démarrage de PostgreSQL..."
sleep 5

# 4. Build (Optionnel si déjà fait, mais recommandé pour DEV)
docker build -t match-prediction-app:ultra-light -f FastAPI_App/Dockerfile .
docker build -t match-prediction-ml:ultra-light -f FastAPI_ML/Dockerfile .
docker build -t match-frontend:ultra-light -f match_prediction_app-front/Dockerfile .

# 5. Run Services
docker run -d \
  --name api-app \
  --network match-network \
  -p 8000:8000 \
  --env-file .env.dev \
  -e ENV=dev \
  match-prediction-app:ultra-light

docker run -d \
  --name api-ml \
  --network match-network \
  -p 8001:8001 \
  --env-file .env.dev \
  -e ENV=dev \
  match-prediction-ml:ultra-light

docker run -d \
  --name frontend-vue \
  --network match-network \
  -p 8082:8080 \
  -e ENV=dev \
  match-frontend:ultra-light

echo "✅ Environnement DEV prêt !"
echo "Frontend: http://localhost:8082"
echo "API App: http://localhost:8000/docs"
echo "API ML: http://localhost:8001/docs"
