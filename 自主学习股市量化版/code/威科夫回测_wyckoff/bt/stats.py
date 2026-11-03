import numpy as np, pandas as pd
from scipy.stats import norm
from itertools import combinations
def dsr(sr, n_obs, n_trials, sr_var, skew=0, kurt=3):
    """Bailey & López de Prado 2014。sr 为逐期（月）SR；sr_var 为各试验 SR 的方差。"""
    if n_trials <= 1: sr0 = 0
    else:
        e = 0.5772156649
        sr0 = np.sqrt(sr_var) * ((1 - e) * norm.ppf(1 - 1 / n_trials) + e * norm.ppf(1 - 1 / (n_trials * np.e)))
    z = (sr - sr0) * np.sqrt(n_obs - 1) / np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    return norm.cdf(z), sr0
def pbo(M, S=16):
    """CSCV：M 为 (期数 × 试验) 的月度收益矩阵。"""
    M = M.dropna(how="all").fillna(0).to_numpy(); T = len(M) // S * S; M = M[:T]
    blocks = np.array_split(np.arange(T), S); logits = []
    for c in combinations(range(S), S // 2):
        tr = np.concatenate([blocks[i] for i in c]); te = np.setdiff1d(np.arange(T), tr)
        def sr(x): return x.mean(0) / (x.std(0) + 1e-12)
        best = np.argmax(sr(M[tr])); r = sr(M[te]).argsort().argsort()[best] + 1
        w = r / (M.shape[1] + 1); logits.append(np.log(w / (1 - w)))
    return float((np.array(logits) <= 0).mean())
