# Course Schedule Planner — INFO-H410 Project

A comparison of three AI techniques applied to the **university course scheduling problem**:

- **Approach A**: Constraint Satisfaction Problem (CSP) with Backtracking + AC-3
- **Approach B**: Local Search with Simulated Annealing
- **Approach C**: Reinforcement Learning with Q-Learning

## Problem

Given a set of courses, professors, rooms, and time slots, find a valid schedule that satisfies all hard constraints and maximizes soft constraint satisfaction.

## Project Structure

```
course_scheduler/
├── core/
│   ├── problem.py          # CourseScheduleProblem — shared data model
│   ├── schedule.py         # Schedule — schedule representation
│   ├── constraints.py      # ConstraintChecker — hard/soft constraint evaluation
│   └── instance_generator.py  # Random instance generator (small/medium/large)
├── approaches/
│   ├── csp_solver.py       # Approach A: CSP + Backtracking + AC-3 (P2)
│   ├── local_search.py     # Approach B: Hill Climbing + Simulated Annealing (P3)
│   └── q_learning.py       # Approach C: Q-Learning (P4)
├── evaluation/
│   ├── metrics.py          # Shared evaluation metrics
│   └── run_experiments.py  # Run all approaches and generate comparison plots
├── data/
│   ├── small_instance.json   # 5 courses, 3 professors, 3 rooms
│   ├── medium_instance.json  # 15 courses, 6 professors, 5 rooms
│   └── large_instance.json   # 30 courses, 10 professors, 8 rooms
├── .gitignore
├── requirements.txt
├── plan_de_travail.md
└── README.md
```

## Setup & Reproducibility

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/course-scheduler-ai.git
cd course_scheduler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate test instances (or use pre-generated ones in data/)
python core/instance_generator.py

# 4. Run a specific approach
python approaches/csp_solver.py --instance data/small_instance.json
python approaches/local_search.py --instance data/medium_instance.json
python approaches/q_learning.py --instance data/small_instance.json

# 5. Run full comparison experiments
python evaluation/run_experiments.py
```

## Dependencies

See `requirements.txt`. Python 3.9+ recommended.

## Authors

- Burak Sogutlu (architecture, problem formulation, evaluation)
- Gregoire Van den Eynde (CSP approach)
- Urielle Nkwinga (Local Search approach)
- Nasssim Machichi (Q-Learning approach)

## Course

INFO-H410 — Techniques of Artificial Intelligence
MA1 Ingénieur Civil — Université Libre de Bruxelles, 2025–2026
