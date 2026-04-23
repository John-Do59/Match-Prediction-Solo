FROM python:3.12-slim as base

WORKDIR /app

# Installation des dépendances système nécessaires pour psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# On copie d'abord les requirements pour profiter du cache Docker
COPY FastAPI_App/requirements.txt /app/FastAPI_App/requirements.txt
RUN pip install --no-cache-dir -r /app/FastAPI_App/requirements.txt

# Copie du dossier partagé (nécessite un build depuis la racine : docker build -f FastAPI_App/Dockerfile .)
COPY shared/ /app/shared/

# Copie du code de l'application
COPY FastAPI_App/ /app/FastAPI_App/

# On se place dans le dossier de l'app pour le démarrage
WORKDIR /app/FastAPI_App

# Exposition du port par défaut
EXPOSE 8000

# Commande de démarrage (L'hôte 0.0.0.0 est crucial pour Docker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
