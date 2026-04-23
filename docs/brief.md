# Brief projet – MVP Ia entrepreneurial

FastAPI • DTOs • Validation • Tests automatisés
Durée : 5 semaines

## 🎯 Finalité du brief
Ce projet vise à revoir et mobiliser l’ensemble des compétences techniques et transversales abordées depuis le début du parcours.
Le sujet est libre, mais doit respecter les contraintes imposées.

## Situation professionnelle
Concevoir et déployer un MVP intégrant un modèle de classification en environnement startup.

### 👤 Rôle professionnel visé
Développeur·se en Intelligence Artificielle travaillant en équipe produit dans une startup early-stage.

### 🎯 Besoin / Problématique
Suite à un brainstorming produit, votre équipe identifie un problème réel pouvant être résolu par un modèle de classification supervisée.
Vous devez :
- Valider la faisabilité technique
- Démontrer la pertinence métier
- Produire un MVP permettant de tester l’appétence marché

Vous êtes autonomes sur le choix du domaine.

**Exemples de projets possibles :**
- Développer un outil prédictif capable de classifier le risque de churn client à partir de données CRM et de données publiques économiques.
- Concevoir un service capable de classifier des annonces immobilières frauduleuses en croisant API publique et scraping de plateformes.

## Contexte Du Projet
Vous êtes une équipe fondatrice (3–4 personnes).
Vous devez :
- Partir d’une idée problème
- Construire un Lean Canvas
- Définir des Epics
- Rédiger minimum 15 User Stories
- Développer un MVP complet

## Contraintes Obligatoires
Le projet doit intégrer :
- **Modèle de classification obligatoire**
- Vous devez trouver et récupérer au minimum **2 sources de données externes de types différents** qui permet d’apporter une solution à votre problème choisi (API, Fichier, Scraping)
- Base de données, API REST, Application (back + front)
- bdd + API pour la partie données et modèle (entraînement, inférence…)
- bdd + API pour la partie données et modèle différente de la partie application. 
- Suite de tests automatisés

### Data Engineering:
- Collecte multi-source
- Nettoyage
- Normalisation
- Stockage

### Modélisation :
- Feature engineering
- Entraînement modèle
- Évaluation métriques
- Packaging

### API & Application :
- API REST sécurisée
- Intégration modèle
- Front minimal fonctionnel
- Tests d’intégration

## Organisation & Planning (5 semaines)

A chaque sprint des applications fonctionnelles en mode Agile (pas comme découpage)
- **Sprint 0** – Cadrage & Architecture
  - Lean Canvas
  - Spécifications fonctionnelles (Epics et US)
  - Architecture technique
  - Setup projet et Git
- **Sprint 1**
- **Sprint 2**
- **Sprint 3**
- **Semaine 5** – MEP & Soutenance
  - Documentation complète
  - Démo produit

## Modalités Pédagogiques
- Équipe de 3–4
- Méthode agile (rituels obligatoires)
- PO & Scrum Master tournants
- Sprint planning & démo avec formateurs
- Daily et autres rituels en autonomie
- Revues de code hebdomadaires
- Soutenance finale type comité produit

## Livrables Attendus
- Lean Canvas
- Backlog (Epics + US)
- Code versionné (Git propre)
- README structuré
- Documentation API (OpenAPI)
- Slides :
  - vision produit
  - architecture
  - démonstration live
- Daily summary
- Rapport d’évaluation modèle

## Critères De Performance
Les critères sont observables, mesurables et sans ambiguïté.

### Cadrage & Produit
- Le problème est clairement défini et corrélé à une cible précise.
- Le Lean Canvas est cohérent.
- Les US respectent le formalisme.
- Les Epics structurent logiquement le backlog.

### Data Engineering
- Les 2 sources de données sont effectivement exploitées.
- Les scripts d’extraction sont versionnés.
- Les données sont nettoyées et normalisées.
- La base est fonctionnelle.

### Modèle ML
- Modèle de classification implémenté.
- Métriques pertinentes présentées (accuracy + recall minimum).
- Pipeline reproductible.
- Modèle sauvegardé et versionné.

### API
- Authentification fonctionnelle.
- Endpoint entraînement opérationnel.
- Endpoint prédiction opérationnel.
- Documentation OpenAPI complète.

### Application
- Interface fonctionnelle.
- Interaction réelle avec API.
- Gestion des erreurs implémentée.
- Tests couvrant les endpoints critiques.
- Tests automatisés exécutés.

### Qualité globale
- Architecture cohérente.
- Code structuré.
- README permettant installation en <15 min.
- Démo fluide.

## Modalités D’évaluation
- Évaluation continue (revue sprint)
- Évaluation finale :
  - Démonstration live (20 min)
  - Questions techniques
  - Soutenance produit

## Ressources Disponibles
- Template Lean Canvas
- Template backlog Scrum
- Documentation Scikit-learn
- OpenAPI Specification
- Documentation FastAPI
- Guide tests pytest

---
**Notes additionnelles :**
- 13 personnes : 3 équipes
- micro SaaS
- story mapping
- Epic et US (INVEST)
- DOR / DOD
- Objectif de sprint
- Sprint planning
- Daily
