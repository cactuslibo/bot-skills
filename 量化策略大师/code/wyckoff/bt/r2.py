import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from run_round import *
V = {}; TK = {}
for b in ("V1_base", "V3_pierce_clx"):
    for tag, o in {"in3": dict(buf=0.03), "cl0": dict(stop_mode="close"), "cl3": dict(stop_mode="close", buf=0.03),
                   "nsVS": dict(stop=False, volscale=True)}.items():
        V[f"{b}@{tag}"] = W.VARIANTS[b]; TK[f"{b}@{tag}"] = o
df, N, pb = run("R2", V, controls=False, tk=TK)
print(fmt(df)); print("n_trials", N, "PBO", pb)
