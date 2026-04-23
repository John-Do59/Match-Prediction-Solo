#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Démarrage de l'orchestration manuelle Docker ===${NC}"

# 0. Nettoyage de sécurité
echo -e "${GREEN}[0/6] Nettoyage des anciens conteneurs...${NC}"
./scripts/docker_clean.sh > /dev/null 2>&1 || true

# Vérification des ports occupés par des serveurs locaux (hors Docker)
for port in 8000 8001 8082 5432; do
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
      echo -e "\033[0;31mERREUR : Le port $port est déjà utilisé par un processus local.\033[0m"
      echo "👉 Merci d'arrêter tes terminaux qui font tourner uvicorn, npm ou psql avant de continuer."
      exit 1
  fi
done

# 1. Création du réseau
echo -e "${GREEN}[1/6] Création du réseau 'match-network'...${NC}"
docker network create match-network 2>/dev/null || echo "Le réseau existe déjà."

# 2. Lancement de PostgreSQL avec Volume pour la persistance
echo -e "${GREEN}[2/5] Lancement du conteneur PostgreSQL...${NC}"
docker run -d \
  --name postgres-db \
  --network match-network \
  -v postgres_data:/var/lib/postgresql/data \
  -e POSTGRES_USER=amaury \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=footballapp_db \
  -p 5432:5432 \
  postgres:15

echo "Attente de 5 secondes pour l'initialisation de Postgres..."
sleep 5

# Création de la deuxième base de données (ML) et de test si elles n'existent pas
docker exec -i postgres-db psql -U amaury -d footballapp_db -tc "SELECT 1 FROM pg_database WHERE datname = 'footballml_db'" | grep -q 1 || \
docker exec -i postgres-db psql -U amaury -d footballapp_db -c "CREATE DATABASE footballml_db;"

docker exec -i postgres-db psql -U amaury -d footballapp_db -tc "SELECT 1 FROM pg_database WHERE datname = 'footballapp_app_test'" | grep -q 1 || \
docker exec -i postgres-db psql -U amaury -d footballapp_db -c "CREATE DATABASE footballapp_app_test;"

# 3. Build des images
echo -e "${GREEN}[3/5] Build des images (Backend & Frontend)...${NC}"
docker build -t match-api-app -f FastAPI_App/Dockerfile .
docker build -t match-api-ml -f FastAPI_ML/Dockerfile .
docker build -t match-frontend -f match_prediction_app-front/Dockerfile .

# 4. Lancement des Backend
echo -e "${GREEN}[4/5] Lancement des services Backend...${NC}"

# API Application (Port 8000)
docker run -d \
  --name api-app \
  --network match-network \
  -p 8000:8000 \
  --env-file .env \
  -e DATABASE_URL=postgresql://amaury:password@postgres-db:5432/footballapp_db \
  match-api-app

# API Machine Learning (Port 8001)
docker run -d \
  --name api-ml \
  --network match-network \
  -p 8001:8001 \
  --env-file .env \
  -e DATABASE_ML_URL=postgresql://amaury:password@postgres-db:5432/footballml_db \
  match-api-ml

# 5. Lancement du Frontend
echo -e "${GREEN}[5/5] Lancement du Frontend Vue.js...${NC}"
docker run -d \
  --name frontend-vue \
  --network match-network \
  -p 8082:80 \
  match-frontend

# 6. Post-déploiement : Migrations et Seeds
echo -e "${GREEN}[6/6] Exécution des migrations et chargement des données...${NC}"
docker exec api-app alembic upgrade head
docker exec api-ml alembic upgrade head
docker exec -i postgres-db psql -U amaury -d footballapp_db < Data/seeds/teams_seed.sql

echo -e "${BLUE}=== Architecture déployée avec succès ! ===${NC}"
echo -e "Frontend : http://localhost:8082"
echo -e "API App  : http://localhost:8000/docs"
echo -e "API ML   : http://localhost:8001/docs"
echo -e "Base de données accessible sur le port 5432"
echo -e "${BLUE}==========================================${NC}"
