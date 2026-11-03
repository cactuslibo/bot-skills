#!/usr/bin/env python3
"""Bass / Logistic 扩散拟合（离线，无网络、无文件写入，除非 --out）。

用法:
  python3 bass_fit.py data.csv --model bass --horizon 10
  python3 bass_fit.py data.csv --model bass --m 5000000      # 固定 m，只拟合 p,q
  python3 bass_fit.py data.csv --model logistic --K 0.6       # 拟合渗透率，固定上限
CSV 两列: year,value
  bass: value = 当期新增采用量（销量）
  logistic: value = 渗透率(0-1) 或累计量
依赖: numpy, scipy
"""
import argparse, csv, math, sys
import numpy as np
from scipy.optimize import curve_fit

def bass_F(t, p, q):
    e = np.exp(-(p + q) * t)
    return (1 - e) / (1 + (q / p) * e)

def bass_new(t, m, p, q):
    return m * (bass_F(t, p, q) - bass_F(t - 1, p, q))

def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

def r2(y, yh):
    ss = np.sum((y - yh) ** 2); st = np.sum((y - y.mean()) ** 2)
    return 1 - ss / st if st > 0 else float("nan")

def main():
    a = argparse.ArgumentParser()
    a.add_argument("csv"); a.add_argument("--model", choices=["bass", "logistic"], default="bass")
    a.add_argument("--horizon", type=int, default=10)
    a.add_argument("--m", type=float); a.add_argument("--K", type=float)
    x = a.parse_args()
    rows = [r for r in csv.reader(open(x.csv)) if r and r[0].strip().lstrip("-").isdigit()]
    yrs = np.array([int(r[0]) for r in rows]); y = np.array([float(r[1]) for r in rows])
    if len(y) < 4:
        print("警告：少于 4 个观测点，参数不稳定，应以类比先验为主", file=sys.stderr)
    t = (yrs - yrs[0] + 1).astype(float); fut = np.arange(1, len(t) + x.horizon + 1, dtype=float)
    if x.model == "bass":
        if x.m:
            f = lambda tt, p, q: bass_new(tt, x.m, p, q)
            (p, q), _ = curve_fit(f, t, y, p0=[0.03, 0.38], bounds=([1e-5, 1e-4], [1, 3]), maxfev=20000)
            m = x.m
        else:
            (m, p, q), _ = curve_fit(bass_new, t, y, p0=[y.sum() * 3, 0.03, 0.38],
                                     bounds=([y.sum(), 1e-5, 1e-4], [y.sum() * 1e3, 1, 3]), maxfev=20000)
        yh = bass_new(t, m, p, q)
        tstar = math.log(q / p) / (p + q)
        print(f"m={m:.4g} p={p:.4g} q={q:.4g} q/p={q/p:.2f} R2={r2(y, yh):.3f}")
        print(f"峰值时间 t*={tstar:.2f} 期（约 {yrs[0] - 1 + tstar:.1f} 年），峰值新增={m*(p+q)**2/(4*q):.4g}")
        print("year,new,cumulative")
        for tt in fut:
            print(f"{int(yrs[0] - 1 + tt)},{bass_new(tt, m, p, q):.4g},{m * bass_F(tt, p, q):.4g}")
    else:
        if x.K:
            f = lambda tt, r, t0: logistic(tt, x.K, r, t0)
            (r, t0), _ = curve_fit(f, t, y, p0=[0.5, len(t)], maxfev=20000); K = x.K
        else:
            (K, r, t0), _ = curve_fit(logistic, t, y, p0=[y.max() * 2, 0.5, len(t)],
                                      bounds=([y.max(), 1e-3, -50], [y.max() * 100, 5, 200]), maxfev=20000)
        yh = logistic(t, K, r, t0)
        print(f"K={K:.4g} r={r:.4g} 拐点年={yrs[0] - 1 + t0:.1f} 10%→90%用时={4.39/r:.1f}年 R2={r2(y, yh):.3f}")
        print("year,value")
        for tt in fut:
            print(f"{int(yrs[0] - 1 + tt)},{logistic(tt, K, r, t0):.4g}")

if __name__ == "__main__":
    main()
