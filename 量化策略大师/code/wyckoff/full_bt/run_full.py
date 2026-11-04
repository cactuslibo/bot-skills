"""威科夫筑底全样本回测（2005-01-01 ~ 2026-11-03，全部数据，无样本外保留）。
信号 raw_* 在 T 日收盘确认 -> T+1 开盘入场（等价 entry_* = raw_*.shift(1)）。"""
import os, sys, pickle, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, "/workspace/wyckoff"); sys.path.insert(0, "/workspace/wyckoff/bt")
import wyckoff_v0 as W
from stats import pbo, dsr
D = "/workspace/wyckoff/data_1b"; OUT = "/workspace/wyckoff/full_bt"
START = pd.Timestamp("2005-01-01"); HS = (5, 10, 20, 40, 60); COST = 0.002; GAP = 10
VARS = {"V1_base": W.VARIANTS["V1_base"], "V3_pierce_clx": W.VARIANTS["V3_pierce_clx"]}
U = pd.read_csv("/workspace/wyckoff/universe.csv").drop_duplicates("ticker").set_index("ticker")
SPY = pd.read_csv(f"{OUT}/SPY.csv", index_col=0, parse_dates=True)

def segments(t):
    df = pd.read_csv(f"{D}/{t}.csv", index_col=0, parse_dates=True).sort_index()
    df = df[(df.volume > 0) & (df.low > 0)].dropna()
    gid = (df.index.to_series().diff().dt.days > GAP).cumsum()          # 缺口>10 天处切断
    segs = []
    for _, s in df.groupby(gid):
        dv = (s.close * s.volume).rolling(60).median()
        ok = np.where(dv.to_numpy() >= 1e6)[0]                           # 剔除开头低流动性段（SPAC 壳/前身）
        if not len(ok): continue
        s = s.iloc[max(ok[0] - 59, 0):]
        if len(s) >= 150: segs.append(s)
    return segs

def one(t):
    res = {v: [] for v in VARS}; cur = {}; elig = []
    for s in segments(t):
        o, h, l, c, vol = (s[k].to_numpy() for k in ["open", "high", "low", "close", "volume"])
        adv = (s.close * s.volume).rolling(20).mean().to_numpy()
        liq = (c >= 3) & (adv >= 1e6)
        idx = s.index; n = len(s)
        so = SPY.open.reindex(idx).to_numpy(); sc = SPY.close.reindex(idx).to_numpy()
        def trade(T, stop, kind, var, arm, sdate=None):
            i = T + 1
            if i + max(HS) - 1 >= n and i + min(HS) - 1 >= n: return None
            r = {"t": t, "var": var, "arm": arm, "kind": kind, "sig": idx[T], "date": idx[i] if i < n else None, "spring": sdate}
            if i >= n: return None
            for H in HS:
                j = i + H - 1
                if j >= n: r[f"r{H}"] = r[f"rs{H}"] = r[f"x{H}"] = r[f"xs{H}"] = np.nan; continue
                raw = c[j] / o[i] - 1; px = c[j]
                if stop == stop:
                    hit = np.where(l[i:j + 1] < stop)[0]
                    if len(hit): px = min(o[i + hit[0]], stop)
                b = sc[j] / so[i] - 1 if so[i] == so[i] and sc[j] == sc[j] else np.nan
                r[f"r{H}"] = raw - COST; r[f"rs{H}"] = px / o[i] - 1 - COST
                r[f"x{H}"] = r[f"r{H}"] - b; r[f"xs{H}"] = r[f"rs{H}"] - b
            return r
        evalok = (idx >= START) & liq
        evalok[n - 1] = False
        elig.append((s, np.where(evalok)[0]))
        for var, P in VARS.items():
            out = W.run_wyckoff(s, P)
            spl = out.spring_low.to_numpy()
            sp = np.where(out.raw_spring.to_numpy())[0]; te = np.where(out.raw_test.to_numpy())[0]
            for T in sp:
                if evalok[T]:
                    x = trade(T, spl[T], "sig", var, "E1", idx[T]); x and res[var].append(x)
            for T in te:
                if evalok[T]:
                    sd = idx[sp[sp <= T][-1]] if (sp <= T).any() else None
                    x = trade(T, spl[T], "sig", var, "E2", sd); x and res[var].append(x)
            if s is not None and s.index[-1] == segments_last(t):
                cur[var] = dict(out=out[["state", "spring_low", "raw_spring", "raw_test"]].iloc[-40:], close=c[-1], last=idx[-1],
                                liq=bool(liq[-1]), low=s.low.iloc[-40:])
        res["_trade"] = trade
    res.pop("_trade", None)
    # 随机日期对照：每个 (变体,臂) 用相同笔数，同一标的可交易日随机抽，5 次重复
    rng = np.random.default_rng(abs(hash(t)) % 2**32)
    ctrl = []
    for var in VARS:
        for arm in ("E1", "E2"):
            k = sum(1 for r in res[var] if r["arm"] == arm)
            if not k: continue
            for rep in range(5):
                for s, ok in elig:
                    pass
                pool = [(si, T) for si, (s, ok) in enumerate(elig) for T in ok]
                if not pool: continue
                pick = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
                for pi in pick:
                    si, T = pool[pi]; s = elig[si][0]
                    ctrl.append(_ctrl_trade(t, s, T, var, arm, rep))
    return t, res, [x for x in ctrl if x], cur

_last = {}
def segments_last(t):
    if t not in _last:
        sg = segments(t); _last[t] = sg[-1].index[-1] if sg else None
    return _last[t]

def _ctrl_trade(t, s, T, var, arm, rep):
    o, c = s.open.to_numpy(), s.close.to_numpy(); n = len(s); i = T + 1
    so = SPY.open.reindex(s.index).to_numpy(); sc = SPY.close.reindex(s.index).to_numpy()
    r = {"t": t, "var": var, "arm": arm, "kind": "rand", "rep": rep, "sig": s.index[T], "date": s.index[i]}
    for H in HS:
        j = i + H - 1
        if j >= n: r[f"r{H}"] = r[f"x{H}"] = np.nan; continue
        r[f"r{H}"] = c[j] / o[i] - 1 - COST; b = sc[j] / so[i] - 1
        r[f"x{H}"] = r[f"r{H}"] - b
    return r

if __name__ == "__main__":
    tks = [t for t in U.index if os.path.exists(f"{D}/{t}.csv")]
    with Pool(8) as p:
        R = p.map(one, tks, chunksize=4)
    pickle.dump(R, open(f"{OUT}/raw_results.pkl", "wb"))
    print("done", len(R))
