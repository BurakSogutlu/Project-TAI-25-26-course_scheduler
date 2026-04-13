"""
Schedule — Schedule representation

A Schedule maps each course to a (timeslot, room) assignment.
This is the central object manipulated by all three approaches.
"""

from typing import Dict, Optional, Tuple, List
from core.problem import Course, TimeSlot, Room, CourseScheduleProblem


# Assignment: a (timeslot, room) pair
Assignment = Tuple[TimeSlot, Room]


class Schedule:
    """
    Represents a (possibly partial or complete) course schedule.

    Internal state

    _assignments : dict{ course_id -> (TimeSlot, Room) }
        Stores the assignment for each scheduled course.
        Unscheduled courses are simply absent from this dict.
    """

    def __init__(self, problem: CourseScheduleProblem):
        self.problem = problem
        self._assignments: Dict[str, Assignment] = {}

    # Assignment API

    def assign(self, course: Course, slot: TimeSlot, room: Room):
        """Assign a course to a (timeslot, room) pair."""
        self._assignments[course.id] = (slot, room)

    def unassign(self, course: Course):
        """Remove the assignment of a course (used during backtracking)."""
        self._assignments.pop(course.id, None)

    def get(self, course: Course) -> Optional[Assignment]:
        """Return the assignment of a course, or None if unassigned."""
        return self._assignments.get(course.id)

    def is_assigned(self, course: Course) -> bool:
        return course.id in self._assignments

    def is_complete(self) -> bool:
        """True iff every course in the problem has been assigned."""
        return len(self._assignments) == len(self.problem.courses)

    def unassigned_courses(self) -> List[Course]:
        """Return courses that have not yet been assigned."""
        return [c for c in self.problem.courses if c.id not in self._assignments]

    # Neighbour generation — used by Local Search

    def swap_neighbour(self, course_a: Course, course_b: Course) -> "Schedule":
        """
        Return a new Schedule where course_a and course_b swap their assignments.
        Both must already be assigned.
        """
        new_sched = self.copy()
        assign_a = self._assignments[course_a.id]
        assign_b = self._assignments[course_b.id]
        new_sched._assignments[course_a.id] = assign_b
        new_sched._assignments[course_b.id] = assign_a
        return new_sched

    def move_neighbour(self, course: Course, new_slot: TimeSlot, new_room: Room) -> "Schedule":
        """
        Return a new Schedule where one course is moved to a different (slot, room).
        """
        new_sched = self.copy()
        new_sched._assignments[course.id] = (new_slot, new_room)
        return new_sched

    # Utility

    def copy(self) -> "Schedule":
        new_sched = Schedule(self.problem)
        new_sched._assignments = dict(self._assignments)
        return new_sched

    def to_dict(self) -> dict:
        """Serialise the schedule to a plain dictionary."""
        result = {}
        for cid, (slot, room) in self._assignments.items():
            result[cid] = {
                "slot": {"day": slot.day, "hour": slot.hour},
                "room": room.id,
            }
        return result

    def pretty_print(self):
        """Print a human-readable timetable."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        print(f"\n{'='*65}")
        print(f"{'SCHEDULE':^65}")
        print(f"{'='*65}")
        for cid, (slot, room) in sorted(
            self._assignments.items(),
            key=lambda x: (x[1][0].day, x[1][0].hour)
        ):
            course = self.problem.course_by_id[cid]
            end_hour = slot.hour + 2
            print(
                f"  {days[slot.day]:<10} {slot.hour:02d}h–{end_hour:02d}h  |  "
                f"{course.name:<30}  |  {room.name}  (cap. {room.capacity})"
            )
        print(f"{'='*65}\n")

    def __repr__(self):
        assigned = len(self._assignments)
        total = len(self.problem.courses)
        return f"Schedule({assigned}/{total} courses assigned)"
