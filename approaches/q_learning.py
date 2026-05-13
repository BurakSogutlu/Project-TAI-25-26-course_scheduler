"""
Q-Learning Solver

An agent learns by trial-and-error to build a valid course schedule.
Uses a feature-based Q-table to keep the state space manageable.

Reward signal: checker.objective() = -10 × hard_violations + soft_score
"""

import random
from collections import defaultdict
from core.problem import CourseScheduleProblem
from core.schedule import Schedule
from core.constraints import ConstraintChecker


class QLearningScheduler:
    """
    Q-Learning agent for course scheduling.

    Each episode builds one complete schedule from scratch. The agent picks
    a (slot, room) for each course using ε-greedy, then updates the Q-table
    via the Bellman equation.

    n_episodes    : number of full schedule attempts
    alpha         : learning rate
    gamma         : discount factor
    epsilon       : initial exploration rate (1.0 = fully random)
    epsilon_min   : minimum exploration rate after decay
    epsilon_decay : linear decay per episode
    """

    def __init__(
        self,
        problem: CourseScheduleProblem,
        n_episodes: int = 1000,
        alpha: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.005,
    ):
        self.problem = problem
        self.checker = ConstraintChecker(problem)

        self.n_episodes    = n_episodes
        self.alpha         = alpha
        self.gamma         = gamma
        self.epsilon       = epsilon
        self.epsilon_min   = epsilon_min
        self.epsilon_decay = epsilon_decay

        # defaultdict returns 0.0 for unseen (state, action) pairs
        self.q_table = defaultdict(float)

        self.best_schedule: Schedule = None
        self.best_score: float       = float('-inf')

    def _get_features(self, course, slot, room, schedule) -> tuple:
        """
        Encode a (course, slot, room, partial schedule) as a 5-dimensional feature tuple
        used as the Q-table key.

        f1: slot in professor's preferred slots
        f2: professor already teaching at this slot
        f3: room already occupied at this slot
        f4: courses already scheduled on this day
        f5: room capacity sufficient
        """
        prof = self.problem.professor_by_id[course.professor_id]

        f1 = 1 if slot in prof.preferred_slots else 0

        f2 = 0
        for other in self.problem.courses:
            if schedule.is_assigned(other):
                other_slot, _ = schedule.get(other)
                if other_slot == slot and other.professor_id == course.professor_id:
                    f2 = 1
                    break

        f3 = 0
        for other in self.problem.courses:
            if schedule.is_assigned(other):
                other_slot, other_room = schedule.get(other)
                if other_slot == slot and other_room.id == room.id:
                    f3 = 1
                    break

        f4 = sum(
            1 for c in self.problem.courses
            if schedule.is_assigned(c) and schedule.get(c)[0].day == slot.day
        )

        f5 = 1 if room.capacity >= course.required_capacity else 0

        return (f1, f2, f3, f4, f5)

    def _choose_action(self, course, schedule):
        """
        ε-greedy action selection for the given course.
        Returns a (slot, room) pair, or None if no valid action exists.
        """
        actions = self.problem.domain(course)
        if not actions:
            return None

        if random.random() < self.epsilon:
            return random.choice(actions)

        best_action, best_q = None, float('-inf')
        for slot, room in actions:
            q_val = self.q_table[self._get_features(course, slot, room, schedule)]
            if q_val > best_q:
                best_q, best_action = q_val, (slot, room)

        return best_action

    def _update_q(self, features, reward, next_features_list):
        """Bellman update: Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') − Q(s,a)]"""
        max_next_q = max(self.q_table[f] for f in next_features_list) if next_features_list else 0.0
        current_q  = self.q_table[features]
        self.q_table[features] = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)

    def train(self):
        """
        Run n_episodes episodes. Each episode builds a full schedule, updates the Q-table,
        and tracks the best complete schedule found.
        """
        for _ in range(self.n_episodes):
            schedule = Schedule(self.problem)
            courses  = list(self.problem.courses)
            random.shuffle(courses)

            for i, course in enumerate(courses):
                action = self._choose_action(course, schedule)
                if action is None:
                    continue

                slot, room       = action
                current_features = self._get_features(course, slot, room, schedule)
                schedule.assign(course, slot, room)

                reward = self.checker.objective(schedule)

                # Next-state features come from the immediate next course only (sequential MDP)
                next_features_list = []
                if i + 1 < len(courses):
                    next_course = courses[i + 1]
                    for next_slot, next_room in self.problem.domain(next_course):
                        next_features_list.append(
                            self._get_features(next_course, next_slot, next_room, schedule)
                        )

                self._update_q(current_features, reward, next_features_list)

            if schedule.is_complete():
                score = self.checker.objective(schedule)
                if score > self.best_score:
                    self.best_score    = score
                    self.best_schedule = schedule.copy()

            self.epsilon = max(self.epsilon_min, self.epsilon - self.epsilon_decay)

        if self.best_schedule is None:
            self.best_schedule = schedule

    def solve(self) -> Schedule:
        """Train the agent, then build one final greedy schedule. Returns the best overall."""
        self.train()

        saved_epsilon = self.epsilon
        self.epsilon  = 0.0

        schedule = Schedule(self.problem)
        courses  = list(self.problem.courses)
        random.shuffle(courses)

        for course in courses:
            action = self._choose_action(course, schedule)
            if action is not None:
                slot, room = action
                schedule.assign(course, slot, room)

        self.epsilon = saved_epsilon

        final_score = self.checker.objective(schedule)
        if final_score > self.best_score:
            return schedule
        return self.best_schedule if self.best_schedule is not None else schedule


def solve(problem: CourseScheduleProblem, n_episodes: int = 1000) -> Schedule:
    """Entry point called by evaluation/metrics.py."""
    scheduler = QLearningScheduler(problem, n_episodes=n_episodes)
    return scheduler.solve()


if __name__ == "__main__":
    from core.problem import CourseScheduleProblem
    from core.constraints import ConstraintChecker

    print("Loading small instance...")
    problem = CourseScheduleProblem.from_json("data/instance_05.json")

    print("Training Q-Learning agent (1000 episodes)...")
    scheduler = QLearningScheduler(problem, n_episodes=1000)
    solution  = scheduler.solve()

    checker    = ConstraintChecker(problem)
    violations = checker.hard_violations(solution)
    score      = checker.soft_score(solution) if violations == 0 else 0.0

    print(f"\nResults:")
    print(f"  Hard violations : {violations}  (0 = valid)")
    print(f"  Soft score      : {score:.3f}  (0–1, higher is better)")
    print(f"  Q-table size    : {len(scheduler.q_table)} entries")

    solution.pretty_print()
