# Match Prediction App

![Match Prediction App](docs/match-prediction-banner.jpg)

Application complète de prédiction de matchs de Ligue 1 avec une architecture micro-services robuste :

- **2 APIs FastAPI** (Application & ML) communicantes.
- **2 bases PostgreSQL** isolées (`footballapp_db` & `footballml_db`).
- **1 frontend Vue.js 3** moderne et réactif.
- **Pipeline de données Python** (SQLAlchemy) pour le seeding et l'ingestion.
- **Orchestration Docker** manuelle pour simuler un environnement de production.

---

## 🏗️ Architecture

```text
Match-Prediction-App/
├── shared/               # Code partagé (Configuration, Schémas communs)
├── FastAPI_App/          # API Application (Auth, Historique, Favoris)
├── FastAPI_ML/           # API ML (Matchs, Entraînement, Prédiction)
├── match_prediction_app-front/  # Frontend Vue.js
├── Data/                 # Datasets CSV et documentation SQL (MCD)
├── scripts/              # Orchestration Docker (Run & Clean)
├── .env                  # Source unique de vérité (partagée)
└── docker.md             # Guide détaillé sur l'implémentation Docker
```

---

## 🚀 Démarrage Rapide (Docker)

La méthode recommandée est d'utiliser Docker pour lancer tout l'écosystème en une seule commande.

### 1. Configuration

```bash
cp .env.example .env
# Éditez .env avec vos secrets (SECRET_KEY, etc.)
```

### 2. Lancement "Zero-Touch"

```bash
chmod +x scripts/*.sh
./scripts/run_docker_env.sh
```
*Ce script s'occupe de tout : création du réseau, base de données, builds, migrations Alembic, seeding Python et entraînement initial du modèle ML.*

### 3. Accès

- **Frontend** : [http://localhost:8082](http://localhost:8082)
- **API App** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **API ML** : [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 🛠️ Développement Local (Sans Docker)

Si vous préférez travailler sans Docker, suivez ces étapes :

### 1. Base de données

Assurez-vous d'avoir PostgreSQL qui tourne sur le port 5432, puis créez les bases :

```bash
psql -U postgres -c "CREATE DATABASE footballapp_db;"
psql -U postgres -c "CREATE DATABASE footballml_db;"
```

### 2. Initialisation des Services

Appliquez les migrations et lancez les serveurs :

```bash
# API App
cd FastAPI_App && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seeds.seed_teams  # Seeding des équipes
uvicorn app.main:app --reload --port 8000

# API ML (dans un autre terminal)
cd FastAPI_ML && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

---

## 🧪 Tests et Validation

Nous recommandons d'exécuter les tests à l'intérieur des conteneurs pour garantir la parité avec la production :

```bash
# Lancer les tests de l'API principale
docker exec api-app pytest tests/

# Lancer les tests de l'intelligence artificielle
docker exec api-ml pytest tests_ml/
```

---

## 📖 Documentation Complémentaire

- **Docker** : Consultez [docker.md](docker.md) pour comprendre comment nous avons implémenté Docker sans Docker Compose.
- **Base de données** : Les schémas de référence sont disponibles dans `Data/MCD.sql` (ML) et `Data/MCD_app.sql` (App).
- **Workflow Alembic** : Toute modification des modèles Python doit faire l'objet d'une migration via `alembic revision --autogenerate`.

---

**Note d'équipe :** Ce projet privilégie l'idempotence et la modularité. Le dossier `shared/` est crucial pour maintenir une configuration cohérente entre les services.