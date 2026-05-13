import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.problem import CourseScheduleProblem
from core.constraints import ConstraintChecker

from approaches.csp_solver import CSPSolver as CSP_FirstSol
from approaches.csp_solver_timeout import CSPSolver as CSP_Anytime
from approaches.local_search import solve as solve_sa
from approaches.q_learning import solve as solve_ql


def run_experiments():
    instances = ["instance_05", "instance_15", "instance_30", "instance_60", "instance_100", "instance_125", "instance_150"]

    results = []

    TIMEOUT_ANYTIME = 30.0

    for inst_name in instances:
        print(f"\n{'='*50}\n--- Testing on {inst_name} ---\n{'='*50}")
        problem_path = f"data/{inst_name}.json"

        if not os.path.exists(problem_path):
            print(f"Warning: {problem_path} not found. Run the instance generator first.")
            continue

        problem     = CourseScheduleProblem.from_json(problem_path)
        checker     = ConstraintChecker(problem)
        num_courses = len(problem.courses)

        # 1. CSP (First Sol)
        print("\n>>> Running CSP (First Sol)...")
        if inst_name == "instance_150":
            print(f"    (Skipping on {inst_name} — known to hang. Use Anytime instead.)")
        else:
            solver1 = CSP_FirstSol(problem, use_mrv=True, use_degree=True, use_lcv=True, use_fc=True)
            start   = time.time()
            sch1    = solver1.solve()
            t1      = time.time() - start
            if sch1:
                v1 = checker.hard_violations(sch1)
                s1 = checker.soft_score(sch1)
                print(f"Done in {t1:.2f}s | Violations: {v1} | Soft Score: {s1:.3f}")
                results.append({
                    "Instance": inst_name, "Courses": num_courses, "Algorithm": "CSP (First Sol)",
                    "Time (s)": t1, "Violations": v1, "Soft Score": s1
                })

        # 2. CSP (Anytime)
        print(f"\n>>> Running CSP (Anytime {TIMEOUT_ANYTIME}s)...")
        solver2 = CSP_Anytime(problem, use_mrv=True, use_degree=True, use_lcv=True, use_fc=True, time_limit=TIMEOUT_ANYTIME)
        start   = time.time()
        sch2    = solver2.solve()
        t2      = time.time() - start
        if sch2:
            v2 = checker.hard_violations(sch2)
            s2 = checker.soft_score(sch2)
            print(f"Done in {t2:.2f}s | Violations: {v2} | Soft Score: {s2:.3f}")
            results.append({
                "Instance": inst_name, "Courses": num_courses, "Algorithm": f"CSP (Anytime {TIMEOUT_ANYTIME}s)",
                "Time (s)": t2, "Violations": v2, "Soft Score": s2
            })

        # 3. Simulated Annealing
        print("\n>>> Running Local Search (Simulated Annealing)...")
        sa_iters = 4000
        if num_courses > 100:
            sa_iters = 500
        elif num_courses > 25:
            sa_iters = 2000
        print(f"    ({sa_iters} iterations)")
        start = time.time()
        sch3  = solve_sa(problem, iterations=sa_iters)
        t3    = time.time() - start
        if sch3:
            v3 = checker.hard_violations(sch3)
            s3 = checker.soft_score(sch3)
            print(f"Done in {t3:.2f}s | Violations: {v3} | Soft Score: {s3:.3f}")
            results.append({
                "Instance": inst_name, "Courses": num_courses, "Algorithm": "Simulated Annealing",
                "Time (s)": t3, "Violations": v3, "Soft Score": s3
            })

        # 4. Q-Learning
        print("\n>>> Running Q-Learning...")
        episodes = 1000
        if num_courses > 100:
            episodes = 2  # very slow in Python due to O(C³) feature loop
        elif num_courses > 25:
            episodes = 50
        print(f"    ({episodes} episodes)")
        start = time.time()
        sch4  = solve_ql(problem, n_episodes=episodes)
        t4    = time.time() - start
        if sch4:
            v4 = checker.hard_violations(sch4)
            s4 = checker.soft_score(sch4)
            print(f"Done in {t4:.2f}s | Violations: {v4} | Soft Score: {s4:.3f}")
            results.append({
                "Instance": inst_name, "Courses": num_courses, "Algorithm": "Q-Learning",
                "Time (s)": t4, "Violations": v4, "Soft Score": s4
            })

    df      = pd.DataFrame(results)
    out_dir = Path("evaluation")
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)

    print(f"\n{'='*50}\nFINAL RESULTS\n{'='*50}")
    print(df.to_string())
    print(f"\nResults saved to {out_dir / 'results.csv'}")

    plot_dir = out_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    df = df.sort_values(by="Courses")

    styles = {
        "CSP (First Sol)":               {"color": "blue",   "linestyle": "-",  "marker": "o"},
        f"CSP (Anytime {TIMEOUT_ANYTIME}s)": {"color": "orange", "linestyle": "--", "marker": "x"},
        "Simulated Annealing":           {"color": "green",  "linestyle": "-.", "marker": "s"},
        "Q-Learning":                    {"color": "red",    "linestyle": ":",  "marker": "^"},
    }

    plt.figure(figsize=(10, 6))
    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]
        style  = styles.get(algo, {"color": "black", "linestyle": "-", "marker": "o"})
        plt.plot(subset["Courses"], subset["Soft Score"], label=algo, linewidth=2.5, **style)
    plt.title("Schedule Quality (Soft Score) vs Instance Size", fontsize=14)
    plt.xlabel("Number of courses", fontsize=12)
    plt.ylabel("Soft Score (0.0 – 1.0)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / "soft_score.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]
        style  = styles.get(algo, {"color": "black", "linestyle": "-", "marker": "o"})
        plt.plot(subset["Courses"], subset["Time (s)"], label=algo, linewidth=2.5, **style)
    plt.title("Runtime vs Instance Size", fontsize=14)
    plt.xlabel("Number of courses", fontsize=12)
    plt.ylabel("Time (seconds)", fontsize=12)
    plt.yscale('log')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / "time.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]
        style  = styles.get(algo, {"color": "black", "linestyle": "-", "marker": "o"})
        plt.plot(subset["Courses"], subset["Violations"], label=algo, linewidth=2.5, **style)
    plt.title("Hard Constraint Violations vs Instance Size", fontsize=14)
    plt.xlabel("Number of courses", fontsize=12)
    plt.ylabel("Number of hard constraint violations", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / "violations.png", dpi=300)
    plt.close()

    print(f"Plots saved to {plot_dir}/")


if __name__ == '__main__':
    run_experiments()
