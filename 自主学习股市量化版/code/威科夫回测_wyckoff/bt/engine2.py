"""第二阶段：带特征的信号 + 成本 + 更多出场。仍只读 ≤2019-12-31。"""
import os, sys, pickle, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from engine import load, tickers, panel, CACHE, EVAL_START, HS, W
COST = 0.002   # 单边 10bp × 往返
ARMS2 = {"E1": "raw_spring", "E2": "raw_test", "LPS": "raw_lps"}

def _sig2(args):
    t, params = args
    df = load(t)
    if df is None: return t, None
    out = W.run_wyckoff(df, params)
    c, v = df.close, df.volume
    ro = out.range_ok.astype(int); run = ro.groupby((ro == 0).cumsum()).cumsum()
    pc = c.shift(1); up = c > pc; dn = c < pc
    F = pd.DataFrame(index=df.index)
    F["range_run"] = run.shift(1)                                   # 截至 T-1 连续合格天数
    cs = c.shift(60); F["dd52"] = cs / cs.rolling(252).max() - 1      # 区间开始时距 52 周高点
    F["dry_half"] = (v.shift(1).rolling(30).mean() < v.shift(31).rolling(30).mean())
    vu = (v * up).shift(1).rolling(60).sum() / up.shift(1).rolling(60).sum()
    vd = (v * dn).shift(1).rolling(60).sum() / dn.shift(1).rolling(60).sum()
    F["dry_ud"] = vd < vu
    F["stk_nolow"] = c.shift(1).rolling(20).min() >= c.shift(21).rolling(40).min()
    h, l = df.high, df.low
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    F["atr"] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    F["stop"] = out.spring_low
    res = {}
    for a, col in ARMS2.items():
        m = out[col].to_numpy()
        res[a] = F[m].copy()            # 行索引 = 信号日 T（T+1 开盘入场）
    return t, res

def signals2(params, tag):
    p = os.path.join(CACHE, f"sig2_{tag}.pkl")
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    with Pool(8) as pool:
        res = dict(pool.map(_sig2, [(t, params) for t in tickers()], chunksize=8))
    pickle.dump(res, open(p, "wb")); return res

def market(P):
    p = os.path.join(CACHE, "market.pkl")
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    r = P["close"].pct_change(fill_method=None).mean(axis=1).fillna(0); ix = (1 + r).cumprod()
    br = (P["close"] > P["ma200"]).where(P["ma200"].notna()).mean(axis=1)
    M = pd.DataFrame({"ix": ix, "ix_up": ix > ix.rolling(200).mean(),
                      "ix_newlow": ix.rolling(20).min() < ix.shift(20).rolling(40).min(),
                      "breadth": br, "br_up": br > br.shift(20)})
    pickle.dump(M, open(p, "wb")); return M

def trades2(P, sig, arm, exit="none", filt=None, volscale=True):
    """exit: none | intra_atr1 | intra_atr2 | close0 | intra0。止损后持现金。扣往返 20bp。"""
    idx = P["close"].index; rows = []
    for t, d in sig.items():
        if not d or t not in P["close"]: continue
        F = d[arm]
        o, c, lo = P["open"][t].to_numpy(), P["close"][t].to_numpy(), P["low"][t].to_numpy()
        for T, f in F.iterrows():
            if T < pd.Timestamp(EVAL_START) or T not in idx: continue
            if filt is not None and not filt(t, T, f): continue
            i = idx.get_loc(T) + 1
            if i >= len(idx) or np.isnan(o[i]): continue
            sl = f["stop"]
            if exit.startswith("intra_atr"): sl = sl - float(exit[-1]) * f["atr"]
            r = {"t": t, "date": idx[i]}
            for H in HS:
                j = i + H - 1
                if j >= len(idx) or np.isnan(c[j]): r = None; break
                b = P["bench"][H].iloc[i]; px = c[j]
                if exit != "none" and sl == sl:
                    if exit == "close0":
                        hit = np.where(c[i:j] < sl)[0]
                        if len(hit): px = o[i + hit[0] + 1]
                    else:
                        hit = np.where(lo[i:j + 1] < sl)[0]
                        if len(hit): px = min(o[i + hit[0]], sl)
                r[f"ex{H}"] = c[j] / o[i] - 1 - b - COST
                r[f"exs{H}"] = px / o[i] - 1 - b - COST
            if r is None: continue
            if volscale:
                rv = P["rv20"][t].iloc[i - 1]; w = min(0.25 / rv, 2.0) if rv == rv and rv > 0 else 1.0
                for k in list(r):
                    if k.startswith("ex"): r[k] *= w
            rows.append(r)
    return pd.DataFrame(rows)
