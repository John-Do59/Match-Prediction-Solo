# Guide Docker Multi-Environnement (DEV & PROD)

Ce projet supporte deux environnements distincts pilotés par la variable `ENV`.

---

## 1. Choix de l'Environnement

Nous utilisons deux fichiers de configuration séparés :
*   `.env.dev` : Pour le développement local (simple, HTTP uniquement).
*   `.env.prod` : Pour la production (sécurisé, HTTPS obligatoire).

---

## 2. Méthode Automatisée (Recommandée)

Deux scripts sont à votre disposition pour lancer tout l'écosystème d'un coup :

### Mode DEV (Démonstration locale)
*   **Port** : [http://localhost:8082](http://localhost:8082)
*   **Sécurité** : SSL désactivé, secrets par défaut.
```bash
./scripts/start-dev.sh
```

### Mode PROD (Simulation de production)
*   **Port** : [https://localhost:8443](https://localhost:8443)
*   **Sécurité** : SSL activé (nécessite le dossier `ssl/`), secrets renforcés.
```bash
./scripts/start-prod.sh
```

---

## 3. Méthode Manuelle (Pas à pas)

Si vous préférez lancer les conteneurs un par un, voici la logique à suivre.

### Étape A : Création du réseau
```bash
docker network create match-network
```

### Étape B : Lancer la Base de Données
```bash
docker run -d --name postgres-db --network match-network -v postgres_data:/var/lib/postgresql/data -e POSTGRES_USER=amaury -e POSTGRES_PASSWORD=password -e POSTGRES_DB=footballapp_db -p 5432:5432 postgres:15
```

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

---

## 4. Choix Techniques & Mentalité DevOps

1.  **Entrypoint Dynamique** : Le frontend utilise un script `docker-entrypoint.sh` qui choisit entre `nginx.dev.conf` et `nginx.prod.conf` au moment du démarrage selon la valeur de `ENV`.
2.  **Séparation des Secrets** : Les fichiers `.env.dev` et `.env.prod` permettent de ne pas mélanger les accès de test avec les accès sécurisés.
3.  **Zéro Suppression** : Toute la logique SSL a été conservée. Elle est simplement rendue conditionnelle pour faciliter les démos locales.
4.  **Idempotence** : Les scripts de démarrage nettoient les anciens conteneurs avant de relancer l'infra.

---

## 5. Accès aux Services

*   **Frontend (DEV)** : [http://localhost:8082](http://localhost:8082)
*   **Frontend (PROD)** : [https://localhost:8443](https://localhost:8443)
*   **Documentation API App** : [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Documentation API ML** : [http://localhost:8001/docs](http://localhost:8001/docs)
