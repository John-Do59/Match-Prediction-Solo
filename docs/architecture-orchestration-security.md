# Architecture, Orchestration & Sécurité : Dossier Technique

Ce document offre une vue d'ensemble du projet **Match Prediction App**, justifiant les choix techniques faits pour transformer une application locale en un système microservices "Production Ready".

---

## 1. Vision Globale de l'Architecture

Le projet est découpé en services spécialisés communiquant via un réseau privé virtuel :

- **Frontend (Vue.js + Nginx)** : Point d'entrée unique, gère le SSL et le routage.
- **API Application (FastAPI)** : Gère la logique métier, les utilisateurs et l'historique.
- **API ML (FastAPI + Scikit-Learn)** : Dédiée à l'ingestion de données et aux prédictions IA.
- **Bases de Données (Dual PostgreSQL)** : Instances isolées pour la sécurité et la performance.

---

## 2. Orchestration & Cycle de Vie (Docker Compose)

L'orchestration repose sur **Docker Compose**, qui assure la reproductibilité totale de l'environnement.

### Points Clés :
- **Dépendances de Santé (Healthchecks)** : Les APIs attendent que leurs bases de données respectives soient `healthy` (via `pg_isready`) avant de démarrer.
- **Entrypoint Automatisé** : Chaque backend exécute ses migrations Alembic au démarrage, garantissant que le schéma SQL est toujours en phase avec le code.
- **Volumes Persistants** : Séparation des données de base de données (`postgres_data`) et des datasets ML (`Data/`) montés en lecture seule pour l'IA.

---

## 3. Stratégie de Sécurité Multi-Couches

La sécurité a été implémentée à tous les niveaux de la stack :

### A. Sécurité Réseau & Infrastructure
- **Isolation des Services** : Seul le conteneur `frontend` expose des ports au monde extérieur (8082, 8443). Les bases de données et les APIs sont cachées dans le réseau interne Docker.
- **Utilisateur Non-Root** : Tous les conteneurs s'exécutent avec un utilisateur `appuser`, limitant les dégâts en cas d'intrusion.
- **CORS Restrictif** : L'API n'autorise que les domaines de confiance via des expressions régulières.

### B. Sécurité Inter-Services (Shared Token)
Pour éviter qu'un utilisateur ou un autre service malveillant ne sollicite directement l'API ML, nous avons implémenté un **Service Token** :
- L'API ML exige un header `X-Service-Token`.
- L'API App possède ce jeton et l'injecte dans chaque requête.
- Ce jeton est configurable via les variables d'environnement.

### C. Gestion des Secrets
- **Zéro Hardcoding** : Toutes les informations sensibles (DATABASE_URL, SECRET_KEY, SERVICE_TOKEN) sont extraites du fichier `.env`.
- **Validation Pydantic** : Les configurations sont validées au démarrage. Si un secret est manquant, l'application refuse de démarrer (fail-fast).

### D. Protection Applicative
- **Authentification JWT** : Utilisation de jetons sécurisés pour l'accès utilisateur.
- **Rate Limiting** : Protection contre le brute-force et le spam via `SlowAPI`.

---

## 4. Observabilité & Maintenance

- **Logs Structurés** : Les logs sont générés au format JSON, facilitant leur analyse par des outils modernes (ELK, Datadog).
- **Monitoring Docker** : Utilisation des `healthchecks` applicatifs permettant l'auto-récupération des services en cas de crash.

---

**Conclusion** : Cette architecture respecte les piliers du développement "Cloud Native" : isolation, sécurité par défaut et reproductibilité.
