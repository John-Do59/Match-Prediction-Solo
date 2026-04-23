import sys
import os
from contextlib import asynccontextmanager

# On ajoute le chemin vers 'shared' pour qu'il soit importable quel que soit le contexte
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.logging_config import setup_logging

# Initialisation immédiate du logging
setup_logging("API-App")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.base import register_routes
from .core.config import settings
from .core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Démarrage de l'application.
    Aucune initialisation de schéma ici — c'est le rôle d'Alembic.
    """
    yield  # L'application tourne ici


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API Application (utilisateurs, historique, favoris, prédictions) pour la Match Prediction App.",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

# Configuration de SlowAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "app-api"}
