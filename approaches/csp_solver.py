"""
CSPSolver — Constraint Satisfaction Problem approach

Solves the course scheduling problem using backtracking search with
optional heuristics and filtering techniques.

Relies entirely on the shared core:
  - CourseScheduleProblem.domain(course) for initial domains (already filters H3 + H4)
  - ConstraintChecker.is_consistent()    for incremental hard constraint checks
  - Schedule                             for assignment management

AC-3 handles binary constraints between unassigned variables (H1, H2).
Unary constraints (H3, H4) are already filtered by problem.domain() and
ConstraintChecker.is_consistent(), so we never duplicate them here.
"""

from collections import deque # Complexity O(1) for managing Queue, instead of O(n) with simple list
from core.schedule import Schedule
from core.constraints import ConstraintChecker
from core.problem import CourseScheduleProblem, Course, TimeSlot, Room


class CSPSolver:
    """
    Backtracking solver with pluggable heuristics.

    Parameters
    ----------
    use_mrv            : Minimum Remaining Values — pick the most constrained variable first
    use_degree         : Static Degree Heuristic — fast tie-breaker based ONLY on shared professors O(n) (n = number of unassigned courses)
    use_dynamic_degree : Dynamic Degree Heuristic — computes exact current conflicts (expensive but precise) O(n^2 s^2) (s = max number of unique TimeSlots in a course's domain)
    use_lcv            : Least Constraining Value — order values by how little they eliminate from neighbours
    use_fc             : Forward Checking — detect dead ends early (domain becomes empty)
    use_ac3            : AC-3 arc-consistency — stronger propagation between unassigned vars
    """

    def __init__(
        self, problem: CourseScheduleProblem, use_mrv: bool = False, use_degree: bool = False, 
        use_dynamic_degree: bool = False,  use_lcv: bool = False, use_fc: bool = False, use_ac3: bool = False,):

        self.problem = problem
        self.checker = ConstraintChecker(problem)
        
        # Pluggable heuristics
        self.use_mrv            = use_mrv
        self.use_degree         = use_degree
        self.use_dynamic_degree = use_dynamic_degree 
        self.use_lcv            = use_lcv
        self.use_fc             = use_fc
        self.use_ac3            = use_ac3

        # Metrics for experimental evaluation (T1.3)
        self.backtrack_count: int = 0
        self.nodes_explored: int  = 0

    # =========================================================================
    # AC-3 — Binary arc-consistency between unassigned variables
    # =========================================================================

    def _is_arc_compatible(self, c1: Course, val1: tuple, c2: Course, val2: tuple,) -> bool:
        """
        Return True if assigning val1=(slot1, room1) to c1 and
        val2=(slot2, room2) to c2 simultaneously violates no binary
        hard constraint.
        """
        slot1, room1 = val1
        slot2, room2 = val2

        if slot1.overlaps(slot2):
            if c1.professor_id == c2.professor_id:   # H1
                return False
            if room1.id == room2.id:                 # H2
                return False

        return True

    def _remove_inconsistent_values(self, domains: dict, Xi: Course, Xj: Course,) -> bool:
        """
        Remove from domains[Xi.id] every value that has no compatible
        counterpart in domains[Xj.id].
        """
        removed = False
        for x in list(domains[Xi.id]):
            if not any(self._is_arc_compatible(Xi, x, Xj, y) for y in domains[Xj.id]):
                domains[Xi.id].remove(x)
                removed = True
        return removed

    def _ac3(self, unassigned: list, domains: dict) -> bool:
        """
        AC-3 algorithm.
        Uses a deque for O(1) popleft.
        Returns False if any domain becomes empty (dead end detected).
        """
        queue = deque((unassigned[i], unassigned[j])
            for i in range(len(unassigned))
            for j in range(len(unassigned))
            if i != j)

        while queue:
            Xi, Xj = queue.popleft()   # O(1)

            if self._remove_inconsistent_values(domains, Xi, Xj):
                if len(domains[Xi.id]) == 0:
                    return False   # dead end — backtrack immediately

                for Xk in unassigned:
                    if Xk.id != Xi.id:
                        queue.append((Xk, Xi))

        return True

    # =========================================================================
    # Variable selection heuristics
    # =========================================================================

    def _mrv_score(self, course: Course, domains: dict) -> int:
        """MRV: number of remaining valid values (lower = more constrained)."""
        return len(domains[course.id])

    def _static_degree_score(self, course: Course, unassigned: list) -> int:
        """
        [MODIFICATION] Static Degree heuristic: fast calculation based ONLY on 
        professor bottlenecks (the absolute strongest constraint, H1).
        Returns a negative count so that min() picks the highest degree.
        """
        degree = sum(1 for other in unassigned 
                     if other.id != course.id and other.professor_id == course.professor_id)
        return -degree

    def _dynamic_degree_score(self, course: Course, unassigned: list, domains: dict) -> int:
        """
        [AJOUT] Dynamic Degree heuristic: computes the exact number of real binary 
        constraints with other unassigned variables based on CURRENT domains.
        
        Two courses are connected if:
          - They share the same professor (H1 guaranteed conflict)
          - OR they compete for at least one room on at least one common slot (H2)
        """
        degree = 0

        # Precalculate slots and rooms for the current course
        slots_c  = {slot     for slot, room in domains[course.id]}
        rooms_c  = {room.id  for slot, room in domains[course.id]}

        for other in unassigned:
            if other.id == course.id:
                continue

            # H1: same professor -> guaranteed conflict
            if other.professor_id == course.professor_id:
                degree += 1
                continue

            # H2: room competition -> potential conflict if domains share a slot AND a room
            slots_o = {slot    for slot, room in domains[other.id]}
            rooms_o = {room.id for slot, room in domains[other.id]}

            overlapping_slots = any(s1.overlaps(s2) for s1 in slots_c for s2 in slots_o)
            shared_rooms      = bool(rooms_c & rooms_o)

            if overlapping_slots and shared_rooms:
                degree += 1

        return -degree  # negative: min() will pick the most constrained course

    def _select_variable(self, unassigned: list, domains: dict) -> Course:
        """
        [MODIFICATION] Choose the next variable to assign.
        Priority: MRV -> Dynamic Degree OR Static Degree (tie-breaker) -> natural order.
        """
        if self.use_mrv:
            if self.use_dynamic_degree:
                return min(
                    unassigned,
                    key=lambda c: (
                        self._mrv_score(c, domains),
                        self._dynamic_degree_score(c, unassigned, domains), 
                    ),
                )
            elif self.use_degree:
                return min(
                    unassigned,
                    key=lambda c: (
                        self._mrv_score(c, domains),
                        self._static_degree_score(c, unassigned), 
                    ),
                )
            else:
                return min(unassigned, key=lambda c: self._mrv_score(c, domains))
        
        # S'il n'y a pas de MRV, on teste les degrés seuls
        if self.use_dynamic_degree:
            return min(unassigned, key=lambda c: self._dynamic_degree_score(c, unassigned, domains))
        if self.use_degree:
            return min(unassigned, key=lambda c: self._static_degree_score(c, unassigned))

        return unassigned[0]

    # =========================================================================
    # Value ordering heuristic (LCV)
    # =========================================================================

    def _lcv_score(self, course: Course, value: tuple, unassigned: list, domains: dict,) -> int:
        """
        LCV (Least Constraining Value): count how many values this assignment
        would eliminate from other unassigned variables' domains.
        Lower is better — we prefer the value that leaves the most options open.
        """
        eliminated = 0
        for other in unassigned:
            if other.id == course.id:
                continue
            for other_val in domains[other.id]:
                if not self._is_arc_compatible(course, value, other, other_val):
                    eliminated += 1
        return eliminated

    # =========================================================================
    # Backtracking engine
    # =========================================================================

    def solve(self) -> "Schedule | None":
        """Public entry point. Returns a complete Schedule or None."""
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

        # -----------------------------------------------------------------
        # Step 1 — Build dynamic domains & Forward Checking
        # -----------------------------------------------------------------
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

        # -----------------------------------------------------------------
        # Step 2 — AC-3 propagation
        # -----------------------------------------------------------------
        if self.use_ac3:
            if not self._ac3(unassigned, domains):
                return False

        # -----------------------------------------------------------------
        # Step 3 — Variable selection
        # -----------------------------------------------------------------
        course = self._select_variable(unassigned, domains)
        domain = domains[course.id]

        # -----------------------------------------------------------------
        # Step 4 — Value ordering (VCSP: Soft Score then LCV in case of a tie)
        # -----------------------------------------------------------------
        if self.use_lcv:
            def combined_value_score(value):
                slot, room = value
                
                # 1. Soft Score calculus as priority to satisfy the Constraint Optimisation Problem
                schedule.assign(course, slot, room)
                s_score = self.checker.soft_score(schedule)
                schedule.unassign(course)
                
                # 2. LCV if there is a tie between values based on Soft Score evaluation
                lcv_eliminated = self._lcv_score(course, value, unassigned, domains)
                
                # Minus Score to have the highest score first when sorted and in case of a tie having the option pruning the least valid values
                # from the remaining variables to assign (positive lcv_eliminated)
                return (-s_score, lcv_eliminated)

            domain = sorted(domain, key=combined_value_score)

        # -----------------------------------------------------------------
        # Step 5 — Try each value; backtrack on failure
        # -----------------------------------------------------------------
        for slot, room in domain:
            schedule.assign(course, slot, room)

            if self._backtrack(schedule):
                return True

            schedule.unassign(course)
            self.backtrack_count += 1

        return False