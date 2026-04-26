#!/bin/bash

# Script pour peupler la base de données avec les équipes initiales
echo "🌱 Initialisation des données (teams)..."

docker exec match-api-app python -m app.seeds.seed_teams
