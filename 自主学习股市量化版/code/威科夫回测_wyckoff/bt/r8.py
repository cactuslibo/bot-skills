from run2 import *
import glob
from scipy.stats import spearmanr
C = P["close"]; idx = C.index
S = pd.DataFrame(0.0, index=idx, columns=C.columns)
for b in ("V1_base", "V3_pierce_clx"):
    for a, w in (("E1", 1.0), ("E2", 2.0)):
        for t, d in sig(b).items():
            if not d or t not in S: continue
            ev = pd.Series(1.0, index=d[a].index).reindex(idx, fill_value=0)
            S[t] += w * ev.rolling(10, min_periods=1).max()
S += 0.5 * (C > P["ma200"]).astype(float)
fwd = (C.shift(-20) / P["open"].shift(-1) - 1)            # T+1 开盘 → T+20 收盘
fwd = fwd.sub(fwd.mean(axis=1), axis=0)
wk = [d for d in idx[idx >= EVAL_START] if d.weekday() == 4]; wk = [d for d in wk if idx.get_loc(d) + 21 < len(idx)]
rng = np.random.default_rng(0); ic = []; sp = []
for d in wk:
    s = S.loc[d]; f = fwd.loc[d]; m = s.notna() & f.notna() & C.loc[d].notna()
    s, f = s[m] + rng.uniform(0, 1e-6, m.sum()), f[m]
    if s.std() == 0 or len(s) < 50: continue
    ic.append(spearmanr(s, f)[0]); q = s.rank(pct=True)
    sp.append(f[q >= 0.9].mean() - f[q <= 0.1].mean() - 0.004)   # 多空两边各往返 20bp
ic, sp = pd.Series(ic), pd.Series(sp)
nw = lambda x: x.mean() / x.std() * np.sqrt(len(x) / 4)          # 周频、20 日重叠：有效样本约 /4
print(f"weeks={len(ic)} IC={ic.mean():.4f} ICIR={ic.mean()/ic.std():.3f} t≈{nw(ic):.2f}  D10-D1={sp.mean()*100:.2f}% t≈{nw(sp):.2f}")
L = ledger(); L["trials"].append({"key": "R8|xsec_score", "round": "R8"}); json.dump(L, open(LEDGER, "w"), indent=1); print("n_trials", len(L["trials"]))
# walk-forward：候选 = R5–R7 的 24 个已有试验；每年用前 5 年 exs20 均值最高者
T = {os.path.basename(f)[4:-4]: pd.read_pickle(f) for f in glob.glob(os.path.join(CACHE, "tr2_*.pkl"))}
T = {k: v for k, v in T.items() if len(v) > 100}
out = []
for y in range(2010, 2020):
    tr = {k: v[(v.date.dt.year >= y - 5) & (v.date.dt.year < y)].exs20.mean() for k, v in T.items()}
    best = max(tr, key=tr.get); te = T[best][T[best].date.dt.year == y]
    out.append((y, best, len(te), te.exs20.mean()))
wf = pd.DataFrame(out, columns=["year", "pick", "n", "exs20"]); print(wf.to_string())
allte = pd.concat([T[r.pick][T[r.pick].date.dt.year == r.year] for r in wf.itertuples()])
print("WF 汇总 n", len(allte), "exs20", allte.exs20.mean(), "正年份", (wf.exs20 > 0).sum(), "/10")
