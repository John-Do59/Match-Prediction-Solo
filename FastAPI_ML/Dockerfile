# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Installation des dépendances de build
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python (incluant pandas, sklearn, scipy)
COPY FastAPI_ML/requirements.prod.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.prod.txt


# Stage 2: Final (Runtime)
FROM python:3.12-slim

WORKDIR /app

# Runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages
COPY --from=builder /install /usr/local

# Copie du dossier partagé
COPY shared/ /app/shared/

# Copie du code de l'application et des scripts
COPY FastAPI_ML/ /app/FastAPI_ML/
COPY scripts/docker-entrypoint.sh /app/scripts/docker-entrypoint.sh
RUN chmod +x /app/scripts/docker-entrypoint.sh

WORKDIR /app/FastAPI_ML

EXPOSE 8001

# Sécurité : Utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
