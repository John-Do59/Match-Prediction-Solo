#!/bin/bash

# Script pour lancer l'environnement de développement
echo "🚀 Lancement de l'environnement Match Prediction App..."

# Vérifie si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env introuvable ! Copie de .env.example..."
    cp .env.example .env
fi

# Redirige vers le nouveau script de démarrage DEV
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
