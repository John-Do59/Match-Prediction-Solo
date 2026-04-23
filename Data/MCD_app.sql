-- ============================================================
-- DB APPLICATION : footballapp_db
-- Gestion des utilisateurs, de l'authentification et de
-- l'historique des prédictions.
-- SÉPARÉE de footballml_db (DB ML / Data).
--
-- USAGE : Ce fichier sert de RÉFÉRENCE pour documenter le schéma.
-- Pour créer les tables, utiliser Alembic : alembic upgrade head
-- ============================================================

-- Prérequis : créer la base manuellement avant d'appliquer les migrations
-- psql -U postgres -c "CREATE DATABASE footballapp_db;"

-- ============================================================
-- Table des équipes (référence pour les prédictions)
-- ============================================================
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    logo_url VARCHAR(255)
);

-- ============================================================
-- Table des utilisateurs (authentification JWT)
-- ============================================================
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Table de l'historique des prédictions
-- ============================================================
CREATE TABLE prediction_history (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_team_name VARCHAR(100) NOT NULL,
    home_team_logo_url TEXT,
    away_team_name VARCHAR(100) NOT NULL,
    away_team_logo_url TEXT,
    predicted_result VARCHAR(10),
    confidence_score NUMERIC(5, 4),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_prediction FOREIGN KEY (user_id)
        REFERENCES "user" (id) ON DELETE CASCADE,
    CONSTRAINT fk_home_team FOREIGN KEY (home_team_id)
        REFERENCES teams (id),
    CONSTRAINT fk_away_team FOREIGN KEY (away_team_id)
        REFERENCES teams (id)
);

-- ============================================================
-- Table des équipes favorites d'un utilisateur
-- ============================================================
CREATE TABLE user_favorite_team (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    team_id INT,
    CONSTRAINT fk_user_favorite FOREIGN KEY (user_id)
        REFERENCES "user" (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_favorite FOREIGN KEY (team_id)
        REFERENCES teams (id),
    CONSTRAINT uq_user_team UNIQUE (user_id, team_id)
);

-- Index
CREATE INDEX idx_prediction_history_user_id ON prediction_history(user_id);
CREATE INDEX idx_prediction_history_created_at ON prediction_history(created_at);
CREATE INDEX idx_user_favorite_team_user_id ON user_favorite_team(user_id);