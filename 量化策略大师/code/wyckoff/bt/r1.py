import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from run_round import *
df, N, pb = run("R1", W.VARIANTS)
print(fmt(df)); print("n_trials", N, "PBO", pb)
