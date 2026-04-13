"""
ConstraintChecker — Hard and soft constraint evaluation

Central constraint engine shared by all three approaches.

Hard constraints (H1–H4): must all be zero violations for a valid schedule.
Soft constraints (S1–S3): scored 0–1 per course, averaged over the schedule.
"""

from typing import List, Tuple
from core.problem import CourseScheduleProblem, Course, TimeSlot, Room
from core.schedule import Schedule


class ConstraintChecker:
    """
    Evaluates constraint violations for a (possibly partial) Schedule.

    checker = ConstraintChecker(problem)

    # Check hard violations for a complete schedule
    violations = checker.hard_violations(schedule)   # → int (0 = valid)

    # Compute soft score for a complete schedule
    score = checker.soft_score(schedule)             # → float in [0, 1]

    # Incremental check: is adding (course, slot, room) conflict-free?
    ok = checker.is_consistent(schedule, course, slot, room)
    """

    def __init__(self, problem: CourseScheduleProblem):
        self.problem = problem

    # Incremental consistency check — used by CSP backtracking
    
    def is_consistent(
        self,
        schedule: Schedule,
        course: Course,
        slot: TimeSlot,
        room: Room,
    ) -> bool:
        """
        Return True if assigning (slot, room) to course violates no hard
        constraint, given the current partial schedule.

        Checks:
          H1 — professor conflict (same slot, same professor already used)
          H2 — room conflict (same slot, same room already used)
          H3 — room capacity (room.capacity ≥ course.required_capacity)
          H4 — professor availability (slot ∈ professor.available_slots)
        """
        prof = self.problem.professor_by_id[course.professor_id]

        # H4 — Availability
        if slot not in prof.available_slots:
            return False

        # H3 — Capacity
        if room.capacity < course.required_capacity:
            return False

        for other_course in self.problem.courses:
            if not schedule.is_assigned(other_course):
                continue
            other_slot, other_room = schedule.get(other_course)

            if other_slot.overlaps(slot):
                # H1 — Professor conflict
                if other_course.professor_id == course.professor_id:
                    return False
                # H2 — Room conflict
                if other_room.id == room.id:
                    return False

        return True

    # Full hard violation count — used by Local Search & evaluation

    def hard_violations(self, schedule: Schedule) -> int:
        """
        Count total hard constraint violations in a complete schedule.
        Returns 0 for a completely valid schedule.
        """
        violations = 0
        courses = self.problem.courses

        for i, c1 in enumerate(courses):
            if not schedule.is_assigned(c1):
                violations += 1   # unscheduled course counts as violation
                continue

            slot1, room1 = schedule.get(c1)
            prof1 = self.problem.professor_by_id[c1.professor_id]

            # H3
            if room1.capacity < c1.required_capacity:
                violations += 1
            # H4
            if slot1 not in prof1.available_slots:
                violations += 1

            for c2 in courses[i + 1:]:
                if not schedule.is_assigned(c2):
                    continue
                slot2, room2 = schedule.get(c2)

                if slot1.overlaps(slot2):
                    # H1
                    if c1.professor_id == c2.professor_id:
                        violations += 1
                    # H2
                    if room1.id == room2.id:
                        violations += 1

        return violations

    # Soft score — used by Local Search & evaluation

    def soft_score(self, schedule: Schedule) -> float:
        """
        Compute the soft constraint score in [0, 1].
        Higher is better.

        S1 — Professor prefers this slot             (+1 per course)
        S2 — No gaps in daily schedule               (+1 if no gap)
        S3 — Daily load ≤ max_daily_courses          (+1 per day with ≤ limit)

        Returns the weighted average across all criteria.
        This can be evaluated on partial schedules (useful for CSP heuristics).
        """
        s1_score = self._score_s1(schedule)
        s2_score = self._score_s2(schedule)
        s3_score = self._score_s3(schedule)

        # Equal weighting between the three soft criteria
        return (s1_score + s2_score + s3_score) / 3.0

    def _score_s1(self, schedule: Schedule) -> float:
        """S1: Professor preference satisfaction."""
        total = len(self.problem.courses)
        if total == 0:
            return 1.0
        satisfied = 0
        for course in self.problem.courses:
            if not schedule.is_assigned(course):
                continue
            slot, _ = schedule.get(course)
            prof = self.problem.professor_by_id[course.professor_id]
            if slot in prof.preferred_slots:
                satisfied += 1
        return satisfied / total

    def _score_s2(self, schedule: Schedule) -> float:
        """S2: No gaps in a student's day.
        A gap is a free 2h block between two scheduled courses.
        i.e. consecutive start hours differ by more than 2."""
        from collections import defaultdict
        courses_per_day = defaultdict(list)
        for course in self.problem.courses:
            if not schedule.is_assigned(course):
                continue
            slot, _ = schedule.get(course)
            courses_per_day[slot.day].append(slot.hour)

        days_with_no_gap = 0
        active_days = 0
        for day, hours in courses_per_day.items():
            if len(hours) <= 1:
                days_with_no_gap += 1
                active_days += 1
                continue
            active_days += 1
            hours_sorted = sorted(hours)
            has_gap = any(
                hours_sorted[i + 1] - hours_sorted[i] > 2   # gap = skipped 2h block
                for i in range(len(hours_sorted) - 1)
            )
            if not has_gap:
                days_with_no_gap += 1

        return days_with_no_gap / active_days if active_days > 0 else 1.0

    def _score_s3(self, schedule: Schedule) -> float:
        """S3: Balanced daily load (≤ max_daily_courses per day)."""
        from collections import defaultdict
        courses_per_day = defaultdict(int)
        for course in self.problem.courses:
            if not schedule.is_assigned(course):
                continue
            slot, _ = schedule.get(course)
            courses_per_day[slot.day] += 1

        limit = self.problem.max_daily_courses
        days_within_limit = sum(1 for v in courses_per_day.values() if v <= limit)
        total_days = len(courses_per_day)
        return days_within_limit / total_days if total_days > 0 else 1.0

    # Combined objective — used by RL reward function

    def objective(self, schedule: Schedule) -> float:
        """
        Single scalar objective combining hard and soft constraints.
        Used as reward signal for Q-Learning.

        Returns a value in (-∞, 1]:
          - Heavily penalises hard violations (−10 per violation)
          - Adds soft score bonus in [0, 1]
        """
        hard = self.hard_violations(schedule)
        soft = self.soft_score(schedule) if hard == 0 else 0.0
        return -10.0 * hard + soft
