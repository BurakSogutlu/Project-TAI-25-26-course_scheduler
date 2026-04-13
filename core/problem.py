"""
CourseScheduleProblem — Shared data model 

Defines the problem instance: courses, professors, rooms, timeslots,
and all constraint data. This is the single shared data structure
used by all three solving approaches (CSP, Local Search, Q-Learning).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import json


# Core data types

@dataclass(frozen=True)
class TimeSlot:
    """A (day, start_hour) pair representing a 2-hour scheduling block."""
    day: int    # 0 = Monday, 1 = Tuesday, ... , 4 = Friday
    hour: int   # start hour — must be one of {8, 10, 14, 16}

    DURATION = 2  # all blocks are 2 hours long

    def __repr__(self):
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        return f"{days[self.day]} {self.hour:02d}h–{self.hour + self.DURATION:02d}h"

    def overlaps(self, other: "TimeSlot") -> bool:
        """Two 2-hour blocks overlap iff they are on the same day and their
        intervals [hour, hour+2) intersect, i.e. |h1 - h2| < DURATION."""
        return self.day == other.day and abs(self.hour - other.hour) < self.DURATION


@dataclass
class Course:
    """A course that must be scheduled."""
    id: str                         # e.g. "CS101"
    name: str                       # e.g. "Intro to Programming"
    professor_id: str               # ID of the assigned professor
    required_capacity: int          # minimum room capacity needed
    duration: int = 2               # all courses are 2-hour blocks


@dataclass
class Professor:
    """A professor with availability constraints."""
    id: str
    name: str
    available_slots: List[TimeSlot] = field(default_factory=list)
    # Soft: preferred slots (subset of available_slots)
    preferred_slots: List[TimeSlot] = field(default_factory=list)


@dataclass
class Room:
    """A physical room with a seating capacity."""
    id: str
    name: str
    capacity: int


# Problem instance

class CourseScheduleProblem:
    """
    Encapsulates a complete course scheduling problem instance.

    Formal definition:

    - Variables  : X = { x_c | c ∈ Courses }
                   x_c = (timeslot, room) assigned to course c
    - Domains    : D(x_c) = { (t, r) | t ∈ TimeSlots, r ∈ Rooms,
                               r.capacity ≥ c.required_capacity,
                               t ∈ professor[c].available_slots }
    - Hard constraints (must all be satisfied):
        H1 — No professor teaches two courses at the same time
        H2 — No room hosts two courses at the same time
        H3 — Room capacity ≥ course required capacity
        H4 — Timeslot is in professor's availability
    - Soft constraints (maximised):
        S1 — Timeslot is in professor's preferred slots
        S2 — No "gap" (free hour between two courses) in a student's day
        S3 — Daily load is balanced (≤ max_daily_courses per day)
    """

    def __init__(
        self,
        courses: List[Course],
        professors: List[Professor],
        rooms: List[Room],
        timeslots: List[TimeSlot],
        max_daily_courses: int = 3,
    ):
        self.courses = courses
        self.professors = professors
        self.rooms = rooms
        self.timeslots = timeslots
        self.max_daily_courses = max_daily_courses

        # Quick-access dictionaries
        self.professor_by_id: Dict[str, Professor] = {p.id: p for p in professors}
        self.room_by_id: Dict[str, Room] = {r.id: r for r in rooms}
        self.course_by_id: Dict[str, Course] = {c.id: c for c in courses}

    # Domain computation — used by the CSP approach

    def domain(self, course: Course) -> List[Tuple[TimeSlot, Room]]:
        """
        Returns all (timeslot, room) pairs that satisfy the unary constraints
        for a given course (H3 + H4).
        """
        prof = self.professor_by_id[course.professor_id]
        valid = []
        for slot in prof.available_slots:
            for room in self.rooms:
                if room.capacity >= course.required_capacity:
                    valid.append((slot, room))
        return valid

    # Serialisation — save / load instances as JSON

    def to_dict(self) -> dict:
        return {
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "professor_id": c.professor_id,
                    "required_capacity": c.required_capacity,
                    "duration": c.duration,
                }
                for c in self.courses
            ],
            "professors": [
                {
                    "id": p.id,
                    "name": p.name,
                    "available_slots": [
                        {"day": s.day, "hour": s.hour} for s in p.available_slots
                    ],
                    "preferred_slots": [
                        {"day": s.day, "hour": s.hour} for s in p.preferred_slots
                    ],
                }
                for p in self.professors
            ],
            "rooms": [
                {"id": r.id, "name": r.name, "capacity": r.capacity}
                for r in self.rooms
            ],
            "timeslots": [
                {"day": t.day, "hour": t.hour} for t in self.timeslots
            ],
            "max_daily_courses": self.max_daily_courses,
        }

    def to_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "CourseScheduleProblem":
        timeslots = [TimeSlot(day=s["day"], hour=s["hour"]) for s in data["timeslots"]]

        professors = []
        for p in data["professors"]:
            avail = [TimeSlot(day=s["day"], hour=s["hour"]) for s in p["available_slots"]]
            pref  = [TimeSlot(day=s["day"], hour=s["hour"]) for s in p["preferred_slots"]]
            professors.append(Professor(id=p["id"], name=p["name"],
                                        available_slots=avail, preferred_slots=pref))

        rooms = [Room(id=r["id"], name=r["name"], capacity=r["capacity"])
                 for r in data["rooms"]]

        courses = [
            Course(
                id=c["id"], name=c["name"],
                professor_id=c["professor_id"],
                required_capacity=c["required_capacity"],
                duration=c.get("duration", 1),
            )
            for c in data["courses"]
        ]

        return cls(
            courses=courses,
            professors=professors,
            rooms=rooms,
            timeslots=timeslots,
            max_daily_courses=data.get("max_daily_courses", 3),
        )

    @classmethod
    def from_json(cls, path: str) -> "CourseScheduleProblem":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    # Helpers

    def __repr__(self):
        return (
            f"CourseScheduleProblem("
            f"{len(self.courses)} courses, "
            f"{len(self.professors)} professors, "
            f"{len(self.rooms)} rooms, "
            f"{len(self.timeslots)} slots)"
        )
