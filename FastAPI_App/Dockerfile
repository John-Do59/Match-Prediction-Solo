# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Installation des dépendances de build (nécessaires pour compiler psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python dans un dossier isolé (--prefix)
# On utilise le fichier .prod pour exclure les outils de test
COPY FastAPI_App/requirements.prod.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.prod.txt


# Stage 2: Final (Runtime)
FROM python:3.12-slim

WORKDIR /app

# Installation du strict nécessaire pour le runtime
# libpq5 est la bibliothèque runtime pour PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Récupération des packages installés depuis le builder
COPY --from=builder /install /usr/local

# Copie du dossier partagé
COPY shared/ /app/shared/

# Copie du code de l'application et des scripts
COPY FastAPI_App/ /app/FastAPI_App/
COPY scripts/docker-entrypoint.sh /app/scripts/docker-entrypoint.sh
RUN chmod +x /app/scripts/docker-entrypoint.sh

# Configuration de l'environnement de travail
WORKDIR /app/FastAPI_App

# Exposition du port
EXPOSE 8000

# Sécurité : Utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Utilisation de l'entrypoint
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
