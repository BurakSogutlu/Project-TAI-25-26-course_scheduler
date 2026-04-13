"""
Instance Generator

Generates small, medium, and large course scheduling problem instances.
Both random instances and hand-crafted realistic instances are provided.

Instances are saved to data/ as JSON files for reproducibility.
"""

import json
import random
from pathlib import Path
from core.problem import (
    CourseScheduleProblem, Course, Professor, Room, TimeSlot
)


# Standard timeslot grid — Mon–Fri, 2-hour blocks
# Morning  : 08h–10h, 10h–12h
# Afternoon: 14h–16h, 16h–18h

HOURS = [8, 10, 14, 16]           # start hour of each 2-hour block
DAYS  = [0, 1, 2, 3, 4]           # 0=Mon … 4=Fri

ALL_SLOTS = [TimeSlot(day=d, hour=h) for d in DAYS for h in HOURS]
# Total: 5 days × 4 slots = 20 slots


# Pre-defined realistic instances (hand-crafted)

def make_small_instance() -> CourseScheduleProblem:
    """
    Small instance: 5 courses, 3 professors, 3 rooms.
    """
    rooms = [
        Room("R1", "Salle 101", capacity=30),
        Room("R2", "Salle 102", capacity=50),
        Room("R3", "Amphi A",   capacity=100),
    ]

    # Each professor is available Mon/Wed/Fri
    mwf_days = [0, 2, 4]
    mwf_slots = [TimeSlot(day=d, hour=h) for d in mwf_days for h in HOURS]

    professors = [
        Professor("P_A", "Prof. Alpha",  available_slots=mwf_slots,
                  preferred_slots=[TimeSlot(0, 10), TimeSlot(2, 10)]),
        Professor("P_B", "Prof. Beta",   available_slots=mwf_slots,
                  preferred_slots=[TimeSlot(0, 14), TimeSlot(2, 14)]),
        Professor("P_C", "Prof. Gamma",  available_slots=mwf_slots,
                  preferred_slots=[TimeSlot(4, 8),  TimeSlot(4, 10)]),
    ]

    courses = [
        Course("CS101", "Intro to Programming",   professor_id="P_A", required_capacity=25),
        Course("CS102", "Algorithms",              professor_id="P_A", required_capacity=25),
        Course("CS201", "Artificial Intelligence", professor_id="P_B", required_capacity=45),
        Course("CS202", "Machine Learning",        professor_id="P_C", required_capacity=20),
        Course("CS301", "Data Structures",         professor_id="P_B", required_capacity=30),
    ]

    return CourseScheduleProblem(
        courses=courses,
        professors=professors,
        rooms=rooms,
        timeslots=mwf_slots,
        max_daily_courses=3,
    )


def make_medium_instance(seed: int = 42) -> CourseScheduleProblem:
    """
    Medium instance: 15 courses, 6 professors, 5 rooms.
    """
    rng = random.Random(seed)

    rooms = [
        Room("R1", "Salle 101",  capacity=30),
        Room("R2", "Salle 102",  capacity=30),
        Room("R3", "Salle 201",  capacity=50),
        Room("R4", "Amphi A",    capacity=100),
        Room("R5", "Labo Info",  capacity=25),
    ]

    all_slots = ALL_SLOTS

    professors = [
        Professor(f"P{i}", f"Prof_{i}", available_slots=all_slots,
                  preferred_slots=rng.sample(all_slots, k=4))
        for i in range(6)
    ]

    course_templates = [
        ("Maths",            25), ("Physics",          40), ("Chemistry",       30),
        ("Computer Science", 50), ("Programming",      25), ("Statistics",      35),
        ("Linear Algebra",   30), ("Data Science",     45), ("Networks",        20),
        ("OS",               30), ("Databases",        35), ("Security",        25),
        ("AI",               50), ("Machine Learning", 40), ("Deep Learning",   35),
    ]

    courses = [
        Course(
            id=f"C{i:02d}",
            name=name,
            professor_id=f"P{i % 6}",
            required_capacity=cap,
        )
        for i, (name, cap) in enumerate(course_templates)
    ]

    return CourseScheduleProblem(
        courses=courses,
        professors=professors,
        rooms=rooms,
        timeslots=all_slots,
        max_daily_courses=4,
    )


def make_large_instance(seed: int = 42) -> CourseScheduleProblem:
    """
    Large instance: 30 courses, 10 professors, 8 rooms.
    Tests scalability of each approach.
    """
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room {i}", capacity=rng.choice([25, 30, 40, 50, 80, 100]))
        for i in range(8)
    ]

    professors = [
        Professor(
            id=f"P{i}",
            name=f"Professor_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=rng.randint(10, len(ALL_SLOTS))),
            preferred_slots=[],
        )
        for i in range(10)
    ]
    # Set preferred slots as a random subset of available
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(
                prof.available_slots, k=min(4, len(prof.available_slots))
            )

    courses = [
        Course(
            id=f"C{i:02d}",
            name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, 9)}",
            required_capacity=rng.choice([20, 25, 30, 40, 50]),
        )
        for i in range(30)
    ]

    return CourseScheduleProblem(
        courses=courses,
        professors=professors,
        rooms=rooms,
        timeslots=ALL_SLOTS,
        max_daily_courses=4,
    )


# Random instance generator (parametric) — for scalability experiments

def make_random_instance(
    n_courses: int,
    n_professors: int,
    n_rooms: int,
    seed: int = 0,
) -> CourseScheduleProblem:
    """
    Generate a random instance with the given number of courses, professors
    and rooms. Used for scalability experiments.
    """
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room_{i}", capacity=rng.choice([25, 30, 40, 50, 80]))
        for i in range(n_rooms)
    ]

    # Clamp k so it never exceeds len(ALL_SLOTS)
    avail_k = max(len(ALL_SLOTS) // 2, min(n_courses, len(ALL_SLOTS)))
    professors = [
        Professor(
            id=f"P{i}",
            name=f"Prof_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=avail_k),
            preferred_slots=[],
        )
        for i in range(n_professors)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(
                prof.available_slots, k=min(4, len(prof.available_slots))
            )

    courses = [
        Course(
            id=f"C{i:03d}",
            name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, n_professors - 1)}",
            required_capacity=rng.choice([20, 25, 30, 40]),
        )
        for i in range(n_courses)
    ]

    return CourseScheduleProblem(
        courses=courses,
        professors=professors,
        rooms=rooms,
        timeslots=ALL_SLOTS,
        max_daily_courses=max(3, n_courses // 5),
    )


# Main — generate and save all standard instances

if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    instances = {
        "small_instance":  make_small_instance(),
        "medium_instance": make_medium_instance(),
        "large_instance":  make_large_instance(),
    }

    for name, problem in instances.items():
        path = data_dir / f"{name}.json"
        problem.to_json(str(path))
        print(f"[OK] Saved {name}: {problem}")

    print("\nAll instances generated successfully.")
    print(f"  Timeslots per day : {len(HOURS)} blocks × 2h = {len(HOURS)*2}h covered")
    print(f"  Total slots       : {len(ALL_SLOTS)} ({len(DAYS)} days × {len(HOURS)} slots)")
    print(f"Files saved to: {data_dir.resolve()}")
