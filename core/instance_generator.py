"""
Instance Generator

Generates course scheduling problem instances of varying sizes.
Instances are saved to data/ as JSON files for reproducibility.
"""

import json
import random
from pathlib import Path
from core.problem import (
    CourseScheduleProblem, Course, Professor, Room, TimeSlot
)

# Standard timeslot grid: Mon–Fri, four 2-hour blocks per day
HOURS = [8, 10, 14, 16]
DAYS  = [0, 1, 2, 3, 4]

ALL_SLOTS = [TimeSlot(day=d, hour=h) for d in DAYS for h in HOURS]


def make_instance_05() -> CourseScheduleProblem:
    """5 courses, 3 professors, 3 rooms."""
    rooms = [
        Room("R1", "Salle 101", capacity=30),
        Room("R2", "Salle 102", capacity=50),
        Room("R3", "Amphi A",   capacity=100),
    ]

    mwf_slots = [TimeSlot(day=d, hour=h) for d in [0, 2, 4] for h in HOURS]

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
        courses=courses, professors=professors, rooms=rooms,
        timeslots=mwf_slots, max_daily_courses=3,
    )


def make_instance_15(seed: int = 42) -> CourseScheduleProblem:
    """15 courses, 6 professors, 5 rooms."""
    rng = random.Random(seed)

    rooms = [
        Room("R1", "Salle 101",  capacity=30),
        Room("R2", "Salle 102",  capacity=30),
        Room("R3", "Salle 201",  capacity=50),
        Room("R4", "Amphi A",    capacity=100),
        Room("R5", "Labo Info",  capacity=25),
    ]

    professors = [
        Professor(f"P{i}", f"Prof_{i}", available_slots=ALL_SLOTS,
                  preferred_slots=rng.sample(ALL_SLOTS, k=4))
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
        Course(id=f"C{i:02d}", name=name, professor_id=f"P{i % 6}", required_capacity=cap)
        for i, (name, cap) in enumerate(course_templates)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=4,
    )


def make_instance_30(seed: int = 42) -> CourseScheduleProblem:
    """30 courses, 10 professors, 8 rooms."""
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room {i}", capacity=rng.choice([25, 30, 40, 50, 80, 100]))
        for i in range(8)
    ]

    professors = [
        Professor(
            id=f"P{i}", name=f"Professor_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=rng.randint(10, len(ALL_SLOTS))),
            preferred_slots=[],
        )
        for i in range(10)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(prof.available_slots, k=min(4, len(prof.available_slots)))

    courses = [
        Course(
            id=f"C{i:02d}", name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, 9)}",
            required_capacity=rng.choice([20, 25, 30, 40, 50]),
        )
        for i in range(30)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=4,
    )


def make_instance_60(seed: int = 42) -> CourseScheduleProblem:
    """60 courses, 15 professors, 8 rooms."""
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room {i}", capacity=rng.choice([25, 30, 40, 50, 80, 100]))
        for i in range(8)
    ]

    professors = [
        Professor(
            id=f"P{i}", name=f"Professor_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=rng.randint(12, len(ALL_SLOTS))),
            preferred_slots=[],
        )
        for i in range(15)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(prof.available_slots, k=min(4, len(prof.available_slots)))

    courses = [
        Course(
            id=f"C{i:02d}", name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, 14)}",
            required_capacity=rng.choice([20, 25, 30, 40, 50]),
        )
        for i in range(60)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=4,
    )


def make_instance_100(seed: int = 42) -> CourseScheduleProblem:
    """100 courses, 20 professors, 8 rooms."""
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room {i}", capacity=rng.choice([25, 30, 40, 50, 80, 100]))
        for i in range(8)
    ]

    professors = [
        Professor(
            id=f"P{i}", name=f"Professor_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=rng.randint(12, len(ALL_SLOTS))),
            preferred_slots=[],
        )
        for i in range(20)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(prof.available_slots, k=min(4, len(prof.available_slots)))

    courses = [
        Course(
            id=f"C{i:03d}", name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, 19)}",
            required_capacity=rng.choice([20, 25, 30, 40, 50]),
        )
        for i in range(100)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=5,
    )


def make_instance_125(seed: int = 42) -> CourseScheduleProblem:
    """125 courses, 25 professors, 8 rooms."""
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room {i}", capacity=rng.choice([25, 30, 40, 50, 80, 100]))
        for i in range(8)
    ]

    professors = [
        Professor(
            id=f"P{i}", name=f"Professor_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=rng.randint(12, len(ALL_SLOTS))),
            preferred_slots=[],
        )
        for i in range(25)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(prof.available_slots, k=min(4, len(prof.available_slots)))

    courses = [
        Course(
            id=f"C{i:03d}", name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, 24)}",
            required_capacity=rng.choice([20, 25, 30, 40, 50]),
        )
        for i in range(125)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=5,
    )


def make_instance_150(seed: int = 42) -> CourseScheduleProblem:
    """150 courses, 30 professors, 8 rooms."""
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room {i}", capacity=rng.choice([25, 30, 40, 50, 80, 100]))
        for i in range(8)
    ]

    professors = [
        Professor(
            id=f"P{i}", name=f"Professor_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=rng.randint(15, len(ALL_SLOTS))),
            preferred_slots=[],
        )
        for i in range(30)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(prof.available_slots, k=min(4, len(prof.available_slots)))

    courses = [
        Course(
            id=f"C{i:03d}", name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, 29)}",
            required_capacity=rng.choice([20, 25, 30, 40, 50]),
        )
        for i in range(150)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=6,
    )


def make_random_instance(
    n_courses: int,
    n_professors: int,
    n_rooms: int,
    seed: int = 0,
) -> CourseScheduleProblem:
    """Generate a random instance with the given numbers of courses, professors, and rooms."""
    rng = random.Random(seed)

    rooms = [
        Room(f"R{i}", f"Room_{i}", capacity=rng.choice([25, 30, 40, 50, 80]))
        for i in range(n_rooms)
    ]

    avail_k = max(len(ALL_SLOTS) // 2, min(n_courses, len(ALL_SLOTS)))
    professors = [
        Professor(
            id=f"P{i}", name=f"Prof_{i}",
            available_slots=rng.sample(ALL_SLOTS, k=avail_k),
            preferred_slots=[],
        )
        for i in range(n_professors)
    ]
    for prof in professors:
        if prof.available_slots:
            prof.preferred_slots = rng.sample(prof.available_slots, k=min(4, len(prof.available_slots)))

    courses = [
        Course(
            id=f"C{i:03d}", name=f"Course_{i}",
            professor_id=f"P{rng.randint(0, n_professors - 1)}",
            required_capacity=rng.choice([20, 25, 30, 40]),
        )
        for i in range(n_courses)
    ]

    return CourseScheduleProblem(
        courses=courses, professors=professors, rooms=rooms,
        timeslots=ALL_SLOTS, max_daily_courses=max(3, n_courses // 5),
    )


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    instances = {
        "instance_05":  make_instance_05(),
        "instance_15":  make_instance_15(),
        "instance_30":  make_instance_30(),
        "instance_60":  make_instance_60(),
        "instance_100": make_instance_100(),
        "instance_125": make_instance_125(),
        "instance_150": make_instance_150(),
    }

    for name, problem in instances.items():
        path = data_dir / f"{name}.json"
        problem.to_json(str(path))
        print(f"[OK] Saved {name}: {problem}")

    print("\nAll instances generated successfully.")
    print(f"  Slots per day : {len(HOURS)} blocks × 2h")
    print(f"  Total slots   : {len(ALL_SLOTS)} ({len(DAYS)} days × {len(HOURS)} slots)")
    print(f"Files saved to : {data_dir.resolve()}")
