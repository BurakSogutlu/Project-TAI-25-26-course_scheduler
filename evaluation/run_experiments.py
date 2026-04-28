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

# Import solvers
from approaches.csp_solver import CSPSolver as CSP_FirstSol
from approaches.csp_solver_timeout import CSPSolver as CSP_Anytime
from approaches.local_search import solve as solve_sa
from approaches.q_learning import solve as solve_ql

def run_experiments():
    instances = ["instance_05", "instance_15", "instance_30", "instance_60", "instance_100", "instance_125", "instance_150"]
    
    results = []
    
    # We set a shorter timeout for the Anytime algorithm in the test to not wait too long overall
    # The timeout is in seconds.
    TIMEOUT_ANYTIME = 30.0
    
    for inst_name in instances:
        print(f"\n{'='*50}\n--- Testing on {inst_name} ---\n{'='*50}")
        problem_path = f"data/{inst_name}.json"
        
        if not os.path.exists(problem_path):
            print(f"Warning: {problem_path} not found. Make sure to generate it first.")
            continue
            
        problem = CourseScheduleProblem.from_json(problem_path)
        checker = ConstraintChecker(problem)
        num_courses = len(problem.courses)
        
        # 1. CSP (First Sol)
        print("\n>>> Running CSP (First Sol)...")
        if inst_name == "instance_150":
            print(f"    (Skipping CSP First Sol on {inst_name} to avoid infinite DFS hang. Use Anytime instead.)")
        else:
            solver1 = CSP_FirstSol(problem, use_mrv=True, use_degree=True, use_lcv=True, use_fc=True)
            start = time.time()
            sch1 = solver1.solve()
            t1 = time.time() - start
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
        start = time.time()
        sch2 = solver2.solve()
        t2 = time.time() - start
        if sch2:
            v2 = checker.hard_violations(sch2)
            s2 = checker.soft_score(sch2)
            print(f"Done in {t2:.2f}s | Violations: {v2} | Soft Score: {s2:.3f}")
            results.append({
                "Instance": inst_name, "Courses": num_courses, "Algorithm": f"CSP (Anytime {TIMEOUT_ANYTIME}s)",
                "Time (s)": t2, "Violations": v2, "Soft Score": s2
            })

        # 3. Local Search (Simulated Annealing)
        print("\n>>> Running Local Search (Simulated Annealing)...")
        start = time.time()
        sa_iters = 4000
        if num_courses > 100:
            sa_iters = 500
        elif num_courses > 25:
            sa_iters = 2000
        print(f"    (Running for {sa_iters} iterations)")
        sch3 = solve_sa(problem, iterations=sa_iters)
        t3 = time.time() - start
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
        start = time.time()
        episodes = 1000
        if num_courses > 100:
            episodes = 2  # VERY slow in python due to O(C^3) loop
        elif num_courses > 25:
            episodes = 50
        print(f"    (Training for {episodes} episodes to avoid excessive wait time)")
        sch4 = solve_ql(problem, n_episodes=episodes)
        t4 = time.time() - start
        if sch4:
            v4 = checker.hard_violations(sch4)
            s4 = checker.soft_score(sch4)
            print(f"Done in {t4:.2f}s | Violations: {v4} | Soft Score: {s4:.3f}")
            results.append({
                "Instance": inst_name, "Courses": num_courses, "Algorithm": "Q-Learning",
                "Time (s)": t4, "Violations": v4, "Soft Score": s4
            })
            
    # Save CSV
    df = pd.DataFrame(results)
    out_dir = Path("evaluation")
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / "results.csv", index=False)
    
    print(f"\n{'='*50}\nFINAL RESULTS\n{'='*50}")
    print(df.to_string())
    print(f"\nResults saved to {out_dir / 'results.csv'}")

    # Plotting
    plot_dir = out_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    # We need to sort dataframe by Courses to ensure lines in plot go left-to-right
    df = df.sort_values(by="Courses")

    # Define styles to prevent perfect overlap hiding lines
    styles = {
        "CSP (First Sol)": {"color": "blue", "linestyle": "-", "marker": "o"},
        f"CSP (Anytime {TIMEOUT_ANYTIME}s)": {"color": "orange", "linestyle": "--", "marker": "x"},
        "Simulated Annealing": {"color": "green", "linestyle": "-.", "marker": "s"},
        "Q-Learning": {"color": "red", "linestyle": ":", "marker": "^"}
    }

    # Plot 1: Soft Score vs Courses
    plt.figure(figsize=(10, 6))
    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]
        style = styles.get(algo, {"color": "black", "linestyle": "-", "marker": "o"})
        plt.plot(subset["Courses"], subset["Soft Score"], label=algo, linewidth=2.5, **style)
    plt.title("Qualité du Planning (Soft Score) vs Complexité (Nb de cours)", fontsize=14)
    plt.xlabel("Nombre de cours (Taille de l'instance)", fontsize=12)
    plt.ylabel("Soft Score (0.0 - 1.0)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / "soft_score.png", dpi=300)
    plt.close()

    # Plot 2: Time vs Courses
    plt.figure(figsize=(10, 6))
    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]
        style = styles.get(algo, {"color": "black", "linestyle": "-", "marker": "o"})
        plt.plot(subset["Courses"], subset["Time (s)"], label=algo, linewidth=2.5, **style)
    plt.title("Temps d'exécution vs Complexité", fontsize=14)
    plt.xlabel("Nombre de cours (Taille de l'instance)", fontsize=12)
    plt.ylabel("Temps (secondes)", fontsize=12)
    plt.yscale('log') # Use logarithmic scale for time to better see small differences
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / "time.png", dpi=300)
    plt.close()

    # Plot 3: Violations vs Courses
    plt.figure(figsize=(10, 6))
    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]
        style = styles.get(algo, {"color": "black", "linestyle": "-", "marker": "o"})
        plt.plot(subset["Courses"], subset["Violations"], label=algo, linewidth=2.5, **style)
    plt.title("Robustesse (Violations Hard) vs Complexité", fontsize=14)
    plt.xlabel("Nombre de cours (Taille de l'instance)", fontsize=12)
    plt.ylabel("Nombre de violations de contraintes dures", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_dir / "violations.png", dpi=300)
    plt.close()

    print(f"Graphs generated successfully in {plot_dir}/")

if __name__ == '__main__':
    run_experiments()
