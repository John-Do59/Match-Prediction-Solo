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
* **Sécurité** : SSL activé (nécessite le dossier ssl/), secrets renforcés.

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

### Étape 1 : Nettoyage de l'Environnement (Requis avant chaque relancement)

Avant de lancer les conteneurs, vérifiez et nettoyez les éventuels résidus d'une session précédente.
Docker refusera de créer un conteneur si un conteneur du même nom existe déjà, même à l'état arrêté.

#### Vérifier ce qui existe déjà

```bash
# Voir les conteneurs actifs ET arrêtés
docker ps -a | grep -E "postgres-db|frontend-vue|api-app|api-ml"

# Voir si le réseau existe déjà
docker network ls | grep match-network
```

#### Nettoyer les conteneurs et le réseau

```bash
# Arrêt des conteneurs (si encore actifs)
docker stop frontend-vue api-app api-ml postgres-db 2>/dev/null; \
docker rm frontend-vue api-app api-ml postgres-db 2>/dev/null; \
docker network rm match-network 2>/dev/null; \
echo "✅ Environnement nettoyé, prêt pour un nouveau lancement"
```

> [!NOTE]
> Le `2>/dev/null` redirige les erreurs vers le néant. Cela évite les messages d'erreur si un conteneur ou le réseau n'existe pas encore — pratique pour une commande de nettoyage "à l'aveugle".

#### Faut-il supprimer le volume PostgreSQL ?

```bash
docker volume rm match_prediction_pg_data
```

| Situation | Supprimer le volume ? |
| :--- | :--- |
| Premier lancement absolu | ❌ Inutile (n'existe pas encore) |
| Repartir de zéro avec une base vierge | ✅ Oui |
| Conserver les données de la session précédente | ❌ Non |

### Étape 2 : Création du Réseau

```bash
docker network create match-network
```

### Étape 3 : Lancer la Base de Données

```bash
# Lancement via fichier d'environnement (Sécurisé)
docker run -d \
  --name postgres-db \
  --network match-network \
  -v match_prediction_pg_data:/var/lib/postgresql/data \
  -v "$(pwd)/scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql" \
  --env-file .env.dev \
  -p 5432:5432 \
  postgres:15
```

> [!IMPORTANT]
> **Fonctionnement de l'initialisation** : Le script `init-db.sql` ne s'exécute **que si le volume est neuf** (dossier `/var/lib/postgresql/data` vide). Si vous modifiez ce script, vous devez supprimer le volume (Étape 1) pour que les changements soient appliqués au prochain lancement.

### Étape 4 : Lancer le Frontend (Choix de l'ENV)

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

### Étape 5 : Lancer les APIs

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

### Étape 6 : Initialisation des Données

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

* **Entrypoint Dynamique** : Le frontend utilise un script `docker-entrypoint.sh` qui choisit entre `nginx.dev.conf` et `nginx.prod.conf` au moment du démarrage selon la valeur de `ENV`.
* **Attente de la Base de Données (Wait-for-DB)** : Les APIs utilisent `pg_isready` (via le paquet `postgresql-client`) dans leur `docker-entrypoint.sh`. Cela garantit que l'application ne tente pas de lancer les migrations Alembic avant que PostgreSQL ne soit totalement prêt à accepter des connexions.
* **Séparation des Secrets** : Les fichiers `.env.dev` et `.env.prod` permettent de ne pas mélanger les accès de test avec les accès sécurisés.
* **Zéro Suppression** : Toute la logique SSL a été conservée. Elle est simplement rendue conditionnelle pour faciliter les démos locales.
* **Idempotence** : Les scripts de démarrage nettoient les anciens conteneurs avant de relancer l'infra.

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

> [!NOTE]
> Si vous souhaitez également supprimer les données PostgreSQL pour repartir d'une base totalement vierge lors du prochain lancement :

```bash
docker volume rm match_prediction_pg_data
```
