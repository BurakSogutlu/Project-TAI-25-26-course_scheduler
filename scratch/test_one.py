import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.problem import CourseScheduleProblem
from core.constraints import ConstraintChecker

from approaches.csp_solver import CSPSolver as CSP_FirstSol
from approaches.csp_solver_timeout import CSPSolver as CSP_Anytime
from approaches.local_search import solve as solve_sa
from approaches.q_learning import solve as solve_ql

algo = sys.argv[1]
instance = sys.argv[2]

problem = CourseScheduleProblem.from_json(f"data/{instance}.json")

print(f"Testing {algo} on {instance} ({len(problem.courses)} courses)...")
start = time.time()

if algo == "csp":
    solver = CSP_FirstSol(problem, use_mrv=True, use_degree=True, use_lcv=True, use_fc=True)
    solver.solve()
elif algo == "csp_anytime":
    solver = CSP_Anytime(problem, use_mrv=True, use_degree=True, use_lcv=True, use_fc=True, time_limit=10.0)
    solver.solve()
elif algo == "sa":
    solve_sa(problem, iterations=100) # Small iterations to test
elif algo == "ql":
    solve_ql(problem, n_episodes=20) # Small episodes

print(f"Done in {time.time() - start:.2f}s")
