#!/bin/bash

# Couleurs
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}=== Nettoyage complet de l'environnement Match Prediction App ===${NC}"

# 1. Utilisation de Docker Compose pour un arrêt propre
echo "Arrêt des services et suppression des volumes avec Docker Compose..."
docker-compose down -v --remove-orphans

# 2. Nettoyage des anciennes images non utilisées (optionnel mais recommandé)
echo "Suppression des images inutilisées..."
docker image prune -f

# 3. Suppression des conteneurs orphelins (sécurité supplémentaire)
# On cherche les conteneurs qui pourraient être restés de l'ancienne orchestration
echo "Recherche de conteneurs résiduels..."
docker stop frontend-vue api-app api-ml postgres-db 2>/dev/null
docker rm frontend-vue api-app api-ml postgres-db 2>/dev/null

echo -e "${RED}=== Nettoyage terminé. L'environnement est comme neuf. ===${NC}"
