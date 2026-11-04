import pickle, numpy as np, pandas as pd, sys
sys.path.insert(0, "/workspace/wyckoff/bt"); from stats import pbo, dsr
OUT = "/workspace/wyckoff/full_bt"; HS = (5, 10, 20, 40, 60)
R = pickle.load(open(f"{OUT}/raw_results.pkl", "rb"))
U = pd.read_csv("/workspace/wyckoff/universe.csv").drop_duplicates("ticker").set_index("ticker")
sig = pd.DataFrame([r for _, res, _, _ in R for v, L in res.items() for r in L])
rnd = pd.DataFrame([r for _, _, c, _ in R for r in c])
# 同一标的 28 个交易日去重（按变体×臂，以信号日计；用日历 40 天≈28 交易日的近似改为精确：按标的交易日序号）
def dedupe(df):
    keep = []
    for _, g in df.sort_values("sig").groupby(["t", "var", "arm"]):
        last = None
        for i, d in zip(g.index, g.sig):
            if last is None or np.busday_count(last.date(), d.date()) >= 28: keep.append(i); last = d
    return df.loc[keep]
n0 = len(sig); sig = dedupe(sig); print("去重", n0, "->", len(sig))
for d in (sig, rnd):
    d["cap"] = d.t.map(U.market_cap); d["sector"] = d.t.map(U.sector); d["year"] = pd.to_datetime(d.date).dt.year
    d["capb"] = pd.cut(d.cap, [0, 1e10, 5e10, 1e16], labels=["1-10B", "10-50B", "50B+"])
def st(r, x):
    r, x = r.dropna(), x.dropna(); n = len(r)
    if n < 2: return dict(n=n)
    g, lo = r[r > 0].sum(), -r[r < 0].sum()
    return dict(n=n, win=(r > 0).mean(), mean=r.mean(), med=r.median(), ex=x.mean(), ex_med=x.median(),
                t_ex=x.mean() / x.std() * np.sqrt(len(x)), pf=g / lo if lo > 0 else np.nan)
def tclust(df, col):  # 按入场月聚类：月均值的 t
    m = df.dropna(subset=[col]).groupby(pd.to_datetime(df.date).dt.to_period("M"))[col].mean()
    return m.mean() / m.std() * np.sqrt(len(m))
rows = []
for (v, a), g in sig.groupby(["var", "arm"]):
    for H in HS:
        for ex, rc, xc in (("止损@Spring低点", f"rs{H}", f"xs{H}"), ("无止损", f"r{H}", f"x{H}")):
            d = st(g[rc], g[xc]); d.update(var=v, arm=a, H=H, exit=ex, t_ex_month=tclust(g, xc), kind="信号"); rows.append(d)
        gr = rnd[(rnd["var"] == v) & (rnd.arm == a)]
        d = st(gr[f"r{H}"], gr[f"x{H}"]); d.update(var=v, arm=a, H=H, exit="无止损", t_ex_month=tclust(gr, f"x{H}"), kind="随机对照(5x)"); rows.append(d)
T = pd.DataFrame(rows)[["kind", "var", "arm", "H", "exit", "n", "win", "mean", "med", "ex", "ex_med", "t_ex", "t_ex_month", "pf"]]
T.to_csv(f"{OUT}/核心结果_全组合.csv", index=False, float_format="%.4f")
# 分组（H=20，两种出场）
B = []
for (v, a), g in sig.groupby(["var", "arm"]):
    for dim in ("year", "capb", "sector"):
        for k, gg in g.groupby(dim, observed=True):
            for ex, rc, xc in (("止损", "rs20", "xs20"), ("无止损", "r20", "x20")):
                d = st(gg[rc], gg[xc]); d.update(var=v, arm=a, dim=dim, key=k, exit=ex); B.append(d)
B = pd.DataFrame(B)[["var", "arm", "dim", "key", "exit", "n", "win", "mean", "med", "ex", "t_ex", "pf"]]
B.to_csv(f"{OUT}/分组结果_H20.csv", index=False, float_format="%.4f")
# PBO / DSR：40 个试验的月度超额收益
M = {}
for (v, a), g in sig.groupby(["var", "arm"]):
    for H in HS:
        for xc in (f"xs{H}", f"x{H}"):
            M[f"{v}|{a}|{H}|{xc}"] = g.dropna(subset=[xc]).groupby(pd.to_datetime(g.date).dt.to_period("M"))[xc].mean()
M = pd.DataFrame(M).sort_index()
p = pbo(M, S=16); srs = M.mean() / M.std(); best = srs.idxmax()
d_, sr0 = dsr(srs[best], M[best].count(), M.shape[1], srs.var(), M[best].skew(), M[best].kurt() + 3)
open(f"{OUT}/pbo_dsr.txt", "w").write(f"trials={M.shape[1]} PBO={p:.3f} best={best} monthlySR={srs[best]:.3f} SR0={sr0:.3f} DSR={d_:.3f}\n")
print(open(f"{OUT}/pbo_dsr.txt").read())
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(T[T.H == 20].round(4).to_string())
print(T.sort_values("t_ex_month", ascending=False).head(8).round(4).to_string())
