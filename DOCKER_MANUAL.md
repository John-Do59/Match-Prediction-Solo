# Guide Docker Multi-Environnement (DEV & PROD)

Ce projet supporte deux environnements distincts pilotés par la variable `ENV`.

---

## 1. Choix de l'Environnement

Nous utilisons deux fichiers de configuration séparés :

* **`.env.dev`** : Pour le développement local (simple, HTTP uniquement).
* **`.env.prod`** : Pour la production (sécurisé, HTTPS obligatoire).

---

## 2. Méthode Automatisée (Recommandée)

Deux scripts sont à votre disposition pour lancer tout l'écosystème d'un coup :

### Mode DEV (Démonstration locale)

* **Port** : [http://localhost:8082](http://localhost:8082)
* **Sécurité** : SSL désactivé, secrets par défaut.

```bash
./scripts/start-dev.sh
```

### Mode PROD (Simulation de production)

* **Port** : [https://localhost:8443](https://localhost:8443)
* **Sécurité** : SSL activé (nécessite le dossier `ssl/`), secrets renforcés.

```bash
./scripts/start-prod.sh
```

---

## 3. Méthode Manuelle (Pas à pas)

Si vous préférez lancer les conteneurs un par un, voici la logique à suivre.

### Étape 0 : Build des Images (Requis avant le premier lancement)

Si vous n'utilisez pas les scripts automatisés, vous devez d'abord construire les images localement :

```bash
# Build API App
docker build -t match-api-app -f FastAPI_App/Dockerfile .

# Build API ML
docker build -t match-api-ml -f FastAPI_ML/Dockerfile .

# Build Frontend
docker build -t match-frontend -f match_prediction_app-front/Dockerfile .
```


### Étape A : Création du réseau

```bash
docker network create match-network
```

### Étape B : Lancer la Base de Données

```bash
# Lancement avec création automatique des deux bases (via script d'init)
docker run -d \
  --name postgres-db \
  --network match-network \
  -v match_prediction_pg_data:/var/lib/postgresql/data \
  -v "$(pwd)/scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql" \
  -e POSTGRES_USER=amaury \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  postgres:15
```

> [!NOTE]
> Nous utilisons `POSTGRES_DB=postgres` comme base par défaut, et le script `init-db.sql` crée ensuite `footballapp_db` et `footballml_db`.


### Étape C : Lancer le Frontend (Choix de l'ENV)

**En mode DEV (HTTP) :**

```bash
docker run -d \
  --name frontend-vue \
  --network match-network \
  -p 8082:8080 \
  -e ENV=dev \
  match-frontend
```

**En mode PROD (HTTPS) :**

```bash
docker run -d \
  --name frontend-vue \
  --network match-network \
  -v "$(pwd)/ssl:/etc/nginx/ssl:ro" \
  -p 8082:8080 \
  -p 8443:8443 \
  -e ENV=prod \
  match-frontend
```

### Étape D : Lancer les APIs

Une fois le réseau, la base de données et le frontend prêts, lancez les services backend :

```bash
# API Application (Port 8000)
docker run -d \
  --name api-app \
  --network match-network \
  -p 8000:8000 \
  --env-file .env.dev \
  -e ENV=dev \
  match-api-app

# API Machine Learning (Port 8001)
docker run -d \
  --name api-ml \
  --network match-network \
  -p 8001:8001 \
  --env-file .env.dev \
  -e ENV=dev \
  match-api-ml
```

### Étape E : Initialisation des Données

Une fois les services lancés, vous devez préparer la base de données :

```bash
# 1. Appliquer les migrations Alembic (Schémas SQL)
docker exec api-app alembic upgrade head
docker exec api-ml alembic upgrade head

# 2. Charger les référentiels (Équipes)
docker exec api-app python -m app.seeds.seed_teams

# 3. Ingestion et Entraînement du modèle ML
curl -X POST http://localhost:8001/ingest
curl -X POST http://localhost:8001/train
```

---

## 4. Choix Techniques & Mentalité DevOps

1. **Entrypoint Dynamique** : Le frontend utilise un script `docker-entrypoint.sh` qui choisit entre `nginx.dev.conf` et `nginx.prod.conf` au moment du démarrage selon la valeur de `ENV`.
2. **Attente de la Base de Données (Wait-for-DB)** : Les APIs utilisent `pg_isready` (via le paquet `postgresql-client`) dans leur `docker-entrypoint.sh`. Cela garantit que l'application ne tente pas de lancer les migrations Alembic avant que PostgreSQL ne soit totalement prêt à accepter des connexions.
3. **Séparation des Secrets** : Les fichiers `.env.dev` et `.env.prod` permettent de ne pas mélanger les accès de test avec les accès sécurisés.
4. **Zéro Suppression** : Toute la logique SSL a été conservée. Elle est simplement rendue conditionnelle pour faciliter les démos locales.
5. **Idempotence** : Les scripts de démarrage nettoient les anciens conteneurs avant de relancer l'infra.

---

## 5. Accès aux Services

* **Frontend (DEV)** : [http://localhost:8082](http://localhost:8082)
* **Frontend (PROD)** : [https://localhost:8443](https://localhost:8443)
* **Documentation API App** : [http://localhost:8000/docs](http://localhost:8000/docs)
* **Documentation API ML** : [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 6. Arrêt et Nettoyage Final

À la fin de votre démonstration ou de votre session de travail, voici comment tout couper proprement :

```bash
# Arrêt des conteneurs
docker stop frontend-vue api-app api-ml postgres-db

# Suppression des conteneurs
docker rm frontend-vue api-app api-ml postgres-db

# Suppression du réseau
docker network rm match-network
```

---

> [!NOTE]
> **Mentalité DevOps** : Ne jamais supprimer une configuration fonctionnelle, mais la rendre optionnelle ou configurable (Dev/Staging/Prod).
