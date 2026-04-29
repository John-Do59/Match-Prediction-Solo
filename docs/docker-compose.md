# Infrastructure Docker Compose (Profiles & Networks)

## Architecture Réseau

Nous utilisons deux réseaux isolés :
-   **`frontend-network`** : Pour le trafic Web (Traefik, Frontend, API).
-   **`backend-network`** : Pour la communication privée API ◄──► Base de données.

---

## Profils d'Utilisation

L'utilisation des **Docker Profiles** permet de basculer d'un environnement à l'autre sans changer de fichier.

### 🛠️ Mode Développement (DEV)
Utilise le profil `dev`. Le frontend est exposé directement sur le port **8083**.
```bash
cp .env.dev .env
docker compose --profile dev up --build
```

### 🌍 Mode Production (PROD)
Utilise le profil `prod`. Le trafic passe par **Traefik** avec SSL activé.
```bash
cp .env.prod .env
docker compose --profile prod up --build
```

---

## Gestion des Données (Volumes)

-   `postgres_app_data` : Données de l'API principale.
-   `postgres_ml_data` : Données de l'API Machine Learning.

Pour réinitialiser complètement les bases de données :
```bash
docker compose down -v
```

---

## Reverse Proxy (Traefik)

En mode production, Traefik sert de point d'entrée unique. Il gère :
-   La redirection automatique HTTP → HTTPS.
-   Le routage vers le frontend et les APIs.
-   Le tableau de bord (Dashboard) accessible sur le port 8080 (en local).
