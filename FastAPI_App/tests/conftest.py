import os
# Configuration de la base de données de test (PostgreSQL)
# On privilégie la variable d'env, sinon on adapte selon si on est dans Docker ou en local
TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://amaury:password@postgres-db:5432/footballapp_app_test" if os.path.exists("/.dockerenv") 
    else "postgresql:///footballapp_app_test"
)
os.environ["DATABASE_URL"] = TEST_DB_URL

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
# Import des modèles pour s'assurer qu'ils sont enregistrés sur Base.metadata
from app.models.user import User, PredictionHistory, UserFavoriteTeam
from app.models.team import Team

engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Crée les tables avant chaque test et les nettoie après."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    # Seeding des équipes de base pour les tests de favoris/prédictions
    teams = [
        Team(id=1, name="psg", logo_url="psg.png"),
        Team(id=2, name="om", logo_url="om.png"),
        Team(id=3, name="lens", logo_url="lens.png"),
    ]
    for t in teams:
        session.add(t)
    session.commit()
    
    try:
        yield session
    finally:
        session.close()
        # On vide les tables après chaque test pour garder l'isolation
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Client HTTP avec injection de la session DB de test."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# --- Fixtures de confort ---

@pytest.fixture
def registered_user(client):
    """Crée un utilisateur de test et retourne ses données (pour compatibilité)."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securePassword123"
    }
    client.post("/auth/register", json=user_data)
    return user_data

@pytest.fixture
def auth_headers(client, registered_user):
    """Retourne les headers d'authentification pour l'utilisateur de test."""
    resp = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"]
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
