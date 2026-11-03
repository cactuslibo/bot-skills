import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from dataclasses import replace
from run_round import *
P = panel(); up = lambda t, i: P["close"][t].iloc[i] > P["ma200"][t].iloc[i]
b = W.VARIANTS["V3_pierce_clx"]
G = {"clx1.25": dict(pierce_vol_climax=1.25), "clx2.0": dict(pierce_vol_climax=2.0),
     "tv0.75": dict(test_vol_ratio_max=0.75), "tv1.0": dict(test_vol_ratio_max=1.0),
     "r1": dict(reclaim_bars=1), "r5": dict(reclaim_bars=5)}
V = {}; TK = {}
for k, d in G.items():
    n = f"V3n_{k}"; V[n + "@nsVS_up200"] = replace(b, **d); TK[n + "@nsVS_up200"] = dict(stop=False, volscale=True, filt=up)
df, N, pb = run("R4", V, controls=False, tk=TK)
print(fmt(df)); print("n_trials", N, "PBO", pb)
