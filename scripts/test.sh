#!/bin/bash

# Script pour lancer les tests dans les conteneurs
echo "🧪 Lancement des tests unitaires..."

echo "--- [API APP] ---"
docker exec match-api-app pytest tests/

echo ""
echo "--- [API ML] ---"
docker exec match-api-ml pytest tests_ml/
