import sys
from pathlib import Path
from pydantic import Field

# Ajout du chemin racine pour importer le package 'shared'
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.base_settings import CommonSettings


class Settings(CommonSettings):
    PROJECT_NAME: str = "Match Prediction App - Application API"

    # On utilise Field pour mapper DATABASE_URL (BaseSettings le fait déjà nativement
    # mais on s'assure qu'il n'y a pas de confusion)
    DATABASE_URL: str

    ML_API_URL: str = "http://localhost:8001"


settings = Settings()
