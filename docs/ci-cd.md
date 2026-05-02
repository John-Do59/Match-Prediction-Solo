# Pipeline CI/CD — Docker Build, Scan & Publish

## Vue d'ensemble

Le pipeline GitHub Actions automatise la construction, le scan de sécurité et la publication des images sur chaque push vers `develop` ou `main`.

```mermaid
graph TD
    A[Push / PR] --> B[Checkout + Login GHCR]
    B --> C[Build Multi-Stage (load: true)]
    C --> D[Scan Trivy (CVE CRITICAL/HIGH)]
    D --> E[Upload SARIF to GitHub Security]
    E --> F{Est-ce un Push?}
    F -- Oui --> G[Push final vers GHCR]
    F -- Non --> H[Fin (Validation PR)]
```

---

## Déclencheurs

| Événement | Action |
| :--- | :--- |
| `push` sur `develop` | Build + Scan + **Push** vers GHCR |
| `push` sur `main` | Build + Scan + **Push** vers GHCR + tag `latest` |
| `pull_request` vers `develop`/`main` | Build + Scan (pas de push) |

---

## Services buildés

Chaque service est buildé en parallèle via une **strategy matrix** :

| Service | Dockerfile | Image GHCR |
| :--- | :--- | :--- |
| `api-app` | `FastAPI_App/Dockerfile` | `ghcr.io/<org>/<repo>/api-app` |
| `api-ml` | `FastAPI_ML/Dockerfile` | `ghcr.io/<org>/<repo>/api-ml` |
| `frontend` | `match_prediction_app-front/Dockerfile` | `ghcr.io/<org>/<repo>/frontend` |

---

## Sécurité — Scan Trivy

Après chaque build, **Trivy** analyse l'image à la recherche de CVE.
- Si une CVE **CRITICAL** ou **HIGH** est détectée → **le build est bloqué**.
- Le rapport est consultable dans l'onglet **Security** de GitHub.

---

## 💡 Retour d'Expérience : Incident "Missing SARIF"

**Date** : 29 Avril 2026
**Symptôme** : Échec de la pipeline à l'étape `Upload SARIF` avec l'erreur `Path does not exist: trivy-api-app.sarif`.

**Analyse** :
L'incident s'est produit lors d'une synchronisation de branche (`git pull`) où le workflow a été écrasé par une version simplifiée ne contenant plus l'étape de scan Trivy.

**Action Corrective** :
- Restructuration du workflow (Build -> Scan -> Push).
- Ajout de `security-events: write`.
- Utilisation de `load: true` pour le scan local.

---

## 💡 Retour d'Expérience : Détection de CVE par Trivy (DoS Starlette & python-jose)

**Date** : 30 Avril 2026
**Symptôme** : Trivy a bloqué le pipeline en détectant deux vulnérabilités dans les dépendances Python :
1. **CVE-2024-47874 (HIGH)** : Déni de service (DoS) via `multipart/form-data` dans `starlette` (version 0.38.6).
2. **Vulnérabilité (CRITICAL)** : Faille potentielle d'injection d'algorithme dans `python-jose` (< 3.4.0).

**Analyse** :
Le scan SBOM de Trivy a correctement identifié que `fastapi==0.115.0` dépendait d'une version vulnérable de `starlette`. De plus, `python-jose` nécessitait une mise à jour de sécurité.

**Action Corrective** :
1. **Mise à jour des dépendances** : 
   - `fastapi` mis à jour vers `0.115.6` (ce qui tire une version patchée de `starlette`).
   - `python-jose` mis à jour vers `3.4.0` dans les fichiers `requirements.txt` et `requirements.prod.txt`.
2. **Audit du code** : Vérification du code source confirmant que l'application FastAPI utilisait **déjà** explicitement `algorithms=[settings.ALGORITHM]` lors des appels `jwt.decode()`, la protégeant nativement contre l'attaque par confusion d'algorithme.

---

## Optimisations Cache

La pipeline utilise le cache GitHub Actions (`type=gha`) pour réduire le temps de build (passage de ~4min à ~30s).
