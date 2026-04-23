-- ============================================================
-- DB ML : footballml_db
-- Données de matchs, statistiques et modèle ML
-- ============================================================

CREATE DATABASE footballml_db;

\c footballml_db;

-- ============================================================
-- Table des équipes
-- ============================================================
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- ============================================================
-- Table des matchs de football
-- Corrigée pour correspondre au modèle SQLAlchemy
-- ============================================================
CREATE TABLE football_matches (
    id SERIAL PRIMARY KEY,
    league_season INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_score INT,
    away_score INT,
    date VARCHAR(50),
    time VARCHAR(20),
    result VARCHAR(10),
    
    -- Stats brutes du match
    halftime_home_goals INT,
    halftime_away_goals INT,
    halftime_result VARCHAR(10),
    home_shot INT,
    away_shot INT,
    home_shot_target INT,
    away_shot_target INT,
    home_team_fouls INT,
    away_team_fouls INT,
    home_team_corners INT,
    away_team_corners INT,
    home_yellow_cards INT,
    away_yellow_cards INT,
    home_red_cards INT,
    away_red_cards INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_home_team FOREIGN KEY (home_team_id)
        REFERENCES teams (id) ON DELETE RESTRICT,
    CONSTRAINT fk_away_team FOREIGN KEY (away_team_id)
        REFERENCES teams (id) ON DELETE RESTRICT
);

-- ============================================================
-- Table des statistiques calculées par match
-- Manquante dans le script original
-- ============================================================
CREATE TABLE match_stats (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL UNIQUE,
    
    -- Stats saison séparées par lieu
    home_goals_scored_home FLOAT,
    home_goals_conceded_home FLOAT,
    home_win_rate_home FLOAT,
    away_goals_scored_away FLOAT,
    away_goals_conceded_away FLOAT,
    away_win_rate_away FLOAT,
    
    -- Classement
    home_season_rank INT,
    away_season_rank INT,
    
    -- Rolling averages — forme récente (5 derniers matchs)
    home_rolling_scored FLOAT,
    home_rolling_conceded FLOAT,
    home_rolling_win_rate FLOAT,
    away_rolling_scored FLOAT,
    away_rolling_conceded FLOAT,
    away_rolling_win_rate FLOAT,
    
    CONSTRAINT fk_match_stats FOREIGN KEY (match_id)
        REFERENCES football_matches (id) ON DELETE CASCADE
);

-- ============================================================
-- Table de référence des statistiques par équipe par saison
-- Manquante dans le script original
-- ============================================================
CREATE TABLE team_stats_reference (
    id SERIAL PRIMARY KEY,
    team VARCHAR(100) NOT NULL,
    season INT NOT NULL,
    
    -- Stats domicile
    goals_scored_home FLOAT,
    goals_conceded_home FLOAT,
    win_rate_home FLOAT,
    
    -- Stats extérieur
    goals_scored_away FLOAT,
    goals_conceded_away FLOAT,
    win_rate_away FLOAT,
    
    -- Classement
    season_rank FLOAT,
    
    -- Rolling averages
    rolling_scored_home FLOAT,
    rolling_conceded_home FLOAT,
    rolling_win_rate_home FLOAT,
    rolling_scored_away FLOAT,
    rolling_conceded_away FLOAT,
    rolling_win_rate_away FLOAT,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- Table des logs d'entraînement du modèle
-- Manquante dans le script original
-- ============================================================
CREATE TABLE train_log (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_version VARCHAR(50) NOT NULL,
    n_samples INT NOT NULL,
    cv_accuracy FLOAT NOT NULL,
    cv_log_loss FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_message VARCHAR(500)
);

-- Index pour optimiser les performances
CREATE INDEX idx_football_matches_season ON football_matches(league_season);
CREATE INDEX idx_football_matches_date ON football_matches(date);
CREATE INDEX idx_match_stats_match_id ON match_stats(match_id);
CREATE INDEX idx_team_stats_reference_team_season ON team_stats_reference(team, season);
CREATE INDEX idx_train_log_created_at ON train_log(created_at);