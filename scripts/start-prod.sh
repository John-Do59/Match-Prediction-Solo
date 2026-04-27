#!/bin/bash
# Lancement de l'environnement PROD (AVEC SSL)

echo "🔒 Lancement de Match Prediction App en mode PROD..."

# Vérification SSL
if [ ! -d "ssl" ]; then
    echo "❌ Erreur: Dossier 'ssl' manquant. Lancez ./scripts/generate_ssl.sh d'abord."
    exit 1
fi

# 1. Nettoyage
docker stop frontend-vue api-app api-ml postgres-db 2>/dev/null
docker rm frontend-vue api-app api-ml postgres-db 2>/dev/null
docker network rm match-network 2>/dev/null

# 2. Réseau
docker network create match-network

# 3. Base de données
docker run -d \
  --name postgres-db \
  --network match-network \
  -v postgres_data:/var/lib/postgresql/data \
  -e POSTGRES_USER=amaury \
  -e POSTGRES_PASSWORD=secure-password-prod \
  -e POSTGRES_DB=footballapp_db \
  -p 5432:5432 \
  postgres:15

sleep 5
docker exec -it postgres-db psql -U amaury -d footballapp_db -c "CREATE DATABASE footballml_db;"

# 4. Build
docker build -t match-api-app -f FastAPI_App/Dockerfile .
docker build -t match-api-ml -f FastAPI_ML/Dockerfile .
docker build -t match-frontend -f match_prediction_app-front/Dockerfile .

# 5. Run Services
docker run -d \
  --name api-app \
  --network match-network \
  -p 8000:8000 \
  --env-file .env.prod \
  -e ENV=prod \
  match-api-app

docker run -d \
  --name api-ml \
  --network match-network \
  -p 8001:8001 \
  --env-file .env.prod \
  -e ENV=prod \
  match-api-ml

docker run -d \
  --name frontend-vue \
  --network match-network \
  -v "$(pwd)/ssl:/etc/nginx/ssl:ro" \
  -p 8082:8080 \
  -p 8443:8443 \
  -e ENV=prod \
  match-frontend

echo "✅ Environnement PROD prêt !"
echo "Frontend (HTTPS): https://localhost:8443"
echo "API App: http://localhost:8000/docs"
echo "API ML: http://localhost:8001/docs"
