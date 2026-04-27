#!/bin/bash

# Script pour lancer les tests dans les conteneurs
echo "🧪 Lancement des tests unitaires..."

echo "--- [API APP] ---"
docker exec api-app pytest tests/

echo ""
echo "--- [API ML] ---"
docker exec api-ml pytest tests_ml/
