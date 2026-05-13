# Course Schedule Planner — INFO-H410 Project

A comparison of three AI techniques applied to the **university course scheduling problem**:

- **Approach A**: Constraint Satisfaction Problem (CSP) with Backtracking + Forward Checking
- **Approach B**: Local Search with Simulated Annealing
- **Approach C**: Reinforcement Learning with Q-Learning

## Problem

Given a set of courses, professors, rooms, and time slots, find a valid schedule that satisfies all hard constraints and maximizes soft constraint satisfaction.

## Project Structure

```
course_scheduler/
├── core/
│   ├── problem.py              # CourseScheduleProblem — shared data model
│   ├── schedule.py             # Schedule — schedule representation
│   ├── constraints.py          # ConstraintChecker — hard/soft constraint evaluation
│   └── instance_generator.py  # Random instance generator
├── approaches/
│   ├── csp_solver.py           # Approach A: CSP + Backtracking + MRV/LCV/FC
│   ├── csp_solver_timeout.py   # Approach A (Anytime): continues after first solution
│   ├── local_search.py         # Approach B: Hill Climbing + Simulated Annealing
│   └── q_learning.py           # Approach C: Q-Learning
├── evaluation/
│   ├── metrics.py              # Shared evaluation metrics
│   ├── run_experiments.py      # Run all approaches and generate comparison plots
│   ├── results.csv             # Output: per-instance results table
│   └── plots/                  # Output: generated graphs (soft score, time, violations)
├── data/
│   ├── instance_05.json        # 5 courses, 3 professors, 3 rooms
│   ├── instance_15.json        # 15 courses, 6 professors, 5 rooms
│   ├── instance_30.json        # 30 courses, 10 professors, 8 rooms
│   ├── instance_60.json        # 60 courses, 15 professors, 8 rooms
│   ├── instance_100.json       # 100 courses, 20 professors, 8 rooms
│   ├── instance_125.json       # 125 courses, 25 professors, 8 rooms
│   └── instance_150.json       # 150 courses, 30 professors, 8 rooms
├── Rapport/
│   ├── INFO-H410_Groupe9.tex   # Latex report
│   ├── INFO-H410_Groupe9.pdf   # PDF compiled report
│   ├── presentation_groupe9.tex  # Presentation slides
│   ├── presentation_groupe9.pdf  # Compiled slides
│   └── references.bib          # Bibliography
├── .gitignore
├── requirements.txt
├── plan_de_travail.md
└── README.md
```

## Setup & Reproducibility

```bash
# 1. Clone the repo
git clone https://github.com/BurakSogutlu/Project-TAI-25-26-course_scheduler.git
cd Project-TAI-25-26-course_scheduler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate test instances (or use pre-generated ones in data/)
python -m core.instance_generator

# 4. Run full comparison experiments (all approaches, all instances)
python evaluation/run_experiments.py

# 5. Run a quick test for a specific approach (from project root)
python -m approaches.local_search
python -m approaches.q_learning
```

## Dependencies

See `requirements.txt`. Python 3.9+ recommended.

## Authors

- Burak Sogutlu
- Grégoire Van den Eynde
- Urielle Nkwinga
- Nassim Machichi

## Course

INFO-H410 — Techniques of Artificial Intelligence  
MA1 Ingénieur Civil — Université Libre de Bruxelles, 2025–2026  
Groupe 9
