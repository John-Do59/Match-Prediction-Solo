# Planification : Pipeline CI/CD (Intégration & Déploiement Continus)

Ce document détaille la stratégie de CI/CD prévue pour automatiser la qualité, les tests et le déploiement du projet **Match Prediction App**.

---

## 1. Objectifs de la CI/CD

- **Détection Précoce** : Identifier les bugs dès qu'une ligne de code est poussée.
- **Reproductibilité** : Garantir que les tests passent dans un environnement identique à la production.
- **Automatisation** : Éliminer les erreurs humaines lors de la construction des images Docker.

---

## 2. Le Workflow GitHub Actions (Prévu)

Le pipeline sera déclenché à chaque `push` ou `Pull Request` sur les branches `develop` et `main`.

### Étape 1 : Quality Gate (Linting & Style)
- **Outil** : `flake8` ou `black`.
- **But** : Vérifier que le code respecte les standards Python (PEP8).

### Étape 2 : Automated Testing (Unit & Integration)
- **Outil** : `pytest`.
- **Mécanisme** : 
  - Lancement d'un conteneur PostgreSQL éphémère.
  - Exécution des migrations Alembic.
  - Lancement des tests unitaires sur les APIs App et ML.

### Étape 3 : Docker Build & Scan
- **But** : Construire les images Docker des 3 services (App, ML, Front).
- **Sécurité** : Utilisation de `Trivy` ou `Snyk` pour scanner les images à la recherche de vulnérabilités connues (CVE).

### Étape 4 : Push to Registry (Optionnel)
- **But** : Pousser les images validées vers GitHub Container Registry (GHCR) ou Docker Hub.

---

## 3. Avantages pour le Projet de Groupe

L'implémentation de ce pipeline transforme votre workflow :
- Plus besoin de se demander "Est-ce que ça marche chez toi ?". Si le pipeline est au vert, le projet est fonctionnel.
- Sécurisation du code : Aucun code ne peut être fusionné sans avoir passé les tests.

---

**Statut actuel** : En attente d'implémentation sur la branche `feat/cicd-pipeline`.
