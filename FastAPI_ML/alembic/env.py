"""
Alembic env.py — FastAPI_ML (footballml_db)

Ce fichier connecte Alembic aux modèles SQLAlchemy pour permettre
la génération et l'application des migrations de la base ML.
"""
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# FastAPI_ML/alembic/env.py → on remonte à FastAPI_ML/
APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ── Import des variables d'environnement ──────────────────────────────────────
from dotenv import load_dotenv
import os

_root_env = APP_DIR.parent / ".env"
load_dotenv(dotenv_path=_root_env)

# ── Import des modèles SQLAlchemy ─────────────────────────────────────────────
# Import obligatoire de TOUS les modèles ML pour qu'Alembic les détecte
from app.database import Base
import app.models.match  # noqa: F401 — enregistre Team, FootballMatch, MatchStats, etc.

# ── Configuration Alembic ─────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Cible de l'autogenerate
target_metadata = Base.metadata

# Injection dynamique de l'URL depuis l'environnement (DATABASE_ML_URL)
DATABASE_ML_URL = os.environ.get("DATABASE_ML_URL")
if not DATABASE_ML_URL:
    raise RuntimeError(
        "La variable d'environnement DATABASE_ML_URL est manquante.\n"
        "Copie .env.example en .env et remplis DATABASE_ML_URL."
    )
config.set_main_option("sqlalchemy.url", DATABASE_ML_URL)


# ── Mode offline (génération SQL sans connexion live) ─────────────────────────
def run_migrations_offline() -> None:
    """Génère les migrations en SQL pur sans connexion active."""
    context.configure(
        url=DATABASE_ML_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Mode online (migrations appliquées directement en base) ──────────────────
def run_migrations_online() -> None:
    """Applique les migrations sur la base de données connectée."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
