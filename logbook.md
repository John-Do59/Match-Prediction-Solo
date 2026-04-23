# Logbook - Feature: Futuristic Landing Page & Team Dev Access

Ce logbook résume les modifications apportées à la branche `feature/futuristic-landing-page` pour optimiser le pipeline de prédiction et permettre un accès de développement facilité pour l'équipe.

## 🚀 Modifications Apportées

### 1. Intelligence Artificielle (Pipeline v3)
- **Modèle Ensemble (Stacking)** : Intégration d'un modèle de Stacking combinant **Random Forest**, **XGBoost** et **Logistic Regression**.
- **Calibration des Probabilités** : Utilisation de `CalibratedClassifierCV` pour des probabilités plus fiables (Accuracy: 57.55%, Log Loss: 0.9299).
- **Market Intelligence** : Utilisation des cotes moyennes de paris comme indicateurs de force des équipes.

### 2. Accès de Développement (Auth Bypass)
- **Frontend** : 
    - Bypass du middleware d'authentification dans `src/router/index.js`.
    - Ajout de liens directs vers "Prédictions" et "Historique" dans la `NavBar` pour une navigation sans compte.
    - Correction de bug dans `HistoryView.vue` (gestion des détails et calculs de stats).
- **Backend (FastAPI_App & FastAPI_ML)** :
    - Suppression temporaire des dépendances `get_current_user` sur les routes de prédiction et d'historique.
    - Configuration CORS mise à jour pour le développement local.

### 3. Transition vers SQLite (Zero Config)
- **Migration PostgreSQL -> SQLite** : Passage temporaire à SQLite pour supprimer la dépendance à un serveur Postgres externe.
- **Auto-Initialization** : Création automatique des tables au démarrage si elles n'existent pas.
- **Seeding Automatique** : Création d'un utilisateur par défaut (`id=1`) et chargement automatique de la liste des équipes de Premier League dans la base de données ML au lancement.

---

## 🛠️ Instructions de Lancement

Pour lancer l'environnement complet, ouvrez **3 terminaux séparés** :

### Terminal 1 : Backend API (Main)
```bash
cd FastAPI_App
python3 -m uvicorn app.main:app --port 8000 --reload
```
*Note : Utilise la base `FastAPI_App/app.db`.*

### Terminal 2 : Moteur ML (Intelligence Engine)
```bash
cd FastAPI_ML
python3 -m uvicorn app.main:app --port 8001 --reload
```
*Note : Utilise la base `FastAPI_ML/ml_app.db`.*

### Terminal 3 : Frontend (Vue.js)
```bash
cd match_prediction_app-front
npm run serve
```
*Accès : http://localhost:8080*

---

## 🛡️ Rappels de Sécurité
> [!WARNING]
> Ces modifications sont strictement destinées au développement et aux tests internes. L'authentification est désactivée. Avant de fusionner sur `main`, il est impératif de restaurer la sécurité et les configurations PostgreSQL.

---

## 🌌 Récents Développements (Branche `feature/cosmic-glassmorphism-style`)

### 1. Refonte Interface Utilisateur (UI/UX)
- **Thème "Cosmic Glassmorphism"** : Mise en place d'un design futuriste avec des effets de transparence sur verre (glassmorphism), des gradients spatiaux et des incrustations néon.
- **Réactivité & Micro-animations** : Ajout de transitions fluides et de halos interactifs au survol (hover) sur les cartes d'équipe et l'arène de prédiction pour un rendu nettement plus premium et immersif.
- **Médias Démonstratifs** : Intégration d'images conceptuelles ciblées (ballons futuristes, nébuleuses, stades) sur l'ensemble du parcours utilisateur.

### 2. Correction et Stabilisation du Pipeline de Prédiction
- **Erreur 422 Unprocessable Entity ("Load failed")** : 
  - **Le Problème** : L'API principale (`FastAPI_App`) envoyait uniquement les identifiants numériques (`home_team_id`, `away_team_id`) au service Machine Learning (`FastAPI_ML`), alors que ce dernier (récemment mis à jour) exigeait les noms texte complets, la saison, la journée et le nom de l'arbitre.
  - **La Solution** : Remaniement de la fonction d'appel dans `FastAPI_App/routes/prediction.py` pour transmettre au modèle le bon format de payload requis.
- **Erreurs 500 Internal Server Error (PostgreSQL & KeyErrors)** :
  - **Problème A (Dictionnaire)** : L'application plantait en lisant la réponse du modèle ML : ce dernier envoyait les attributs `prediction` et `confidence`, tandis que l'application tentait de lire aveuglément `predicted_result` et `confidence_score`.
  - **Solution A** : Correction du mapping dans le backend principal.
  - **Problème B (Base de données désynchronisée)** : Plantage complet lors de la sauvegarde d'historique (renvoyant une autre erreur CORS masquée en "Load failed" sur le frontend) car la table PostgreSQL `prediction_history` manquait de 4 colonnes récemment ajoutées aux ORM (`home_team_logo_url`, `away_team_logo_url`, `predicted_result`, `confidence_score`).
  - **Solution B** : Exécution de séquences directes `ALTER TABLE` via `psql` pour injecter immédiatement ces colonnes dans la base locale et débloquer les sauvegardes sans toucher à la structure de migration de base.

---

## 📊 Expansion du Dashboard & Synchronisation ML

### 1. Dashboard de Ligue 1 Complet
- **Classement National** : Intégration d'un scraper LFP robuste pour afficher le classement officiel de la Ligue 1 en temps réel (Points, MJ, GA).
- **Matchs à Venir** : Extension de la liste des rencontres (passage de 3 à 15 matchs) pour couvrir l'intégralité d'une journée de championnat.
- **Rafraîchissement Dynamique** : Ajout d'un bouton d'actualisation avec animations GSAP pour synchroniser les données sans recharger la page.

### 2. Fiabilité de l'Intelligence Artificielle
- **Mapping des Équipes** : Création d'un utilitaire de mapping (`team_mapper.py`) pour faire la jonction entre les noms complets LFP et les noms abrégés du modèle ML (ex: "Paris Saint-Germain" ➔ "Paris SG").
- **Fin des Fallbacks Aléatoires** : Suppression des valeurs de confiance aléatoires. Le dashboard affiche désormais le véritable indice de probabilité (XGBoost) ou une valeur neutre explicite en cas d'absence de données.
- **Transparence UI** : Ajout d'une icône d'information sur les cartes de match expliquant l'origine de l'indice de confiance IA.

### 3. Optimisation de l'Expérience Utilisateur (UX)
- **Correction du Scroll** : Suppression des contraintes CSS (`height: 100%`) et des zones de défilement imbriquées qui bloquaient la navigation au trackpad/finger-scroll. La page défile désormais de manière fluide et naturelle.
- **Design Premium** : Amélioration des contrastes et de l'accessibilité visuelle des badges de prédiction.

### 4. Ajustements Prédictions et Logique Frontend
- **Suppression du Mock Score** : Retrait de l'affichage statique "Probabilité de score : 2 - 1" dans l'UI de prédiction afin d'éviter d'induire l'utilisateur en erreur, le modèle ML actuel (classification) ne fournissant pas de prédiction de score exact.
- **Sécurisation de la Saisie** : Ajout d'une règle bloquante empêchant l'utilisateur de lancer une analyse si la même équipe est sélectionnée à domicile et à l'extérieur.
- **Bypass de Sécurité (Dev)** : Désactivation temporaire de la vérification du token JWT (`get_current_user`) sur l'API pour faciliter les tests de la pipeline ML depuis l'interface sans nécessiter de compte persistant.

### 5. Centralisation de l'Architecture (Proxy Dashboard)
- **Modèle de Conception "Gateway"** : Pour simplifier le travail du Frontend et centraliser les accès, l'API principale (`FastAPI_App` sur le port 8000) sert désormais de **Proxy** pour le dashboard.
- **Délégation au Service ML** : Les requêtes `/dashboard/upcoming` et `/dashboard/standings` arrivant sur le port 8000 sont automatiquement relayées de manière asynchrone (via `httpx`) vers le service ML (port 8001). 
- **Avantages** : 
    - Le Frontend n'a plus qu'un seul interlocuteur principal.
    - La séparation des bases de données est respectée (le scraper et les données de foot restent côté ML).
    - Préparation de l'infrastructure pour l'enrichissement futur du modèle ML avec les données scrapées.
- **Mise à jour du Client API** : Le client Vue.js a été reconfiguré pour router nativement toutes les demandes de dashboard vers le serveur d'application.

---

### 5. Correction de Résolution de Nom (Shadowing)
- **Renommage Variable `round`** : Modification du paramètre de Pydantic `round` en `league_round` dans les schémas de requêtes et les routes FastAPI. Le mot "round" étant une fonction native Python (built-in), il apparaissait surligné dans l'éditeur et pouvait potentiellement créer une confusion ou un masquage de la fonctionnalité d'origine de Python.

---

## 🔝 Actualisation Saison 2025/2026 & Correction Dashboard

### 1. Alignement des Clubs (Saison Actuelle)
- **Liste Officielle** : Mise à jour de la liste des 18 clubs dans le backend ML (`FastAPI_ML/app/main.py`) pour correspondre strictement à la saison 2025/2026 fournie par l'utilisateur (incluant le **Paris FC**, **FC Lorient**, **FC Metz**, etc.).
- **Auto-Reseeding** : Ajout d'une logique de nettoyage/re-seeding automatique si le nombre d'équipes en base ne correspond pas à 18, assurant une transition fluide vers la nouvelle saison.

### 2. Fiabilité des Données & Mapping
- **Mapping 1:1** : Simplification et mise à jour de `team_mapper.py` pour garantir que le scraper LFP et le moteur de prédiction parlent le même langage sans ambiguïté sur les noms de clubs.
- **Proxy Teams** : Vérification du bon fonctionnement du proxy `/predictions/teams` qui alimente les listes déroulantes du frontend.

### 3. Optimisation de l'Interface (Dashboard)
- **Visibilité Totale du Classement** : Suppression de la contrainte CSS `max-height: 600px` dans `LeagueTable.vue`. Le classement de Ligue 1 s'affiche désormais intégralement de la 1ère à la 18ème place, offrant une vue d'ensemble immédiate sans scroll vertical interne.
- **Correction des Prédictions** : Synchronisation des listes d'équipes dans le simulateur de match pour éviter les erreurs d'équipes manquantes ou obsolètes.

---

## 🔐 Correction Auth & Support PostgreSQL

### 1. Résolution de l'Erreur d'Inscription ("Load failed")
- **Frontend** : Modification de `src/api/client.js` pour utiliser explicitement `127.0.0.1` à la place de `localhost`. Cela résout les échecs de résolution DNS IPv6 (::1) sur macOS qui interrompaient les requêtes `POST` avant d'atteindre le serveur.
- **Optimisation CORS** : Remplacement du regex générique par une déclaration explicite des origines autorisées (`http://localhost:8080`, etc.) dans `main.py`, garantissant une compatibilité totale avec l'envoi de cookies et d'en-têtes d'autorisation (`allow_credentials=True`).

### 2. Infrastructure & Base de Données
- **Validation PostgreSQL** : Confirmation que l'application utilise exclusivement les bases PostgreSQL actives (`footballapp_db` et `footballml_db`). Les tables d'utilisateurs et d'historique sont bien synchronisées sur Postgres.
- **Nettoyage** : Suppression définitive du fichier `app.db` (SQLite) résiduel dans le dossier backend pour éviter toute ambiguïté sur la source de vérité des données.

### 3. Correction Critique — Erreur 500 sur Inscription/Connexion

**Cause racine** : `passlib 1.7.4` est **incompatible** avec `bcrypt 4.x+`. La librairie `bcrypt` a supprimé son attribut `__about__` dans sa version 4.0, ce qui fait crasher `passlib` silencieusement avec une `ValueError: password cannot be longer than 72 bytes` lors de chaque appel à `get_password_hash()` ou `verify_password()`. Ce crash 500 côté serveur n'envoyait aucun header CORS dans la réponse d'erreur, ce qui faisait apparaître une erreur "Load failed" dans le navigateur (masquant le vrai problème).

**Solution** : Remplacement de `passlib.context.CryptContext` par des appels directs à `bcrypt.hashpw()` et `bcrypt.checkpw()` dans `FastAPI_App/app/core/security.py`.

**Bug Secondaire** : `LoginView.vue` tentait de lire `response.user` après la connexion, mais le schéma `Token` ne retourne que `{access_token, token_type}`. Correction : stockage du token, puis appel à `GET /auth/me` pour récupérer les données utilisateur.

---
## 🌌 Refactor Config & .env Unique (Pro)

- Mise en place d’une config commune factorisée via `shared/config/base_settings.py` (`CommonSettings`) pour éviter la duplication entre `FastAPI_App` et `FastAPI_ML`.
- Passage à un **seul** fichier `.env` à la racine (chargement via `env_file` sur `CommonSettings`), au lieu de `.env` dupliqués par API.
- Harmonisation des variables DB avec alias :
  - `FastAPI_App` utilise `DATABASE_APP_URL`
  - `FastAPI_ML` utilise `DATABASE_ML_URL`
  - avec fallback sur `DATABASE_URL` pour conserver la compatibilité avec l’ancienne doc.
- Mise à jour de la doc (`README.md`) pour refléter la convention “1 `.env` à la racine”.

---

## 🛠️ Stabilisation & Fix Logos (Sprint Actuel)

### 1. Correction Connectivité & CORS
- **Compatibilité Safari (Port 8082)** : Suite à des erreurs de connexion sur le port `8080` (Safari macOS), le frontend a été migré sur le port **8082** via `npm run serve -- --port 8082 --host 127.0.0.1`.
- **Mise à jour Whitelist CORS** : Ajout explicite des origines `http://localhost:8082` et `http://127.0.0.1:8082` dans `FastAPI_App/app/main.py` et `FastAPI_ML/app/main.py`.

### 2. Synchronisation Base de Données
- **Rectification Nom de BDD** : Correction d'une divergence entre le code et la réalité physique du serveur PostgreSQL. Le script de configuration pointait vers `footballprediction_db` alors que la base effective est **`footballml_db`**. Mise à jour du fichier `.env` à la racine.
- **Script de Test** : Création de `test_db_ml.py` pour valider instantanément la connexion à la base ML et le compte des équipes.

### 3. Validation de l'Arène de Prédiction
- **Affichage des Logos** : Confirmation du bon fonctionnement de la récupération des logos via l'endpoint `/predictions/teams`. Les icônes s'affichent désormais correctement dans les sélecteurs et le scanner de l'Arène de Prédiction.
- **Révision `api.js`** : Correction d'une régression dans `match_prediction_app-front/src/services/api.js` qui tentait indûment d'appeler le port 8080 au lieu de 8000.

### 4. Rétablissement de la Sauvegarde d'Historique
- **Déconnexion Frontend-Backend** : Le bouton "Enregistrer la prédiction" (`savePrediction`) dans l'interface redirigeait simplement vers l'historique sans jamais envoyer de requête POST. L'API Principale (`FastAPI_App`) avait perdu sa route `/predictions/history` suite à la séparation avec l'API ML.
- **Correction du Backend (FastAPI_App)** : Restauration et refactoring du routeur `prediction.py` pour y inclure spécifiquement un endpoint `POST /history` qui sauvegarde la prédiction complète en base de données.
- **Routage API Client** : Mise à jour du client `apiClient.js` (Frontend) afin que toutes les requêtes commençant par `/predictions` (qui incluent la sauvegarde et la consultation de l'historique) soient routées vers l'API Principale (Port 8000) et non vers le moteur ML.

---

## 🔄 Fusion & Adaptation Branche `develop` (v4 - Avril 2026)

### 1. Synchronisation avec `develop` (PR Umberto)
- **Merge & Résolution de Conflits** : Fusion de la branche `develop` mise à jour par les travaux d'Umberto.
- **Hybridation des Routes ML** : 
    - Conservation des routes **Dashboard & Proxy** (Cosmic UI).
    - Intégration des nouvelles routes **Ingestion de données CSV** (`/ingestion`) apportées par `develop`.
    - Résolution de conflit dans `FastAPI_ML/app/main.py` pour enregistrer les deux routeurs.

### 2. Harmonisation de la Configuration (.env)
- **Retour au `.env` Unique** : Suite à la demande utilisateur, abandon de la fragmentation des fichiers `.env` par service (introduite dans `develop`).
- **Update `BaseSettings`** : Mise à jour des classes `Settings` dans `FastAPI_App` et `FastAPI_ML` pour pointer systématiquement vers le fichier `.env` à la racine du projet via le package `shared`.
- **Enrichissement des Variables** : Ajout de `ML_API_URL` et `DATABASE_URL` (alias) dans le `.env` racine pour garantir que le proxy et les deux APIs fonctionnent de concert sans duplication de fichiers.

### 3. Préservation de l'Identité "Cosmic"
- **Vérification UI** : Validation que les composants Vue.js (`PredictionView.vue`, `StatisticsView.vue`) ont conservé leurs animations GSAP et leur style Glassmorphism malgré les simplifications présentes sur `develop`.
- **Intégrité des Modèles** : Restauration/Maintien de la colonne `logo_url` dans le modèle `Team` pour ne pas casser le scraper et l'affichage des logos dans le frontend.

---

## 🏗️ Refactoring Base de Données & Migration Alembic

### 1. Modernisation de l'Initialisation de la Base de Données
- **Suppression Acte de Foi (create_all)** : Retrait systématique des appels `Base.metadata.create_all(bind=engine)` dans le `lifespan` de `FastAPI_App` et `FastAPI_ML` afin de supprimer l'initialisation magique et dangereuse de SQLAlchemy.
- **Intégration Alembic** : Ajout d'Alembic dans les dépendances (`requirements.txt`) des deux API et configuration asynchrone (`env.py`) pour relier dynamiquement l'outil de migration aux modèles métiers SQLAlchemy en lecture autoconfigurée.
- **Paramétrage `.env` Sécurisé** : Centralisation complète des connections via `DATABASE_URL` et `DATABASE_ML_URL` déclarés dans le `.env` pour empêcher Alembic d'utiliser des bases par défaut en dur dans `.ini`.

### 2. Nettoyage de la Dette Technique
- **Suppression des Scripts Hybrides** : Tous les scripts de création brut ou orphelins (ex: `init_db.py`, `cleanup_teams.py`) ont été purgés pour forcer une source de vérité unique : les fichiers de migrations d'Alembic.
- **Conversion du MCD** : L'ancien script `MCD_app.sql` rempli de commandes SQL de création a été neutralisé (transformation en simple documentation par des commentaires ciblés) pour ne plus perturber la base.

### 3. Résolution des Bugs de Post-Migration
- **Oblitérations des Fausses Routes "baseline_initial"** : Les migrations dites vierges (`baseline_initial.py`), qui bloquaient les builds (erreur `UndefinedTable` ou relation n'existant pas PostgreSQL), ont été droppées via `alembic downgrade base` et supprimées du code.
- **Exécution Vraie & Création Active** : Nouvelles migrations propulsées via `alembic revision --autogenerate -m "Init schema"`. Ces scripts contiennent réellement les `op.create_table(...)`. L'appel final à `alembic upgrade head` a instantanément et matériellement bâti les bases `footballapp_db` et `footballml_db`.
- **Ré-Alignement de l'Ingestion ML** : Le plantage `FileNotFoundError` sur les datasets de l'interface ML a été corrigé en modifiant la variable `DATA_DIR=../Data/dataset/` dans la config et le template `.env.example`.
- **Résolution Auth (JWT "Could not validate...")** : Suite à la disparition des anciens comptes lors la mise à jour, remplacement du bug "utilisateur dev fantôme" par une procédure propre (Déconnexion / Réinscription) ou l'usage documenté de la fonction `bcrypt` en SQL direct.
- **Activation Prédiction (Data Matchday & Équipes)** : Lancement des routes `POST /ingest` (1234 matchs importés de la LFP) et `POST /train` qui ont peuplé la `team_stats_reference`, résolvant la page Prédiction et réglant l'erreur "Équipes introuvables".
