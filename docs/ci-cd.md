# Pipeline CI/CD — Docker Build, Scan & Publish

## Vue d'ensemble

Le pipeline GitHub Actions automatise **4 étapes** à chaque push sur `develop` ou `main` :

```
Push / PR
    │
    ▼
① Checkout + Login GHCR
    │
    ▼
② Build Multi-Stage (avec cache GHA)
    │
    ▼
③ Scan Trivy (CVE CRITICAL/HIGH → bloque)
    │
    ▼
④ Push vers GHCR (uniquement sur push, pas sur PR)
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

## Optimisations Cache

La pipeline utilise le **cache GitHub Actions** (`type=gha`) pour éviter de reconstruire les layers Docker identiques entre deux builds.

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

- **`cache-from`** : Tente de récupérer les layers depuis le cache GHA.
- **`cache-to: mode=max`** : Sauvegarde tous les layers intermédiaires (y compris le stage `builder`), pas seulement le final.

**Impact concret** : Un re-build sans changement de dépendances passe de ~4min à ~30s.

---

## Sécurité — Scan Trivy

Après chaque build, **Trivy** analyse l'image à la recherche de CVE (Common Vulnerabilities and Exposures).

```yaml
exit-code: '1'
severity: 'CRITICAL,HIGH'
ignore-unfixed: true
```

- Si une CVE **CRITICAL** ou **HIGH** est détectée ET qu'un patch existe → **le build est bloqué**.
- `ignore-unfixed: true` évite les faux positifs pour les vulnérabilités sans correctif disponible.
- Le rapport SARIF est uploadé dans l'onglet **Security → Code scanning** du repo GitHub.

---

## Tagging des Images

| Contexte | Tag généré |
| :--- | :--- |
| Push sur `main` | `latest` + `sha-xxxxxxx` |
| Push sur `develop` | `develop` + `sha-xxxxxxx` |
| Pull Request | `pr-42` |
| Tag Git `v1.2.3` | `1.2.3` |

---

## Prérequis

- **Aucun secret à configurer manuellement** : Le token `GITHUB_TOKEN` est injecté automatiquement par GitHub Actions.
- **Permissions** : Le workflow déclare `packages: write` et `security-events: write`.
