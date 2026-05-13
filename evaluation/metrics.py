"""
Metrics

Shared evaluation functions for comparing the three approaches.
Called by run_experiments.py to produce result tables and plots.
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

    hard_violations: int
    soft_score: float
    is_valid: bool

    runtime_seconds: float
    iterations: Optional[int] = None

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
    """Run solver_fn on problem, measure time, and return all evaluation metrics."""
    checker = ConstraintChecker(problem)

    start    = time.perf_counter()
    schedule = solver_fn(problem)
    elapsed  = time.perf_counter() - start

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
