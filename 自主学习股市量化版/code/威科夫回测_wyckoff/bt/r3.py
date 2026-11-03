import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from run_round import *
P = panel()
up = lambda t, i: P["close"][t].iloc[i] > P["ma200"][t].iloc[i]
dn = lambda t, i: P["close"][t].iloc[i] <= P["ma200"][t].iloc[i]
V = {}; TK = {}
for b in ("V1_base", "V3_pierce_clx"):
    for tag, f in {"up200": up, "dn200": dn}.items():
        V[f"{b}@nsVS_{tag}"] = W.VARIANTS[b]; TK[f"{b}@nsVS_{tag}"] = dict(stop=False, volscale=True, filt=f)
df, N, pb = run("R3", V, controls=False, tk=TK)
print(fmt(df)); print("n_trials", N, "PBO", pb)
