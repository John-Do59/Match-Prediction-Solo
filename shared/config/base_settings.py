"""
Configuration de base partagée utilisant Pydantic Settings.

Ce module définit la classe `CommonSettings` qui sert de base à toutes les configurations
de microservices du projet. Il gère :
- La détection automatique de la racine du projet (`ROOT_DIR`).
- Le chargement des variables d'environnement depuis un fichier `.env` centralisé.
- Les paramètres communs de sécurité (JWT, algorithmes, expirations).
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Chemin vers la racine du projet (Match-Prediction-App/)
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = ROOT_DIR / ".env"


class CommonSettings(BaseSettings):
    """
    Settings communs aux services (env_file unique, JWT, etc.).
    Chaque API étend cette classe pour ajouter ses champs spécifiques.
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH) if ENV_FILE_PATH.exists() else None,
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_VERSION: str = "0.1.0"

    # JWT — SECRET_KEY est OBLIGATOIRE, pas de valeur par défaut pour éviter
    # qu'une instance oubliée tourne avec une clé publiquement connue.
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

