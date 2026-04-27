# Plan de Travail — Projet INFO-H410

## Planification d'Horaires de Cours avec Contraintes

### Ce qu'exige le projet

> **3 approches distinctes** sur le même problème, avec :
>
> - Formulation formelle du problème (état, variables, contraintes)
> - Implémentation Python
> - Évaluation expérimentale (métriques, tableaux, graphes)
> - Comparaison qualitative (forces/faiblesses)
> - Rapport AAAI 4 pages max + GitHub + présentation orale
> - **Date limite : 17 mai 2026**

### Grille d'évaluation (10 points)

| Critère                  | Points |
| ------------------------- | ------ |
| Problem Formulation       | 2 pts  |
| Methodological Approaches | 2 pts  |
| Experimental Evaluation   | 2 pts  |
| Qualitative Comparison    | 2 pts  |
| Technical Quality         | 1 pt   |
| Report Quality            | 1 pt   |

---

## 2. Définition du Problème : Course Schedule Planning

### Description du problème

Planifier automatiquement les horaires de cours d'une université en respectant un ensemble de contraintes, et en optimisant la qualité du planning.

### Formulation formelle

**Variables** : `C_ij` = cours i assigné au créneau j (jour × heure × salle)

**Contraintes (hard constraints)** :

- Un professeur ne peut pas enseigner deux cours en même temps
- Une salle ne peut pas accueillir deux cours simultanément
- La capacité de la salle doit être suffisante pour le nombre d'inscrits
- Un étudiant ne peut pas avoir deux cours obligatoires en même temps
- Respect des créneaux autorisés par professeur

**Contraintes douces (soft constraints / objectifs)** :

- Minimiser les "trous" dans l'emploi du temps des étudiants
- Équilibrer la charge journalière
- Respecter les préférences horaires des professeurs

### Les 3 approches IA

| Approche                                           | Technique                                                          | Cours                                                                                                   |
| -------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| **A — CSP + Backtracking**                  | Constraint Satisfaction Problem avec arc-consistency (AC-3) et MRV | Lecture 3 et TP 2 |
| **B — Local Search (Simulated Annealing)**  | Hill climbing + Simulated Annealing sur les contraintes douces     | Lecture 3                        |
| **C — Reinforcement Learning (Q-Learning)** | Q-Learning avec feature-based representation                       | Lecture 6 et TP 6     |

---

## 3. Répartition des Tâches

### Vue d'ensemble

```
PHASE 0 (Semaine 0) : Préparation
  └── [BURAK] Recherche, lecture du cours, élaboration du plan et répartition

PHASE 1 (Semaine 1-2) : Fondations
  ├── [BURAK] Formulation + Architecture générale + GitHub
  ├── [Gregoire]    Approche A : CSP
  ├── [Urielle
]    Approche B : Local Search
  └── [Nasssim]    Approche C : Modélisation RL

PHASE 2 (Semaine 2-3) : Développement 
  ├── [BURAK] Évaluation expérimentale + métriques
  ├── [Gregoire]    Finalisation CSP + tests
  ├── [Urielle
]    Finalisation Simulated Annealing + tests
  └── [Nasssim]    Finalisation Q-Learning + tests

PHASE 3 (Semaine 4) : Intégration + Rapport 
  └── [TOUS] Rapport AAAI + Présentation orale
```

---

## 4. Description Détaillée des Tâches par Personne

---

### BURAK — Architecte & Évaluateur

> **Rôle** : Chef de projet, architecte de la solution, responsable de l'évaluation comparative.

#### T1.0 — Recherche et Planification *(Semaine 0)*

- Lecture approfondie du cours (slides, TPs, énoncé du projet)
- Analyse des exigences et définition des 3 approches d'IA
- Élaboration du plan de travail, structuration du projet
- Répartition des tâches dans le groupe

#### T1.1 — Formulation formelle du problème *(Semaine 1)*

- Définir précisément l'espace d'états, les variables, les domaines
- Rédiger la section "Problem Formulation" du rapport
- Définir les instances de test (petite, moyenne, grande)
- Créer le générateur d'instances aléatoires

#### T1.2 — Architecture commune du code et GitHub *(Semaine 1)*

- Créer le repo GitHub avec structure claire, `.gitignore` et `requirements.txt`
- Collecter/générer des données réalistes
- Implémenter les classes de base partagées :
  - `CourseScheduleProblem` (données du problème)
  - `Schedule` (représentation d'un planning)
  - `ConstraintChecker` (vérification des contraintes)
- Définir les métriques d'évaluation communes

#### T1.3 — Évaluation expérimentale comparative *(Semaine 3)*

- Concevoir les expériences (instances variées, métriques)
- Exécuter les 3 approches sur les mêmes instances
- Générer les tableaux et graphiques de comparaison (matplotlib)
- Analyser les résultats : temps de calcul, qualité, scalabilité

#### T1.4 — Rapport + Présentation *(Semaine 4)*

- Rédiger la comparaison qualitative (forces/faiblesses)
- Assembler le rapport AAAI format (LaTeX)
- Préparer la présentation orale

---

### Gregoire — Approche A : CSP + Backtracking

> **Rôle** : Implémenter la solution basée sur les Constraint Satisfaction Problems — directement inspirée du TP 2 (Course Scheduling).

#### T2.1 — Modélisation CSP *(Semaine 1)*

- Définir les variables CSP (cours → créneau)
- Définir les domaines (liste de tous les créneaux possibles)
- Encoder toutes les contraintes binaires et unaires
- Dessiner le graphe de contraintes

#### T2.2 — Implémentation CSP *(Semaine 2)*

- Implémenter l'algorithme de backtracking
- Ajouter l'arc-consistency (AC-3)
- Implémenter MRV (Minimum Remaining Values) comme heuristique
- Implémenter Degree Heuristic et Least Constraining Value

#### T2.3 — Tests et optimisation CSP *(Semaine 3)*

- Tester sur toutes les instances (petite/moyenne/grande)
- Mesurer temps de calcul et qualité de la solution
- Optimiser si nécessaire (forward checking)
- Rédiger la section "Approche A" du rapport

---

### Urielle — Approche B : Local Search (Simulated Annealing)

> **Rôle** : Implémenter la solution basée sur la recherche locale — traite mieux les soft constraints que le CSP pur.

#### T3.1 — Modélisation Local Search *(Semaine 1)*

- Définir la représentation d'un état (planning complet)
- Définir la fonction d'évaluation / fitness (heuristique de qualité)
- Définir les opérateurs de voisinage (swap de 2 cours, déplacement d'un cours)

#### T3.2 — Implémentation Simulated Annealing *(Semaine 2)*

- Implémenter Hill Climbing basique (baseline)
- Implémenter Simulated Annealing avec schedule de température
- Paramétrer : température initiale, facteur de refroidissement, critère d'arrêt
- Implémenter restart aléatoire pour échapper aux optima locaux

#### T3.3 — Tests et tuning *(Semaine 3)*

- Tester et comparer Hill Climbing vs Simulated Annealing
- Tuning des hyperparamètres (température, cooling rate)
- Mesurer temps + qualité + nombre de violations
- Rédiger la section "Approche B" du rapport

---

### Nasssim — Approche C : Q-Learning + Setup infra

> **Rôle** : Implémenter l'approche Q-Learning (approche la plus originale et différenciante).

#### T4.1 — Modélisation RL *(Semaine 1)*

- Définir l'espace d'états MDP pour la planification
- Définir les actions (placer/déplacer un cours)
- Définir la fonction de récompense (violations = pénalité, planning valide = bonus)
- Choisir la représentation : features basées (comme TP 6 Ex. 3)

#### T4.2 — Implémentation Q-Learning *(Semaine 2)*

- Implémenter Q-Learning avec feature-based representation
- Gérer l'exploration vs exploitation (ε-greedy)
- Entraîner sur les instances générées
- Évaluer la politique apprise

#### T4.3 — Tests et analyse *(Semaine 3)*

- Courbes d'apprentissage (reward vs épisodes)
- Comparaison avant/après apprentissage
- Discussion sur les limites du RL pour ce type de problème
- Rédiger la section "Approche C" du rapport

---

## 5. Planning

```
Semaine 0
┌─────────────────────────────────────────────────────────────┐
│  BURAK: T1.0 Recherche, analyse du cours, plan de travail   │
└─────────────────────────────────────────────────────────────┘
                              ↓
Semaine 1 
┌─────────────────────────────────────────────────────────────┐
│  BURAK: T1.1 Formulation         │  BURAK: T1.2 Archi+GitHub│
│  Gregoire: T2.1 Modélisation CSP │  Urielle: T3.1 Modélisation SA │
│  Nasssim: T4.1 Modélisation RL   │                          │
└─────────────────────────────────────────────────────────────┘
                              ↓ 
Semaine 2 
┌─────────────────────────────────────────────────────────────┐
│  Gregoire: T2.2 Implémentation CSP                          │
│  Urielle: T3.2 Implémentation SA                            │
│  Nasssim: T4.2 Implémentation Q-Learning                    │
└─────────────────────────────────────────────────────────────┘
                              ↓ 
Semaine 3
┌─────────────────────────────────────────────────────────────┐
│  Gregoire: T2.3 Tests CSP → Rapport section A               │
│  Urielle: T3.3 Tests SA → Rapport section B                 │
│  Nasssim: T4.3 Tests QL → Rapport section C                 │
│  BURAK: T1.3 Évaluation comparative (après T2.3+T3.3+T4.3)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
Semaine 4 
┌─────────────────────────────────────────────────────────────┐
│  BURAK: T1.4 Rapport AAAI + Présentation orale              │
│  TOUS: Relecture croisée + révisions                        │
│  DEADLINE: 17 mai 2026                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Métriques d'Évaluation

Pour comparer les 3 approches de façon rigoureuse :

| Métrique                            | Description                                                        |
| ------------------------------------ | ------------------------------------------------------------------ |
| **Hard constraint violations** | Nombre de contraintes dures violées (idéalement 0)               |
| **Soft constraint score**      | Score pondéré des préférences satisfaites (plus = mieux)       |
| **Temps de calcul**            | Temps en secondes pour trouver une solution                        |
| **Scalabilité**               | Comportement quand le nombre de cours augmente (N=10, 20, 50, 100) |
| **Qualité de la solution**    | Score global du planning généré                                 |
| **Convergence**                | Pour RL : courbe d'apprentissage                                   |

---

## 7. Structure du Rapport (AAAI 4 pages)

```
Section 1 : Introduction + Problem Formulation (0.5 pages) → BURAK
Section 2 : Approche A — CSP (0.8 pages)               → Gregoire
Section 3 : Approche B — Local Search (0.8 pages)       → Urielle
Section 4 : Approche C — Q-Learning (0.8 pages)         → Nasssim
Section 5 : Évaluation expérimentale (0.5 pages)        → BURAK
Section 6 : Comparaison qualitative + Conclusion (0.6 pages) → BURAK
```

---
