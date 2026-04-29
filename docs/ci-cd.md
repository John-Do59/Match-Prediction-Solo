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

## Sécurité — Scan Trivy

Après chaque build, **Trivy** analyse l'image.
- Si une CVE **CRITICAL** ou **HIGH** est détectée → **le build échoue**.
- Le rapport est consultable dans l'onglet **Security** de GitHub.

---

## 💡 Retour d'Expérience : Incident "Missing SARIF"

**Date** : 29 Avril 2026
**Symptôme** : Échec de la pipeline à l'étape `Upload SARIF` avec l'erreur `Path does not exist: trivy-api-app.sarif`.

**Analyse** :
L'incident s'est produit lors d'une synchronisation de branche (`git pull`) où le workflow a été écrasé par une version simplifiée ne contenant plus l'étape de scan Trivy, alors que l'étape d'upload était toujours présente.

**Action Corrective (Implémentée)** :
1.  **Séquentialité forcée** : Le workflow a été restructuré pour garantir que le scan s'exécute *avant* l'upload.
2.  **Permissions explicites** : Ajout de `security-events: write` dans les permissions du job.
3.  **Build Local d'abord** : Utilisation de `load: true` dans `build-push-action` pour que l'image soit accessible localement au scanner Trivy avant d'être envoyée sur le registre.

---

## Optimisations Cache

La pipeline utilise le cache GitHub Actions (`type=gha`) pour réduire le temps de build de ~4min à ~30s.

---

## Tagging des Images

| Contexte | Tag généré |
| :--- | :--- |
| Push sur `main` | `latest` + `sha-xxxxxxx` |
| Push sur `develop` | `develop` + `sha-xxxxxxx` |
| Pull Request | `pr-XX` |
