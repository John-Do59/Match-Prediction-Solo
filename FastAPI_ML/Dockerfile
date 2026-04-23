FROM python:3.12-slim as base

WORKDIR /app

# Installation des dépendances système (gcc est nécessaire pour certaines compilations scikit-learn/pandas)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements
COPY FastAPI_ML/requirements.txt /app/FastAPI_ML/requirements.txt
RUN pip install --no-cache-dir -r /app/FastAPI_ML/requirements.txt

# Copie du dossier partagé
COPY shared/ /app/shared/

# Copie du code de l'application
COPY FastAPI_ML/ /app/FastAPI_ML/
COPY Data/ /app/Data/

# On se place dans le dossier de l'app ML
WORKDIR /app/FastAPI_ML

# Exposition du port
EXPOSE 8001

# Création d'un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
