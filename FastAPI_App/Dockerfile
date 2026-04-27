FROM python:3.12-slim as base

WORKDIR /app

# Installation des dépendances système nécessaires (psycopg2 + netcat pour le wait-for-it)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# On copie d'abord les requirements pour profiter du cache Docker
COPY FastAPI_App/requirements.txt /app/FastAPI_App/requirements.txt
RUN pip install --no-cache-dir -r /app/FastAPI_App/requirements.txt

# Copie du dossier partagé
COPY shared/ /app/shared/

# Copie du code de l'application et des scripts
COPY FastAPI_App/ /app/FastAPI_App/
COPY scripts/docker-entrypoint.sh /app/scripts/docker-entrypoint.sh
RUN chmod +x /app/scripts/docker-entrypoint.sh

# On se place dans le dossier de l'app pour le démarrage
WORKDIR /app/FastAPI_App

# Exposition du port par défaut
EXPOSE 8000

# Création d'un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Utilisation de l'entrypoint pour les migrations automatiques
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Commande de démarrage par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
