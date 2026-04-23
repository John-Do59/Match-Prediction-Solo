#!/bin/bash

# Couleurs
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}=== Nettoyage complet de l'environnement Docker ===${NC}"

# Arrêt et suppression des conteneurs
echo "Arrêt des conteneurs..."
docker stop frontend-vue api-app api-ml postgres-db 2>/dev/null
echo "Suppression des conteneurs..."
docker rm frontend-vue api-app api-ml postgres-db 2>/dev/null

# Suppression du réseau
echo "Suppression du réseau 'match-network'..."
docker network rm match-network 2>/dev/null

echo -e "${RED}=== Nettoyage terminé ===${NC}"
