import sys, json, os, pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from engine import *
from stats import dsr, pbo
LEDGER = os.path.join(os.path.dirname(__file__), "trials.json")
def ledger():
    return json.load(open(LEDGER)) if os.path.exists(LEDGER) else {"trials": []}
def run(round_name, variants, arms=("E1", "E2"), controls=True, count=True, tk=None):
    P = panel(); L = ledger(); res = {}; monthly = {}
    for name, prm in variants.items():
        base = name.split("@")[0]; opts = (tk or {}).get(name, {})
        sig = signals(prm, base)
        for a in arms:
            tr = trades(P, sig, a, **opts); key = f"{name}|{a}"
            res[key] = metrics(tr); tr.to_pickle(os.path.join(CACHE, f"tr_{key.replace('|','_')}.pkl"))
            if len(tr): monthly[key] = tr.groupby(tr.date.dt.to_period("M"))["exs20"].mean()
            if count and key not in [x["key"] for x in L["trials"]]:
                L["trials"].append({"key": key, "round": round_name, "params": {k: v for k, v in prm.__dict__.items() if getattr(W.DEFAULT_PARAMS, k) != v}, "trade_opts": {k: str(v) for k, v in opts.items()}})
        if controls and name == list(variants)[0]:
            for a in ("C1_touch", "C2_sos_only", "C3_lps_only"):
                tr = trades(P, sig, a, stop=False); res[f"ctrl|{a}"] = metrics(tr)
            n = max(res[f"{name}|E1"]["n"], 1); res["ctrl|C4_random"] = metrics(random_ctrl(P, n))
    json.dump(L, open(LEDGER, "w"), indent=1)
    N = len(L["trials"])
    # DSR：用全部累计试验的月 SR 方差（只能拿到已缓存的试验）
    allsr = []
    for x in L["trials"]:
        f = os.path.join(CACHE, f"tr_{x['key'].replace('|','_')}.pkl")
        if os.path.exists(f):
            tr = pd.read_pickle(f)
            if len(tr) > 30: allsr.append(metrics(tr)["sr_month"])
    v = np.nanvar(allsr) if len(allsr) > 1 else 0.0
    for k, m in res.items():
        if m.get("n", 0) > 30 and not k.startswith("ctrl"):
            m["DSR"], m["SR0"] = dsr(m["sr_month"], m["months"], N, v)
    df = pd.DataFrame(res).T
    cols = ["n", "ex20", "ex40", "ex60", "exs20", "exs40", "exs60", "win_exs20", "pf_exs20", "t_month", "DSR", "yrs_pos"]
    df = df[[c for c in cols if c in df]]
    M = pd.DataFrame(monthly)
    pb = pbo(M) if M.shape[1] >= 4 else np.nan
    return df, N, pb
def fmt(df):
    d = df.copy()
    for c in d:
        if c.startswith(("ex", "win")): d[c] = d[c].map(lambda x: f"{x*100:.2f}%" if x == x else "")
        elif c in ("pf_exs20", "t_month", "DSR"): d[c] = d[c].map(lambda x: f"{x:.2f}" if isinstance(x, float) and x == x else "")
    return d.to_markdown()
