"""
Metrics — Shared evaluation metrics 

All metrics used for comparing the three approaches.
Called by run_experiments.py to produce tables and plots.
"""

import time
from dataclasses import dataclass
from typing import Callable, Optional
from core.problem import CourseScheduleProblem
from core.schedule import Schedule
from core.constraints import ConstraintChecker


@dataclass
class EvaluationResult:
    """Stores all metrics for one approach on one instance."""
    approach_name: str
    instance_name: str
    n_courses: int

    # Solution quality
    hard_violations: int        # 0 = valid schedule
    soft_score: float           # [0, 1], higher is better
    is_valid: bool              # hard_violations == 0

    # Performance
    runtime_seconds: float
    iterations: Optional[int] = None    # for iterative approaches

    def __str__(self):
        status = "✓ VALID" if self.is_valid else f"✗ {self.hard_violations} violations"
        return (
            f"[{self.approach_name}] on {self.instance_name} ({self.n_courses} courses): "
            f"{status} | soft={self.soft_score:.3f} | time={self.runtime_seconds:.3f}s"
        )


def evaluate(
    approach_name: str,
    instance_name: str,
    problem: CourseScheduleProblem,
    solver_fn: Callable[[CourseScheduleProblem], Schedule],
) -> EvaluationResult:
    """
    Run a solver function and measure all metrics.

    Parameters

    approach_name : str
        Human-readable name of the approach (e.g. "CSP", "SA", "Q-Learning")
    instance_name : str
        Name of the test instance (e.g. "small", "medium", "large")
    problem : CourseScheduleProblem
        The problem instance to solve
    solver_fn : Callable
        A function (problem) -> Schedule

    Returns
    
    EvaluationResult with all metrics filled in
    """
    checker = ConstraintChecker(problem)

    start = time.perf_counter()
    schedule = solver_fn(problem)
    elapsed = time.perf_counter() - start

    hard = checker.hard_violations(schedule)
    soft = checker.soft_score(schedule) if hard == 0 else 0.0

    return EvaluationResult(
        approach_name=approach_name,
        instance_name=instance_name,
        n_courses=len(problem.courses),
        hard_violations=hard,
        soft_score=soft,
        is_valid=(hard == 0),
        runtime_seconds=elapsed,
    )
