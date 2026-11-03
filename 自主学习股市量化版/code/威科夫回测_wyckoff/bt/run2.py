import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from engine2 import *
from engine import metrics
from stats import dsr, pbo
from run_round import LEDGER, ledger, fmt
P = panel(); M = market(P); SIG = {}
def sig(n):
    if n not in SIG: SIG[n] = signals2(W.VARIANTS[n], n)
    return SIG[n]
def allsr():
    out = []
    for f in os.listdir(CACHE):
        if f.startswith(("tr_", "tr2_")):
            tr = pd.read_pickle(os.path.join(CACHE, f))
            if len(tr) > 30: out.append(metrics(tr)["sr_month"])
    return np.nanvar(out)
def run(rnd, specs):
    """specs: key -> (base, arm, exit, filt)"""
    L = ledger(); res = {}; mon = {}
    for key, (b, a, ex, f) in specs.items():
        tr = trades2(P, sig(b), a, exit=ex, filt=f)
        tr.to_pickle(os.path.join(CACHE, "tr2_" + key.replace("|", "_").replace("/", "_") + ".pkl"))
        res[key] = metrics(tr)
        if len(tr): mon[key] = tr.groupby(tr.date.dt.to_period("M"))["exs20"].mean()
        if key not in [x["key"] for x in L["trials"]]:
            L["trials"].append({"key": key, "round": rnd, "base": b, "arm": a, "exit": ex})
    json.dump(L, open(LEDGER, "w"), indent=1); N = len(L["trials"]); v = allsr()
    for k, m in res.items():
        if m.get("n", 0) > 30: m["DSR"], m["SR0"] = dsr(m["sr_month"], m["months"], N, v)
    df = pd.DataFrame(res).T
    cols = ["n", "ex20", "exs20", "exs40", "exs60", "win_exs20", "pf_exs20", "q05", "worst", "t_month", "DSR", "yrs_pos"]
    df = df[[c for c in cols if c in df]]
    for c in ("q05", "worst"):
        if c in df: df[c] = df[c].map(lambda x: f"{x*100:.1f}%")
    Mx = pd.DataFrame(mon); pb = pbo(Mx) if Mx.shape[1] >= 4 else np.nan
    print(fmt(df)); print("n_trials", N, "PBO", pb)
    return df, N, pb
# 过滤器（只用信号日 T 及以前）
F = {
 "base30": lambda t, T, f: f.dd52 <= -0.30 and f.range_run >= 40,
 "dry": lambda t, T, f: bool(f.dry_half) and bool(f.dry_ud),
 "rs": lambda t, T, f: bool(f.stk_nolow) and bool(M.ix_newlow.get(T, False)),
 "mkt": lambda t, T, f: bool(M.ix_up.get(T, False)) or bool(M.br_up.get(T, False)),
 "up200": lambda t, T, f: P["close"][t].get(T, np.nan) > P["ma200"][t].get(T, np.nan),
}
