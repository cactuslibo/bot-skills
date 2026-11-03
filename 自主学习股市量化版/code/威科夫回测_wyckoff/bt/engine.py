"""样本内回测引擎（只读 ≤2019-12-31 数据；样本外在加载时就被截断，物理上不可见）。"""
import os, json, hashlib, pickle, sys
import numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import wyckoff_v0 as W

IS_END = "2019-12-31"; EVAL_START = "2005-01-01"
DB = "/workspace/tv_db"; EXCL = {"ET", "IMO", "CVE"}
HS = (20, 40, 60)
CACHE = os.path.join(os.path.dirname(__file__), "cache"); os.makedirs(CACHE, exist_ok=True)
ARMS = {"E1": "entry_spring_next_open", "E2": "entry_after_test", "SOS": "entry_sos", "LPS": "entry_lps",
        "C1_touch": "entry_ctrl_touch", "C2_sos_only": "entry_ctrl_sos_only", "C3_lps_only": "entry_ctrl_lps_only"}

def tickers():
    u = pd.read_csv(f"{DB}/universe_10B.csv"); u = u[u.type == "stock"]
    return [s for s in u.Symbol if s not in EXCL and os.path.exists(f"{DB}/daily/{s}.csv")]

def load(t):
    df = pd.read_csv(f"{DB}/daily/{t}.csv", index_col=0, parse_dates=True)
    df = df.loc[:IS_END]                          # 样本外锁：此处截断
    df = df[(df.volume > 0) & (df.low > 0)]
    return df if len(df) >= 300 else None

def panel():
    p = os.path.join(CACHE, "panel.pkl")
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    O, C, L = {}, {}, {}
    for t in tickers():
        df = load(t)
        if df is None: continue
        O[t], C[t], L[t] = df.open, df.close, df.low
    P = {k: pd.DataFrame(v).sort_index() for k, v in (("open", O), ("close", C), ("low", L))}
    assert P["close"].index.max() <= pd.Timestamp(IS_END)
    # 等权全样本基准：同一窗口 open[t] -> close[t+H-1]
    P["bench"] = {H: (P["close"].shift(-(H - 1)) / P["open"] - 1).mean(axis=1) for H in HS}
    lr = np.log(P["close"]).diff()
    P["rv20"] = lr.rolling(20).std() * np.sqrt(252)
    P["ma200"] = P["close"].rolling(200, min_periods=200).mean()
    P["ma50"] = P["close"].rolling(50, min_periods=50).mean()
    pickle.dump(P, open(p, "wb")); return P

def _sig(args):
    t, params = args
    df = load(t)
    if df is None: return t, {}
    out = W.run_wyckoff(df, params)
    return t, {a: (out.index[out[c].to_numpy()], out["stop_level"][out[c]].to_numpy()) for a, c in ARMS.items()}

def signals(params, tag):
    p = os.path.join(CACHE, f"sig_{tag}.pkl")
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    with Pool(8) as pool:
        res = dict(pool.map(_sig, [(t, params) for t in tickers()], chunksize=8))
    pickle.dump(res, open(p, "wb")); return res

def trades(P, sig, arm, stop=True, stop_mode="intraday", buf=0.0, filt=None, volscale=False):
    """入场 T+1 开盘；持有 H 日到收盘；可选止损：盘中 low<stop 则以 min(open,stop) 离场，之后持现金。
    只保留出场日 ≤ IS_END 的交易（不跨入样本外）。"""
    idx = P["close"].index; rows = []
    for t, d in sig.items():
        if arm not in d or t not in P["close"]: continue
        dates, stops = d[arm]
        o, c, lo = P["open"][t].to_numpy(), P["close"][t].to_numpy(), P["low"][t].to_numpy()
        for dt, sl in zip(dates, stops):
            if dt < pd.Timestamp(EVAL_START): continue
            i = idx.get_loc(dt)
            if np.isnan(o[i]): continue
            if filt is not None and not filt(t, i - 1): continue   # 过滤器只看信号日 T=i-1 及以前
            r = {"t": t, "date": dt}
            for H in HS:
                j = i + H - 1
                if j >= len(idx) or np.isnan(c[j]): r = None; break
                b = P["bench"][H].iloc[i]
                raw = c[j] / o[i] - 1
                ex_px = c[j]
                if stop and sl == sl and arm in ("E1", "E2", "SOS", "LPS"):
                    slb = sl * (1 - buf)
                    if stop_mode == "intraday":
                        hit = np.where(lo[i:j + 1] < slb)[0]
                        if len(hit):
                            k = i + hit[0]; ex_px = min(o[k], slb)
                    else:   # "close"：收盘跌破才算，次日开盘离场（确认过滤）
                        hit = np.where(c[i:j] < slb)[0]
                        if len(hit): ex_px = o[i + hit[0] + 1]
                r[f"ex{H}"] = c[j] / o[i] - 1 - b
                r[f"exs{H}"] = ex_px / o[i] - 1 - b
            if r:
                if volscale:   # 波动率缩放仓位：w = 目标波动 / 信号日前 20 日实现波动（上限 2）
                    rv = P["rv20"][t].iloc[i - 1]; w = min(0.25 / rv, 2.0) if rv == rv and rv > 0 else 1.0
                    for k2 in list(r):
                        if k2.startswith("ex"): r[k2] *= w
                rows.append(r)
    return pd.DataFrame(rows)

def random_ctrl(P, n, seed=0):
    """C4：在同一标的池随机抽 (标的, 日期)，数量 = n×5。"""
    rng = np.random.default_rng(seed); C = P["close"]; ev = C.loc[EVAL_START:].index
    rows = []; ts = list(C.columns)
    while len(rows) < 5 * n:
        t = ts[rng.integers(len(ts))]; dt = ev[rng.integers(len(ev))]; i = C.index.get_loc(dt)
        o = P["open"][t].iloc[i]; r = {"t": t, "date": dt}
        for H in HS:
            j = i + H - 1
            if j >= len(C) or np.isnan(o) or np.isnan(C[t].iloc[j]): r = None; break
            r[f"ex{H}"] = r[f"exs{H}"] = C[t].iloc[j] / o - 1 - P["bench"][H].iloc[i]
        if r: rows.append(r)
    return pd.DataFrame(rows)

def metrics(df, key="exs20"):
    if len(df) == 0: return {"n": 0}
    m = {"n": len(df)}
    for H in HS:
        for pre in ("ex", "exs"):
            x = df[f"{pre}{H}"]
            m[f"{pre}{H}"] = x.mean()
            if pre == "exs" or H == 20:
                m[f"win_{pre}{H}"] = (x > 0).mean()
                neg = x[x < 0].mean(); m[f"pf_{pre}{H}"] = x[x > 0].mean() / -neg if neg < 0 else np.nan
    mon = df.groupby(df.date.dt.to_period("M"))[key].mean()     # 按月聚类，缓解重叠相关
    x = df[key]; m["q05"] = x.quantile(0.05); m["worst"] = x.min()
    m["months"] = len(mon); m["t_month"] = mon.mean() / mon.std(ddof=1) * np.sqrt(len(mon)) if len(mon) > 2 else np.nan
    m["sr_month"] = mon.mean() / mon.std(ddof=1) if len(mon) > 2 else np.nan
    yr = df.groupby(df.date.dt.year)[key].mean(); m["yrs_pos"] = f"{(yr>0).sum()}/{len(yr)}"
    return m

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
