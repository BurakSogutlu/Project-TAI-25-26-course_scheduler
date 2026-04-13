## Ce qui a été fait : T1.1 et T1.2

Tout le code commun partagé par les 3 approches a déjà été implémenté. 



## `core/problem.py`

Tout tourne autour de 4 classes de données simples :

| Classe | Description | Attributs clés |
|---|---|---|
| `TimeSlot` | Un créneau de **2 heures** | `day` (0=Lun…4=Ven), `hour` (8, 10, 14 ou 16) |
| `Room` | Une salle physique | `id`, `name`, `capacity` |
| `Professor` | Un enseignant | `id`, `available_slots`, `preferred_slots` |
| `Course` | Un cours à planifier | `id`, `name`, `professor_id`, `required_capacity` |

Le problème complet est contenu dans un objet `CourseScheduleProblem` :

```python
from core.problem import CourseScheduleProblem

# Charger depuis un fichier JSON
problem = CourseScheduleProblem.from_json("data/small_instance.json")

# Ce que vous pouvez utiliser :
problem.courses          # Liste de tous les cours à planifier
problem.professors       # Liste de tous les professeurs
problem.rooms            # Liste de toutes les salles
problem.timeslots        # Liste de tous les créneaux disponibles
problem.max_daily_courses  # Nb max de cours par jour (contrainte douce S3)

# Accès rapide par ID :
problem.professor_by_id["P_A"]   # Récupère l'objet Professor directement
problem.room_by_id["R1"]         # Récupère l'objet Room directement
problem.course_by_id["CS101"]    # Récupère l'objet Course directement

# Domaine d'un cours (utile pour le CSP) : toutes les (slot, room) valides
domain = problem.domain(course)  # Respecte H3 (capacité) et H4 (disponibilité)
```

---

## Représenter un planning — `core/schedule.py`

L'objet `Schedule` est le résultat. Il associe chaque cours à un créneau et une salle.

```python
from core.schedule import Schedule

schedule = Schedule(problem)

# Assigner un cours
schedule.assign(course, slot, room)

# Désassigner
schedule.unassign(course)

# Lire une assignation
slot, room = schedule.get(course)

# Vérifications
schedule.is_assigned(course)       # True/False
schedule.is_complete()             # True si tous les cours sont placés
schedule.unassigned_courses()      # Liste des cours pas encore placés

# Pour le Local Search — générer un voisin
new_schedule = schedule.swap_neighbour(course_a, course_b)  # Échange 2 cours
new_schedule = schedule.move_neighbour(course, new_slot, new_room)  # Déplace 1 cours

# Afficher le planning dans le terminal
schedule.pretty_print()
```

---

## Évaluer les contraintes — `core/constraints.py`

Toutes les contraintes y sont définies. A priori complet et rien à modifier.

```python
from core.constraints import ConstraintChecker

checker = ConstraintChecker(problem)
```

### Contraintes dures (H1–H4) — Doivent toutes être = 0

| Code | Règle |
|---|---|
| H1 | Un prof ne peut pas enseigner deux cours en même temps |
| H2 | Une salle ne peut pas accueillir deux cours en même temps |
| H3 | La salle doit avoir une capacité suffisante pour le cours |
| H4 | Le créneau doit être dans les disponibilités du prof |

### Contraintes douces (S1–S3) — Score entre 0 et 1 à maximiser

| Code | Règle |
|---|---|
| S1 | Le créneau choisi est dans les préférences horaires du prof |
| S2 | Aucun trou (créneau vide entre deux cours) dans la journée |
| S3 | Le nombre de cours par jour ne dépasse pas `max_daily_courses` |

### Fonctions disponibles

```python
# CSP — Vérification incrémentale sur planning partiel
# Renvoie True si ajouter ce cours à ce slot/room ne viole aucune contrainte dure
ok = checker.is_consistent(schedule, course, slot, room)

# Local Search — Compter les violations sur planning complet
n = checker.hard_violations(schedule)    # 0 = planning valide
score = checker.soft_score(schedule)     # 0.0 à 1.0 = qualité du planning

# Q-Learning — Récompense unique
# = -10 * violations_dures + soft_score (0 si violations > 0)
reward = checker.objective(schedule)
```

---
### CSP — `approaches/csp_solver.py` 

**Principe** : Pars d'un planning vide et place les cours un par un. Si une impasse est atteinte, reviens en arrière (Backtracking).

**Fonctions à utiliser principalement** :
- `problem.domain(course)` → les valeurs légales pour ce cours
- `checker.is_consistent(schedule, course, slot, room)` → pour couper les branches invalides
- `checker.soft_score(schedule)` → pour trier les valeurs (surrement doit faire une heuristique LCV)
- `schedule.assign(course, slot, room)` et `schedule.unassign(course)` → construire/défaire

---

### Local Search — `approaches/local_search_solver.py` 

**Principe** : Part d'un planning aléatoire mais complet (même s'il est bourré d'erreurs). À chaque itération, génère un voisin et décide de l'accepter ou non (selon la température du recuit simulé).

**Fonctions à utiliser principalement** :
- `checker.hard_violations(schedule)` → score à minimiser (viser 0)
- `checker.soft_score(schedule)` → score à maximiser ensuite (viser 1.0)
- `schedule.swap_neighbour(c1, c2)` → génère un voisin par échange
- `schedule.move_neighbour(c, slot, room)` → génère un voisin par déplacement

---

### Q-Learning — `approaches/ql_solver.py` 

**Principe** : Un agent apprend par essai-erreur à placer les cours. À chaque étape, il choisit une action (placer un cours dans un créneau/salle) et reçoit une récompense. Il met à jour sa Q-Table avec l'équation de Bellman.

**Fonctions à utiliser principalement** :
- `checker.objective(schedule)` → la récompense à maximiser
  - `-10` points par violation dure, `+soft_score` si aucune violation
- `problem.domain(course)` → les actions légales possibles
- `schedule.assign(course, slot, room)` → exécuter une action


---

## Tester

Une fois `solve()` implémenté, vous pouvez tester comme ça :

```python
from core.problem import CourseScheduleProblem
from core.constraints import ConstraintChecker
from approaches.csp_solver import CSPSolver  # ou votre fichier

# 1. Charger le problème
problem = CourseScheduleProblem.from_json("data/small_instance.json")

# 2. Résoudre
solver = CSPSolver(problem)
solution = solver.solve()

# 3. Vérifier
checker = ConstraintChecker(problem)
print(f"Violations dures : {checker.hard_violations(solution)}")  # Doit être 0
print(f"Score de confort : {checker.soft_score(solution):.3f}")   # Entre 0 et 1

# 4. Afficher le planning
solution.pretty_print()
```
