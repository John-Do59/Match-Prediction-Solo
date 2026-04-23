# Guide d'Apprentissage : Docker Sans Docker Compose

Ce document explique le fonctionnement de Docker et détaille comment nous l'avons implémenté manuellement dans le projet **Match Prediction App** pour simuler une architecture micro-services professionnelle.

---

## 1. Introduction à Docker

### C'est quoi ?

Docker est une plateforme qui permet d'emballer une application et toutes ses dépendances (librairies, configuration, environnement) dans une unité isolée appelée **Conteneur**.

### Pourquoi Docker ?

- **"It works on my machine"** : Garanti que si ça tourne sur ton ordi, ça tournera partout (Serveur, Cloud, PC d'un collègue).
- **Isolation** : Chaque micro-service vit dans sa propre boîte. Si l'API ML plante, elle ne fait pas tomber la base de données.
- **Légèreté** : Contrairement à une machine virtuelle, Docker partage les ressources de ton ordinateur sans simuler tout un système d'exploitation.

### Lexique Essentiel

| Terme | Définition simple |
| :--- | :--- |
| **Image** | C'est le "plan" ou le moule. C'est un fichier statique qui contient ton code et tes réglages. |
| **Conteneur** | C'est l'image en train de tourner. C'est l'instance vivante de ton application. |
| **Dockerfile** | La recette de cuisine qui explique comment transformer ton code en image. |
| **Volume** | Un disque dur persistant. Sert à garder les données (ex: ta BDD) même si le conteneur est supprimé. |
| **Réseau (Network)** | Un câble invisible qui relie tes conteneurs entre eux (`match-network`). |
| **Orchestration** | L'art de coordonner le démarrage et la communication entre plusieurs conteneurs. |

---

## 2. Architecture du Projet

Notre implémentation utilise une approche "Zero-Touch" : un seul script lance tout l'écosystème.

### Composants Clés

1. **Frontend (Port 8082)** : Interface utilisateur (Nginx + Vue.js).
2. **API App (Port 8000)** : Backend principal (FastAPI + PostgreSQL).
3. **API ML (Port 8001)** : Intelligence Artificielle (FastAPI + Modèles Pré-entraînés).
4. **PostgreSQL (Port 5432)** : Base de données relationnelle unique avec deux schémas (`footballapp_db` et `footballml_db`).

### Le Module `shared/`

Pour éviter la duplication de code, nous utilisons un dossier `shared/` à la racine :

- Contient les **Common Settings** (Pydantic).
- Est copié dynamiquement dans chaque conteneur lors du `docker build`.
- **Astuce Technique** : Pour que les migrations Alembic puissent importer `shared`, nous avons modifié `alembic/env.py` pour ajouter le répertoire parent au `sys.path`.

---

## 3. Pipeline de Données Automatisé (Python Seeding)

Nous avons abandonné les anciens scripts SQL (`Data/*.sql`) pour un pipeline Python moderne et robuste.

### Avantages du Seeding via SQLAlchemy

- **Idempotence** : Les scripts vérifient si la donnée existe déjà avant de l'insérer (pas de doublons).
- **Flexibilité** : On peut utiliser des algorithmes complexes pour générer des données (ex: hashing de mots de passe, calculs ML).
- **Maintenance** : Plus besoin de modifier 10 fichiers SQL quand le schéma change ; on utilise les modèles Python.

### Déroulement de l'initialisation

Au démarrage, le script d'orchestration :

1. Lance les migrations **Alembic** pour créer les tables.
2. Exécute `seed_teams.py` pour remplir les référentiels.
3. Appelle l'API ML pour lancer l'**Ingestion** (CSV -> SQL) et l'**Entraînement** initial du modèle.

---

## 4. Guide d'Utilisation

### Lancer l'environnement complet

```bash
chmod +x scripts/*.sh
./scripts/run_docker_env.sh
```

*Cette commande fait tout : Nettoyage -> Réseau -> BDD -> Build -> Migrations -> Seeds -> Ingestion & Training ML.*

### Nettoyer tout l'environnement

```bash
./scripts/docker_clean.sh
```

*Arrête les conteneurs et supprime le réseau pour libérer les ressources.*

### Exécuter les tests unitaires (Dans Docker)

Il est crucial de tester dans Docker car c'est l'environnement qui se rapproche le plus de la production.

```bash
# API Principale
docker exec api-app pytest tests/

# API Machine Learning
docker exec api-ml pytest tests_ml/
```

---

## 5. Résolution de Problèmes

| Problème | Solution |
| :--- | :--- |
| **Port already in use** | Lancez `./scripts/docker_clean.sh` ou vérifiez avec `lsof -i :8000`. |
| **Shared module not found** | Vérifiez que le `Dockerfile` copie bien le dossier `shared/` et que `env.py` a le bon `sys.path`. |
| **Migration failed** | Vérifiez les logs avec `docker logs api-app`. Souvent dû à une DB non prête (le script attend désormais 5s). |
| **HTTPX missing** | Si les tests ML échouent, assurez-vous que `httpx` est présent dans le `requirements.txt` de l'API ML. |

---

**Note sur Docker Compose** : En maîtrisant ces commandes manuelles, vous comprenez le "coeur" de Docker. Dans un vrai projet pro, on utiliserait Docker Compose pour simplifier, mais savoir le faire à la main fait de vous un expert.
fait automatiquement. Tu peux maintenant utiliser ces scripts pour tester ton projet dans un environnement de production simulé sur ton Mac.
