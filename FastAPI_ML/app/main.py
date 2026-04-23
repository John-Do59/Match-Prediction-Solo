from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services.ml_service import ml_service
from .routes.predict import register_routes
from .routes.train import register_routes as register_train_routes
from .routes.ingestion import register_routes as register_ingestion_routes
from .core.config import settings
from .database import SessionLocal


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Démarrage de l'application ML.
    Aucune initialisation de schéma ici — c'est le rôle d'Alembic.
    Seul le modèle scikit-learn est chargé en mémoire au démarrage.
    """
    from pathlib import Path

    if Path(settings.MODEL_PATH).exists():
        try:
            ml_service.load_model()
            db = SessionLocal()
            try:
                ml_service.load_stats_from_db(db)
            finally:
                db.close()
            print("Modèle chargé avec succès.")
        except Exception as e:
            print(f"Avertissement — modèle non chargé : {e}")
    else:
        print(f"Avertissement — modèle introuvable : {settings.MODEL_PATH}")
        print("Lancez POST /train pour entraîner le premier modèle.")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API ML (données de matchs, entraînement et prédiction) pour la Match Prediction App.",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)
register_train_routes(app)
register_ingestion_routes(app)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ml-api"}
