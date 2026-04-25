import sys
from pathlib import Path
from pydantic import AliasChoices, Field

# Ajout du chemin racine pour importer le package 'shared'
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.base_settings import CommonSettings

class Settings(CommonSettings):
    PROJECT_NAME: str = "Match Prediction App - ML API"
    
    # On mappe DATABASE_ML_URL vers DATABASE_URL pour compatibilité avec BaseSettings
    # Pas de valeur par défaut pour forcer la config via env
    DATABASE_URL: str = Field(
        validation_alias=AliasChoices("DATABASE_ML_URL", "DATABASE_URL"),
    )
    
    # Token partagé pour l'authentification inter-services
    SERVICE_TOKEN: str
    
    CORS_ORIGINS: list[str] = ["*"]
    DATA_DIR:     str = Field(default="../Data/dataset/")
    MODEL_PATH:   str = Field(default="../Data/dataset/match_model_v1.joblib")
    DATASET_PATH: str = Field(default="../Data/dataset/completed_match_dataset_final.csv")

settings = Settings()

