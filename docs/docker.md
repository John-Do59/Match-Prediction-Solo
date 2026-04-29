# Docker — Architecture & Bonnes Pratiques (Hardened)

## Multi-Stage Builds

Nous utilisons des **builds multi-stage** pour garantir des images légères (~180MB au lieu de ~800MB) et sécurisées.

### Structure Type
1.  **Stage Builder** : Installe les outils de compilation (gcc, libpq-dev) et compile les packages Python.
2.  **Stage Runtime** : Copie uniquement les packages compilés. Ne contient aucun outil de compilation, réduisant la surface d'attaque.

---

## Sécurité & Hardening

1.  **Utilisateur Non-Root** : Tous les conteneurs tournent avec `appuser` (UID 1000). Même en cas de faille, l'attaquant n'a pas les droits root sur le système hôte.
2.  **Scan de Vulnérabilités** : Intégration de **Trivy** dans la CI/CD pour bloquer les CVE critiques.
3.  **Images de Base** : Utilisation de `python:3.12-slim` et `nginx:stable-alpine`.
4.  **Isolation Réseau** : Les bases de données sont placées sur un réseau privé (`backend-network`) et ne sont pas exposées sur l'hôte.

---

## Optimisation du Cache

L'ordre des instructions dans les Dockerfiles est optimisé :
- Les fichiers `requirements.txt` sont copiés et installés **avant** le code source.
- Résultat : Si vous changez une ligne de code, Docker réutilise le cache pour les dépendances (gain de temps massif).

---

## Healthchecks

Chaque conteneur possède une instruction `healthcheck`. Docker Compose attend qu'une base de données soit "Healthy" avant de démarrer l'API qui en dépend.
