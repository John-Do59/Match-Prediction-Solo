#!/bin/bash

# Script pour lancer l'environnement de développement
echo "🚀 Lancement de l'environnement Match Prediction App..."

# Vérifie si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env introuvable ! Copie de .env.example..."
    cp .env.example .env
fi

# Lance Docker Compose
docker-compose up --build
