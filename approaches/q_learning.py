"""
Q-Learning Solver — Approach C

An agent learns by trial-and-error to build a valid course schedule.
Uses a feature-based Q-Table to handle the large state space.

Key design decisions:
- Feature-based representation (not exhaustive Q-Table) to handle state space explosion
- ε-greedy exploration with linear decay
- Episode-based training: each episode builds a full schedule from scratch
- Reward signal: checker.objective() = -10 * hard_violations + soft_score
"""

import random
from collections import defaultdict
from core.problem import CourseScheduleProblem
from core.schedule import Schedule
from core.constraints import ConstraintChecker


class QLearningScheduler:
    """
    Q-Learning agent for course scheduling.

    The agent iteratively builds complete schedules (episodes).
    At each step, it picks an action (slot, room) for the current course
    using an ε-greedy policy, then updates the Q-Table via Bellman's equation.

    Parameters
    ----------
    problem      : CourseScheduleProblem
    n_episodes   : number of full schedule attempts during training
    alpha        : learning rate (how fast we update Q-values)
    gamma        : discount factor (how much we value future rewards)
    epsilon      : initial exploration rate (1.0 = 100% random at start)
    epsilon_min  : minimum exploration rate after decay
    epsilon_decay: linear decay applied to epsilon after each episode
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

        # Hyperparameters
        self.n_episodes = n_episodes
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-Table: feature_tuple → expected cumulative reward
        # defaultdict(float) returns 0.0 for unseen state-action pairs
        self.q_table = defaultdict(float)

        # Best solution found during training
        self.best_schedule: Schedule = None
        self.best_score: float = float('-inf')


    # Feature extraction


    def _get_features(self, course, slot, room, schedule) -> tuple:
        """
        Encode a (course, slot, room, schedule) state-action pair as a
        compact feature tuple used as the Q-Table key.

        Features
        --------
        f1 : slot is in professor's preferred slots         (0 or 1)
        f2 : professor already has a course at this slot    (0 or 1)
        f3 : room already occupied at this slot             (0 or 1)
        f4 : number of courses already scheduled this day   (int)
        f5 : room capacity is sufficient                    (0 or 1)
        """
        prof = self.problem.professor_by_id[course.professor_id]

        # f1 — Professor preference
        f1 = 1 if slot in prof.preferred_slots else 0

        # f2 — Professor conflict at this slot
        f2 = 0
        for other in self.problem.courses:
            if schedule.is_assigned(other):
                other_slot, _ = schedule.get(other)
                if other_slot == slot and other.professor_id == course.professor_id:
                    f2 = 1
                    break

        # f3 — Room conflict at this slot
        f3 = 0
        for other in self.problem.courses:
            if schedule.is_assigned(other):
                other_slot, other_room = schedule.get(other)
                if other_slot == slot and other_room.id == room.id:
                    f3 = 1
                    break

        # f4 — Daily load for this day
        f4 = sum(
            1 for c in self.problem.courses
            if schedule.is_assigned(c) and schedule.get(c)[0].day == slot.day
        )

        # f5 — Room capacity sufficient
        f5 = 1 if room.capacity >= course.required_capacity else 0

        return (f1, f2, f3, f4, f5)


    # Action selection — ε-greedy


    def _choose_action(self, course, schedule):
        """
        Choose a (slot, room) action for the given course using ε-greedy.

        - With probability ε  : pick a random action (exploration)
        - With probability 1-ε: pick the action with highest Q-value (exploitation)

        Returns None if no valid action exists for this course.
        """
        actions = self.problem.domain(course)  # all (slot, room) pairs satisfying H3+H4
        if not actions:
            return None

        # Exploration: random action
        if random.random() < self.epsilon:
            return random.choice(actions)

        # Exploitation: pick action with best Q-value
        best_action = None
        best_q = float('-inf')
        for slot, room in actions:
            features = self._get_features(course, slot, room, schedule)
            q_val = self.q_table[features]
            if q_val > best_q:
                best_q = q_val
                best_action = (slot, room)

        return best_action


    # Q-Table update — Bellman equation


    def _update_q(self, features, reward, next_features_list):
        """
        Apply the Bellman update to Q(features):

            Q(s,a) ← Q(s,a) + α × [r + γ × max_a'(Q(s',a')) − Q(s,a)]

        Parameters
        ----------
        features         : feature tuple for current (state, action)
        reward           : reward received after taking the action
        next_features_list: list of feature tuples for all possible next actions
        """
        # Best Q-value reachable from next state
        if next_features_list:
            max_next_q = max(self.q_table[f] for f in next_features_list)
        else:
            max_next_q = 0.0  # terminal state: no next actions

        # Bellman update
        current_q = self.q_table[features]
        self.q_table[features] = current_q + self.alpha * (
            reward + self.gamma * max_next_q - current_q
        )


    # Training loop


    def train(self):
        """
        Run n_episodes training episodes.

        Each episode:
        1. Start from an empty schedule
        2. Place each course one by one using ε-greedy
        3. After each placement, compute reward and update Q-Table
        4. Track the best complete schedule found
        5. Decay epsilon
        """
        for episode in range(self.n_episodes):
            schedule = Schedule(self.problem)

            # Shuffle course order for diversity across episodes
            courses = list(self.problem.courses)
            random.shuffle(courses)

            for i, course in enumerate(courses):
                # Choose action (slot, room) for this course
                action = self._choose_action(course, schedule)
                if action is None:
                    # No valid action: skip this course (will count as violation)
                    continue

                slot, room = action
                current_features = self._get_features(course, slot, room, schedule)

                # Place the course
                schedule.assign(course, slot, room)

                # Compute reward: full objective on current schedule
                reward = self.checker.objective(schedule)

                # Compute next state features (for the IMMEDIATE next course only, as per sequential MDP)
                next_features_list = []
                if i + 1 < len(courses):
                    next_course = courses[i + 1]
                    for next_slot, next_room in self.problem.domain(next_course):
                        f = self._get_features(next_course, next_slot, next_room, schedule)
                        next_features_list.append(f)

                # Update Q-Table
                self._update_q(current_features, reward, next_features_list)

            # Track best complete schedule
            if schedule.is_complete():
                score = self.checker.objective(schedule)
                if score > self.best_score:
                    self.best_score = score
                    self.best_schedule = schedule.copy()

            # Decay epsilon: reduce exploration over time
            self.epsilon = max(
                self.epsilon_min,
                self.epsilon - self.epsilon_decay
            )

        # If no complete schedule was ever found, return best partial
        if self.best_schedule is None:
            self.best_schedule = schedule


    # Solve — exploit learned policy


    def solve(self) -> Schedule:
        """
        After training, build one final schedule using pure exploitation (ε=0).
        Returns the best schedule found overall.
        """
        # Train the agent
        self.train()

        # Build a greedy schedule using learned Q-values (no exploration)
        saved_epsilon = self.epsilon
        self.epsilon = 0.0  # pure exploitation

        schedule = Schedule(self.problem)
        courses = list(self.problem.courses)
        random.shuffle(courses)

        for course in courses:
            action = self._choose_action(course, schedule)
            if action is not None:
                slot, room = action
                schedule.assign(course, slot, room)

        self.epsilon = saved_epsilon

        # Return the best schedule found (training or final greedy pass)
        final_score = self.checker.objective(schedule)
        if final_score > self.best_score:
            return schedule
        return self.best_schedule if self.best_schedule is not None else schedule


# Standalone solver function — interface expected by metrics.py


def solve(problem: CourseScheduleProblem, n_episodes: int = 1000) -> Schedule:
    """
    Entry point called by evaluation/metrics.py.

    Usage:
        from approaches.q_learning import solve
        schedule = solve(problem)
    """
    scheduler = QLearningScheduler(problem, n_episodes=n_episodes)
    return scheduler.solve()

# Quick test — run directly to verify on small instance


if __name__ == "__main__":
    from core.problem import CourseScheduleProblem
    from core.constraints import ConstraintChecker

    print("Loading small instance...")
    problem = CourseScheduleProblem.from_json("data/instance_05.json")

    print("Training Q-Learning agent (1000 episodes)...")
    scheduler = QLearningScheduler(problem, n_episodes=1000)
    solution = scheduler.solve()

    checker = ConstraintChecker(problem)
    violations = checker.hard_violations(solution)
    score = checker.soft_score(solution) if violations == 0 else 0.0

    print(f"\nResults:")
    print(f"  Hard violations : {violations}  (0 = valid)")
    print(f"  Soft score      : {score:.3f}  (0-1, higher is better)")
    print(f"  Q-Table size    : {len(scheduler.q_table)} entries")

    solution.pretty_print()
