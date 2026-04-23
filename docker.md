# Guide d'Apprentissage : Docker Sans Docker Compose

Ce document explique le fonctionnement de Docker et détaille comment nous l'avons implémenté manuellement dans le projet **Match Prediction App**.

---

## 🧭 1. Introduction à Docker

### C'est quoi ?

Docker est une plateforme qui permet d'emballer une application et toutes ses dépendances (librairies, configuration, environnement) dans une unité isolée appelée **Conteneur**.

### Pourquoi Docker ?

- **"It works on my machine"** : Garanti que si ça tourne sur ton ordi, ça tournera partout (Serveur, Cloud, PC d'un collègue).
- **Isolation** : Chaque micro-service vit dans sa propre boîte. Si l'API ML plante, elle ne fait pas tomber la base de données.
- **Légèreté** : Contrairement à une machine virtuelle, Docker partage les ressources de ton ordinateur sans simuler tout un système d'exploitation.

### 📚 Lexique Essentiel

| Terme | Définition simple |
| :--- | :--- |
| **Image** | C'est le "plan" ou le moule. C'est un fichier mort qui contient ton code et tes réglages. |
| **Conteneur** | C'est l'image en train de tourner. C'est l'instance vivante de ton application. |
| **Dockerfile** | La recette de cuisine qui explique comment transformer ton code en image. |
| **Volume** | Un disque dur externe pour Docker. Sert à garder les données (ex: ta BDD) même si le conteneur est supprimé. |
| **Persistance** | Capacité à garder les données après un redémarrage (via les Volumes). |
| **Réseau (Network)** | Un câble invisible qui relie tes conteneurs entre eux. |
| **Registry** | Une bibliothèque d'images (ex: Docker Hub pour télécharger l'image officielle de Postgres). |

---

## 🏗️ 2. Pourquoi "Sans Docker Compose" ?

De nos jours, on utilise `docker-compose.yml` pour lancer 10 conteneurs d'un coup. Mais pour apprendre, le faire manuellement est crucial. Sans le Compose, nous devons :

1. Devenir l'**Orchestrateur** : Nous devons décider quel conteneur démarre en premier.
2. Tirer les **Câbles Réseau** : Nous devons créer nous-mêmes le réseau et y brancher chaque service.

---

## 🛠️ 3. L'Implémentation Étape par Étape

### Étape A : Les fichiers d'exclusion (`.dockerignore`)

Avant de builder, on dit à Docker ce qu'il ne doit **pas** copier.

- **Pourquoi ?** On ne veut pas copier les dossiers `venv/` (qui sont propres à ton Mac) ou les bases de données locales `.db` dans l'image. On veut une image propre.

### Étape B : Les Recettes (Dockerfiles)

Nous avons créé trois Dockerfiles différents :

#### 1. Backend (Python)

- On commence par une image légère : `python:3.12-slim`.
- On installe `libpq-dev` et `gcc` car la librairie `psycopg2` (pour Postgres) a besoin d'outils de compilation système.
- **Astuce de Pro** : On copie d'abord `requirements.txt` et on fait le `pip install` **AVANT** de copier le code. Pourquoi ? Parce que si tu modifies ton code mais pas tes dépendances, Docker réutilise le cache du `pip install` et gagne 2 minutes à chaque build !

#### 2. Frontend (Multi-stage Build)

C'est la partie la plus avancée. On utilise deux étapes :

- **Stage 1 (Node)** : On compile le code Vue.js. Une fois terminé, on a un dossier `dist/` plein de fichiers statiques.
- **Stage 2 (Nginx)** : On jette tout ce qui est Node (trop lourd) et on ne garde que le petit dossier `dist/` qu'on donne à un serveur Web ultra-léger (Nginx).

### Étape C : Le Réseau ("match-network")

Comme tes conteneurs sont isolés, `localhost` ne fonctionne plus entre eux.

- Nous créons un réseau : `docker network create match-network`.
- Désormais, le backend peut contacter la base de données via son nom de conteneur : `postgres-db`.

### Étape D : Connexion et Variables d'Environnement

Dans Docker, on ne modifie pas le code pour changer de base de données. On utilise l'option `--env-file .env` ou `-e DATABASE_URL=...` au moment du lancement.

- Cela permet au même code d'utiliser une DB locale en dev et une DB Docker en conteneur.

---

## 🚀 4. Les Scripts d'Automatisation

Pour éviter de taper 15 commandes à chaque fois, nous avons créé deux scripts dans `/scripts` :

1.  **`run_docker_env.sh`** :
    - Il crée le réseau.
    - Il lance Postgres **avec un volume de persistance** (`postgres_data`).
    - Il crée les bases `footballml_db` et `footballapp_app_test` si elles n'existent pas.
    - Il build les 3 images (App, ML, Front).
    - Il lance les 3 conteneurs.
    - **Nouveauté :** Il exécute automatiquement les **migrations Alembic** et charge les **seeds** via `docker exec`.

2.  **`docker_clean.sh`** :
    - C'est l'équivalent de "tout ranger". Il arrête et supprime les conteneurs et le réseau pour laisser ton Docker tout propre.

---

## ⚠️ 5. Astuce : Résoudre les conflits de ports

Si tu vois l'erreur `"Port already in use"` ou `"Bind for 0.0.0.0:8000 failed"`, cela signifie qu'un service (Docker ou local) utilise déjà ce port.

### Pourquoi ça arrive ?

1.  **Serveur local actif** : Tu as un terminal ouvert qui fait tourner `uvicorn` ou `npm run serve`.
2.  **Ancien conteneur** : Un conteneur Docker précédent n'a pas été bien arrêté.

### Comment régler ça ?

1.  **Méthode Automatique** : Lance `./scripts/run_docker_env.sh`. J'ai mis à jour le script pour qu'il vérifie automatiquement si les ports 8000, 8001, 8082 et 5432 sont libres avant de démarrer.
2.  **Cas Particulier du Port 5432 (Postgres)** :
    - Si tu as PostgreSQL installé via Homebrew sur ton Mac, il tourne en tant que service système.
    - Utilise cette commande pour le libérer : `brew services stop postgresql@18` (ou ta version).
3.  **Méthode Manuelle** :
    - Tape `lsof -i :8000` pour voir quel processus utilise le port.
    - Arrête tes serveurs locaux dans tes terminaux.
    - Lance `./scripts/docker_clean.sh` pour nettoyer les vieux conteneurs Docker.

---

## 💻 6. Commandes Terminal Essentielles

Pour ce projet, utilise ces commandes dans ton terminal (à la racine du projet) :

### Lancer l'environnement

```bash
./scripts/run_docker_env.sh
```

*Cette commande fait tout : Réseau -> BDD -> Build Images -> Lancement Conteneurs.*

### Tout arrêter et nettoyer

```bash
./scripts/docker_clean.sh
```

*Utile si tu veux recommencer de zéro ou libérer de la mémoire sur ton Mac.*

### Inspecter ce qui se passe

- **Voir les conteneurs actifs** : `docker ps`
- **Voir TOUS les conteneurs (même arrêtés)** : `docker ps -a`
- **Voir les images créées** : `docker images`
- **Voir les logs d'un service (ex: l'API App)** : `docker logs -f api-app`
- **Entrer dans le conteneur de la BDD** : `docker exec -it postgres-db psql -U amaury -d footballapp_db`

---

## 🧪 7. Tests Automatisés en Docker

Désormais, tu peux valider la stabilité de l'application directement dans son environnement de conteneur.

### Pourquoi tester dans Docker ?

- On utilise les mêmes librairies et la même version de Python que la production.
- On teste la connectivité réelle avec PostgreSQL.

### Comment ça marche ?

1. Le script `run_docker_env.sh` crée automatiquement une base de données dédiée aux tests nommée `footballapp_app_test`.
2. Le fichier `FastAPI_App/tests/conftest.py` détecte s'il est dans Docker et bascule sur cette base de test.
3. Pour lancer les tests :
   ```bash
   docker exec api-app pytest
   ```

### Que vérifier en cas d'erreur ?

- Vérifie que le conteneur `api-app` est bien démarré.
- Assure-toi qu'aucune instance locale de Postgres ne bloque le port 5432.

---

**Bravo !** En maîtrisant ces étapes manuelles, tu as compris 95% de ce que `docker-compose` fait automatiquement. Tu peux maintenant utiliser ces scripts pour tester ton projet dans un environnement de production simulé sur ton Mac.
