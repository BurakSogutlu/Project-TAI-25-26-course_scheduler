"""
Local Search

Two approaches to course scheduling via neighbourhood search:
Hill Climbing (greedy) and Simulated Annealing (probabilistic acceptance).
Both start from a random complete assignment and iteratively improve it.
"""

import math
import random
import time
from core.problem import CourseScheduleProblem
from core.schedule import Schedule
from core.constraints import ConstraintChecker


def resoudre_hill_climbing(probleme: CourseScheduleProblem, iterations=50):
    checker = ConstraintChecker(probleme)

    # Random initial schedule (may violate constraints)
    schedule = Schedule(probleme)
    for course in probleme.courses:
        schedule.assign(course, random.choice(probleme.timeslots), random.choice(probleme.rooms))

    current_score = checker.objective(schedule)
    print(f"Hill Climbing — initial score: {current_score:.4f}")

    for _ in range(iterations):
        if random.random() < 0.5:
            c = random.choice(probleme.courses)
            neighbour = schedule.move_neighbour(c, random.choice(probleme.timeslots), random.choice(probleme.rooms))
        else:
            c1, c2 = random.sample(probleme.courses, 2)
            neighbour = schedule.swap_neighbour(c1, c2)

        neighbour_score = checker.objective(neighbour)
        if neighbour_score >= current_score:
            schedule      = neighbour
            current_score = neighbour_score

    print(f"Hill Climbing — final score: {current_score:.4f}")
    return schedule, current_score


def resoudre_local_search(probleme: CourseScheduleProblem, iterations=4000):
    checker = ConstraintChecker(probleme)

    # Random initial schedule (may violate constraints)
    schedule = Schedule(probleme)
    for course in probleme.courses:
        schedule.assign(course, random.choice(probleme.timeslots), random.choice(probleme.rooms))

    current_score = checker.objective(schedule)
    best_schedule = schedule.copy()
    best_score    = current_score

    # Simulated Annealing parameters
    temperature  = 10.0
    cooling_rate = 0.995

    print(f"Simulated Annealing — initial score: {current_score}")

    for i in range(iterations):
        if random.random() < 0.5:
            c = random.choice(probleme.courses)
            neighbour = schedule.move_neighbour(c, random.choice(probleme.timeslots), random.choice(probleme.rooms))
        else:
            c1, c2 = random.sample(probleme.courses, 2)
            neighbour = schedule.swap_neighbour(c1, c2)

        neighbour_score = checker.objective(neighbour)
        delta           = neighbour_score - current_score

        # Accept improvements immediately; accept worse moves with probability e^(delta/T)
        if delta > 0 or (temperature > 0 and random.random() < math.exp(delta / temperature)):
            schedule      = neighbour
            current_score = neighbour_score

            if current_score > best_score:
                best_schedule = schedule.copy()
                best_score    = current_score

        temperature *= cooling_rate

        if i % 1000 == 0:
            print(f"Iteration {i}: score = {current_score:.2f}")

    return best_schedule, best_score


def solve(problem: CourseScheduleProblem, iterations=4000) -> Schedule:
    """Entry point called by evaluation/metrics.py."""
    schedule, _ = resoudre_local_search(problem, iterations=iterations)
    return schedule


if __name__ == "__main__":
    chemin  = "data/instance_15.json"
    problem = CourseScheduleProblem.from_json(chemin)

    start_hc = time.time()
    _, score_hc = resoudre_hill_climbing(problem, iterations=1000)
    time_hc = time.time() - start_hc

    start_sa = time.time()
    _, score_sa = resoudre_local_search(problem)
    time_sa = time.time() - start_sa

    print("\nComparison")
    print(f"Hill Climbing:       score = {score_hc:.2f}, time = {time_hc:.2f}s")
    print(f"Simulated Annealing: score = {score_sa:.2f}, time = {time_sa:.2f}s")
