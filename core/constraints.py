"""
ConstraintChecker — Hard and soft constraint evaluation

Central constraint engine shared by all three approaches.

Hard constraints (H1–H4): must all be zero for a valid schedule.
Soft constraints (S1–S3): scored 0–1 per course, averaged over the schedule.
"""

from typing import List, Tuple
from core.problem import CourseScheduleProblem, Course, TimeSlot, Room
from core.schedule import Schedule


class ConstraintChecker:
    """
    Evaluates constraint violations for a (possibly partial) Schedule.

    checker = ConstraintChecker(problem)
    violations = checker.hard_violations(schedule)   # → int (0 = valid)
    score      = checker.soft_score(schedule)        # → float in [0, 1]
    ok         = checker.is_consistent(schedule, course, slot, room)
    """

    def __init__(self, problem: CourseScheduleProblem):
        self.problem = problem

    def is_consistent(
        self,
        schedule: Schedule,
        course: Course,
        slot: TimeSlot,
        room: Room,
    ) -> bool:
        """
        Return True if assigning (slot, room) to course violates no hard constraint,
        given the current partial schedule.
        """
        prof = self.problem.professor_by_id[course.professor_id]

        if slot not in prof.available_slots:
            return False

        if room.capacity < course.required_capacity:
            return False

        for other_course in self.problem.courses:
            if not schedule.is_assigned(other_course):
                continue
            other_slot, other_room = schedule.get(other_course)

            if other_slot.overlaps(slot):
                if other_course.professor_id == course.professor_id:
                    return False
                if other_room.id == room.id:
                    return False

        return True

    def hard_violations(self, schedule: Schedule) -> int:
        """Count total hard constraint violations in a complete schedule (0 = valid)."""
        violations = 0
        courses    = self.problem.courses

        for i, c1 in enumerate(courses):
            if not schedule.is_assigned(c1):
                violations += 1
                continue

            slot1, room1 = schedule.get(c1)
            prof1        = self.problem.professor_by_id[c1.professor_id]

            if room1.capacity < c1.required_capacity:
                violations += 1
            if slot1 not in prof1.available_slots:
                violations += 1

            for c2 in courses[i + 1:]:
                if not schedule.is_assigned(c2):
                    continue
                slot2, room2 = schedule.get(c2)

                if slot1.overlaps(slot2):
                    if c1.professor_id == c2.professor_id:
                        violations += 1
                    if room1.id == room2.id:
                        violations += 1

        return violations

    def soft_score(self, schedule: Schedule) -> float:
        """
        Compute the soft constraint score in [0, 1] (higher is better).

        S1 — professor prefers this slot
        S2 — no gaps in the daily schedule
        S3 — daily course load ≤ max_daily_courses

        Returns the equal-weighted average of the three criteria.
        Can be evaluated on partial schedules (used by CSP heuristics).
        """
        return (self._score_s1(schedule) + self._score_s2(schedule) + self._score_s3(schedule)) / 3.0

    def _score_s1(self, schedule: Schedule) -> float:
        """S1: fraction of courses placed in a preferred slot."""
        total = len(self.problem.courses)
        if total == 0:
            return 1.0
        satisfied = 0
        for course in self.problem.courses:
            if not schedule.is_assigned(course):
                continue
            slot, _ = schedule.get(course)
            prof    = self.problem.professor_by_id[course.professor_id]
            if slot in prof.preferred_slots:
                satisfied += 1
        return satisfied / total

    def _score_s2(self, schedule: Schedule) -> float:
        """S2: fraction of active days with no gap between consecutive courses."""
        from collections import defaultdict
        courses_per_day = defaultdict(list)
        for course in self.problem.courses:
            if not schedule.is_assigned(course):
                continue
            slot, _ = schedule.get(course)
            courses_per_day[slot.day].append(slot.hour)

        days_ok     = 0
        active_days = 0
        for day, hours in courses_per_day.items():
            active_days += 1
            if len(hours) <= 1:
                days_ok += 1
                continue
            hours_sorted = sorted(hours)
            has_gap = any(
                hours_sorted[i + 1] - hours_sorted[i] > 2
                for i in range(len(hours_sorted) - 1)
            )
            if not has_gap:
                days_ok += 1

        return days_ok / active_days if active_days > 0 else 1.0

    def _score_s3(self, schedule: Schedule) -> float:
        """S3: fraction of active days where the load is within the daily limit."""
        from collections import defaultdict
        courses_per_day = defaultdict(int)
        for course in self.problem.courses:
            if not schedule.is_assigned(course):
                continue
            slot, _ = schedule.get(course)
            courses_per_day[slot.day] += 1

        limit      = self.problem.max_daily_courses
        days_ok    = sum(1 for v in courses_per_day.values() if v <= limit)
        total_days = len(courses_per_day)
        return days_ok / total_days if total_days > 0 else 1.0

    def objective(self, schedule: Schedule) -> float:
        """
        Combined scalar objective used as the Q-Learning reward signal.
        Returns a value in (−∞, 1]: −10 per hard violation + soft score in [0, 1].
        """
        hard = self.hard_violations(schedule)
        soft = self.soft_score(schedule) if hard == 0 else 0.0
        return -10.0 * hard + soft
