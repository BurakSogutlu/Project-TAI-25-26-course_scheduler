"""
CSP Solver

Solves the course scheduling problem using backtracking search with
optional heuristics and filtering techniques.
"""

from collections import deque
from core.schedule import Schedule
from core.constraints import ConstraintChecker
from core.problem import CourseScheduleProblem, Course, TimeSlot, Room


class CSPSolver:
    """
    Backtracking solver with pluggable heuristics.

    use_mrv            : Minimum Remaining Values — pick the most constrained variable first
    use_degree         : Static Degree — fast tie-breaker based on shared professors, O(n)
    use_dynamic_degree : Dynamic Degree — exact current conflicts, O(n²s²)
    use_lcv            : Least Constraining Value — order values by how little they eliminate
    use_fc             : Forward Checking — detect dead ends early
    use_ac3            : AC-3 arc-consistency — stronger propagation between unassigned vars
    """

    def __init__(
        self, problem: CourseScheduleProblem, use_mrv: bool = False, use_degree: bool = False,
        use_dynamic_degree: bool = False, use_lcv: bool = False, use_fc: bool = False, use_ac3: bool = False,
    ):
        self.problem = problem
        self.checker = ConstraintChecker(problem)

        self.use_mrv            = use_mrv
        self.use_degree         = use_degree
        self.use_dynamic_degree = use_dynamic_degree
        self.use_lcv            = use_lcv
        self.use_fc             = use_fc
        self.use_ac3            = use_ac3

        self.backtrack_count: int = 0
        self.nodes_explored: int  = 0

    # AC-3

    def _is_arc_compatible(self, c1: Course, val1: tuple, c2: Course, val2: tuple) -> bool:
        """Return True if assigning val1 to c1 and val2 to c2 violates no binary hard constraint."""
        slot1, room1 = val1
        slot2, room2 = val2

        if slot1.overlaps(slot2):
            if c1.professor_id == c2.professor_id:
                return False
            if room1.id == room2.id:
                return False

        return True

    def _remove_inconsistent_values(self, domains: dict, Xi: Course, Xj: Course) -> bool:
        """Remove from domains[Xi] every value with no compatible counterpart in domains[Xj]."""
        removed = False
        for x in list(domains[Xi.id]):
            if not any(self._is_arc_compatible(Xi, x, Xj, y) for y in domains[Xj.id]):
                domains[Xi.id].remove(x)
                removed = True
        return removed

    def _ac3(self, unassigned: list, domains: dict) -> bool:
        """AC-3 arc-consistency. Returns False if any domain becomes empty."""
        queue = deque(
            (unassigned[i], unassigned[j])
            for i in range(len(unassigned))
            for j in range(len(unassigned))
            if i != j
        )

        while queue:
            Xi, Xj = queue.popleft()

            if self._remove_inconsistent_values(domains, Xi, Xj):
                if len(domains[Xi.id]) == 0:
                    return False

                for Xk in unassigned:
                    if Xk.id != Xi.id:
                        queue.append((Xk, Xi))

        return True

    # Variable selection heuristics

    def _mrv_score(self, course: Course, domains: dict) -> int:
        """Number of remaining valid values (lower = more constrained)."""
        return len(domains[course.id])

    def _static_degree_score(self, course: Course, unassigned: list) -> int:
        """Count unassigned courses sharing the same professor (negated for min())."""
        degree = sum(
            1 for other in unassigned
            if other.id != course.id and other.professor_id == course.professor_id
        )
        return -degree

    def _dynamic_degree_score(self, course: Course, unassigned: list, domains: dict) -> int:
        """
        Count real binary conflicts with other unassigned courses based on current domains.
        Two courses are connected if they share a professor (H1) or compete for a room on a
        common slot (H2). Negated so min() picks the most constrained course.
        """
        degree  = 0
        slots_c = {slot    for slot, room in domains[course.id]}
        rooms_c = {room.id for slot, room in domains[course.id]}

        for other in unassigned:
            if other.id == course.id:
                continue

            if other.professor_id == course.professor_id:
                degree += 1
                continue

            slots_o = {slot    for slot, room in domains[other.id]}
            rooms_o = {room.id for slot, room in domains[other.id]}

            if any(s1.overlaps(s2) for s1 in slots_c for s2 in slots_o) and (rooms_c & rooms_o):
                degree += 1

        return -degree

    def _select_variable(self, unassigned: list, domains: dict) -> Course:
        """Choose the next variable to assign: MRV → degree tie-breaker → natural order."""
        if self.use_mrv:
            if self.use_dynamic_degree:
                return min(
                    unassigned,
                    key=lambda c: (self._mrv_score(c, domains), self._dynamic_degree_score(c, unassigned, domains)),
                )
            elif self.use_degree:
                return min(
                    unassigned,
                    key=lambda c: (self._mrv_score(c, domains), self._static_degree_score(c, unassigned)),
                )
            else:
                return min(unassigned, key=lambda c: self._mrv_score(c, domains))

        if self.use_dynamic_degree:
            return min(unassigned, key=lambda c: self._dynamic_degree_score(c, unassigned, domains))
        if self.use_degree:
            return min(unassigned, key=lambda c: self._static_degree_score(c, unassigned))

        return unassigned[0]

    # Value ordering (LCV)

    def _lcv_score(self, course: Course, value: tuple, unassigned: list, domains: dict) -> int:
        """Count values this assignment would eliminate from neighbours' domains (lower is better)."""
        eliminated = 0
        for other in unassigned:
            if other.id == course.id:
                continue
            for other_val in domains[other.id]:
                if not self._is_arc_compatible(course, value, other, other_val):
                    eliminated += 1
        return eliminated

    # Backtracking

    def solve(self) -> "Schedule | None":
        """Run the search and return a complete Schedule, or None if unsatisfiable."""
        schedule = Schedule(self.problem)
        if self._backtrack(schedule):
            print(
                f"Solution found — {self.backtrack_count} backtracks, "
                f"{self.nodes_explored} nodes explored."
            )
            return schedule
        print("No solution found.")
        return None

    def _backtrack(self, schedule: Schedule) -> bool:
        """Recursive backtracking with all optional heuristics."""

        if schedule.is_complete():
            return True

        self.nodes_explored += 1
        unassigned = schedule.unassigned_courses()

        # Build current domains, applying FC/AC-3 early exit
        domains: dict = {}
        for c in unassigned:
            valid = [
                (slot, room)
                for slot, room in self.problem.domain(c)
                if self.checker.is_consistent(schedule, c, slot, room)
            ]
            domains[c.id] = valid

            if (self.use_fc or self.use_ac3) and len(valid) == 0:
                return False

        if self.use_ac3:
            if not self._ac3(unassigned, domains):
                return False

        course = self._select_variable(unassigned, domains)
        domain = domains[course.id]

        # Sort values by soft score first, then LCV as tie-breaker
        if self.use_lcv:
            def combined_value_score(value):
                slot, room = value
                schedule.assign(course, slot, room)
                s_score = self.checker.soft_score(schedule)
                schedule.unassign(course)
                lcv_eliminated = self._lcv_score(course, value, unassigned, domains)
                return (-s_score, lcv_eliminated)

            domain = sorted(domain, key=combined_value_score)

        for slot, room in domain:
            schedule.assign(course, slot, room)

            if self._backtrack(schedule):
                return True

            schedule.unassign(course)
            self.backtrack_count += 1

        return False
