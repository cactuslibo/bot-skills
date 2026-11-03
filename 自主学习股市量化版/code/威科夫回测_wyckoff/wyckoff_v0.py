"""wyckoff_v0.py —— 威科夫筑底（Spring 主线）可量化状态机 v0。

依据 /workspace/wyckoff/wyckoff-spec-v0.md。只借鉴各仓库的方法，代码独立编写。
原则：T 日的一切判断只用 ≤T 的数据；摆动点在确认日（右侧 s 根走完）才可用；
对外入场信号 entry_* = raw_*.shift(1)，即 T 日收盘出信号，T+1 开盘执行。

用法：
    from wyckoff_v0 import run_wyckoff, DEFAULT_PARAMS
    out = run_wyckoff(df)            # df: 列 open/high/low/close/volume，日期索引升序
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field, asdict, replace

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Params:
    # 区间（支撑/阻力）
    range_window: int = 60
    swing_window: int = 3
    support_k: int = 5
    support_mode: str = "swing_median"   # swing_median | min_low | min_close
    range_max_pct: float = 0.30          # 固定振幅下限口径
    range_atr_mult: float = 4.0          # 自适应：ATR% × m
    range_cap_pct: float = 0.60          # 振幅绝对上限
    range_drift_max: float = 0.12
    range_min_touches: int = 3           # 触边次数（下沿+上沿已确认摆动点）
    touch_band_atr: float = 0.5
    atr_window: int = 14
    # Spring
    pierce_min_atr: float = 0.0
    pierce_max_atr: float = 1.5
    reclaim_bars: int = 3
    reclaim_min_pct: float = 0.0
    pierce_vol_mode: str = "none"        # none | dry | climax
    pierce_vol_dry: float = 1.0
    pierce_vol_climax: float = 1.5
    reclaim_vol_ratio: float = 0.0       # 0=关闭；>0 要求 收回量/下破量 ≥ 该值
    vol_ma_window: int = 20
    # Test
    test_window: int = 10
    test_vol_ratio_max: float = 0.9
    test_band: float = 0.03              # ×区间宽度，Test 低点距支撑带宽
    test_close_q: float = 0.5
    # 背景过滤
    downtrend_filter: str = "off"        # off | ret_neg | below_ma200
    downtrend_lookback: int = 60
    require_sc: bool = False
    sc_vol_z: float = 2.5
    sc_tr_atr: float = 2.0
    vol_z_window: int = 50
    # 研究对照（SOS/LPS）
    sos_break_pct: float = 0.02
    sos_vol_z: float = 1.5
    lps_window: int = 15
    lps_vol_ratio_max: float = 0.95
    tested_max_bars: int = 60            # TESTED 状态最长保留根数（原硬编码 60）
    lps_hi_tol: float = 0.02             # LPS 低点 ≤ R×(1+该值)（原硬编码 1.02）
    test_atr_band: float = 0.25          # Test 带宽 ATR 项（原硬编码 0.25）
    # 去重
    cooldown: int = 28


DEFAULT_PARAMS = Params()

REQUIRED = ["open", "high", "low", "close", "volume"]


def _atr(df: pd.DataFrame, n: int) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()  # Wilder，只用 ≤t


def _confirmed_swings(x: np.ndarray, s: int, kind: str):
    """返回 (swing 所在 bar 下标数组, 确认日下标数组)。bar i 为摆动点当且仅当它是
    [i-s, i+s] 的严格极值；只有在 i+s 日收盘后才知道，所以确认日 = i+s。"""
    n = len(x)
    idx = []
    for i in range(s, n - s):
        w = x[i - s:i + s + 1]
        v = x[i]
        if np.isnan(v):
            continue
        left = x[i - s:i]
        # 并列时取最左一根：严格优于左侧、不劣于右侧
        if kind == "low" and v == np.nanmin(w) and (left > v).all():
            idx.append(i)
        if kind == "high" and v == np.nanmax(w) and (left < v).all():
            idx.append(i)
    idx = np.array(idx, dtype=int)
    return idx, idx + s


def run_wyckoff(df: pd.DataFrame, params: Params = DEFAULT_PARAMS) -> pd.DataFrame:
    p = params
    d = df.copy()
    d.columns = [c.lower() for c in d.columns]
    miss = [c for c in REQUIRED if c not in d.columns]
    if miss:
        raise ValueError(f"缺少列: {miss}")
    d = d[REQUIRED].astype(float).sort_index()
    n = len(d)
    o, h, l, c, v = (d[k].to_numpy() for k in REQUIRED)

    atr = _atr(d, p.atr_window).to_numpy()
    vol_ma = d["volume"].rolling(p.vol_ma_window).mean().shift(1).to_numpy()   # 分母不含当日
    vmu = d["volume"].rolling(p.vol_z_window).mean().shift(1)
    vsd = d["volume"].rolling(p.vol_z_window).std().shift(1)
    vol_z = ((d["volume"] - vmu) / vsd).to_numpy()
    rng = np.where(h - l > 0, h - l, np.nan)
    close_q = np.nan_to_num((c - l) / rng, nan=0.5)
    ma200 = d["close"].rolling(200).mean().to_numpy()
    tr = np.maximum.reduce([h - l, np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))]); tr[0] = h[0] - l[0]
    # SC 特征（当日即可判断，无未来）
    roll_min20 = d["low"].rolling(20).min().to_numpy()
    sc_flag = (vol_z >= p.sc_vol_z) & (tr >= p.sc_tr_atr * np.nan_to_num(atr, nan=np.inf)) & (close_q <= 0.4) & (l <= roll_min20)

    sl_idx, sl_conf = _confirmed_swings(l, p.swing_window, "low")
    sh_idx, sh_conf = _confirmed_swings(h, p.swing_window, "high")

    sl_conf_l = sl_conf.tolist() if len(sl_conf) else []
    sh_conf_l = sh_conf.tolist() if len(sh_conf) else []

    def zone(t: int):
        """以 t-1 为窗口末端（信号窗口=当日，与区间窗口不重叠）。返回 (S, R, ok, width) 或 None。"""
        end = t - 1
        start = end - p.range_window + 1
        if start < 0 or np.isnan(atr[end]):
            return None
        # 只取 bar 在窗口内、且确认日 ≤ end 的摆动点
        def pick(idx, conf_l, arr):
            k = bisect.bisect_right(conf_l, end) if conf_l else 0
            j = bisect.bisect_left(idx[:k], start) if k else 0   # idx 升序
            cand = list(idx[j:k])
            return cand, [arr[i] for i in cand]
        lo_i, lo_v = pick(sl_idx, sl_conf_l, l)
        hi_i, hi_v = pick(sh_idx, sh_conf_l, h)
        seg_l, seg_h, seg_c = l[start:end + 1], h[start:end + 1], c[start:end + 1]
        if p.support_mode == "swing_median" and len(lo_v) >= 2:
            S = float(np.median(lo_v[-p.support_k:]))
        elif p.support_mode == "min_low":
            S = float(np.min(seg_l))
        else:
            S = float(np.min(seg_c))
        R = float(np.median(hi_v[-p.support_k:])) if len(hi_v) >= 2 else float(np.max(seg_c))
        if R <= S or S <= 0:
            return None
        amp = (np.max(seg_h) - np.min(seg_l)) / np.min(seg_l)
        atr_pct = atr[end] / c[end]
        lim = min(max(p.range_max_pct, p.range_atr_mult * atr_pct), p.range_cap_pct)
        drift = abs(seg_c[-1] / seg_c[0] - 1)
        band = p.touch_band_atr * atr[end]
        touches = sum(abs(x - S) <= band for x in lo_v) + sum(abs(x - R) <= band for x in hi_v)
        ok = amp <= lim and drift <= p.range_drift_max and touches >= p.range_min_touches
        if ok and p.downtrend_filter == "ret_neg":
            j = start - p.downtrend_lookback
            ok = j >= 0 and c[start] < c[j]
        elif ok and p.downtrend_filter == "below_ma200":
            ok = not np.isnan(ma200[end]) and c[end] <= ma200[end] * 1.02
        if ok and p.require_sc:
            ok = bool(sc_flag[start:end + 1].any())
        return S, R, ok, R - S

    cols = {k: np.zeros(n, dtype=bool) for k in ["raw_spring", "raw_test", "raw_sos", "raw_lps",
                                                  "raw_range_touch", "raw_sos_only", "raw_lps_only"]}
    state = np.array(["IDLE"] * n, dtype=object)
    support = np.full(n, np.nan); resist = np.full(n, np.nan); range_ok = np.zeros(n, dtype=bool)
    spring_low_col = np.full(n, np.nan)

    st = "IDLE"; ctx: dict = {}
    last_evt = {k: -10**9 for k in ["spring", "test", "touch", "sos_only", "lps_only"]}
    sos_only_ctx = None

    for t in range(n):
        z = zone(t)
        if z is not None:
            support[t], resist[t], range_ok[t], _ = z
        a = atr[t - 1] if t >= 1 and not np.isnan(atr[t - 1]) else np.nan   # 与 zone 同口径（不含当日 TR）

        # ---- 对照：单纯区间下沿触碰（不下破）、单独 SOS、单独 LPS ----
        if z is not None and z[2] and not np.isnan(a):
            S, R, _, W = z
            if S <= l[t] <= S + p.touch_band_atr * a and c[t] > S and t - last_evt["touch"] >= p.cooldown:
                cols["raw_range_touch"][t] = True; last_evt["touch"] = t
            if c[t] > R * (1 + p.sos_break_pct) and vol_z[t] >= p.sos_vol_z and t - last_evt["sos_only"] >= p.cooldown:
                cols["raw_sos_only"][t] = True; last_evt["sos_only"] = t
                sos_only_ctx = {"t": t, "R": R, "S": S}
        if sos_only_ctx and t > sos_only_ctx["t"]:
            if t - sos_only_ctx["t"] > p.lps_window or c[t] < (sos_only_ctx["S"] + sos_only_ctx["R"]) / 2:
                sos_only_ctx = None
            elif (l[t] <= sos_only_ctx["R"] * (1 + p.lps_hi_tol) and l[t] >= (sos_only_ctx["S"] + sos_only_ctx["R"]) / 2
                  and v[t] <= p.lps_vol_ratio_max * vol_ma[t] and c[t] >= o[t]):
                if t - last_evt["lps_only"] >= p.cooldown:
                    cols["raw_lps_only"][t] = True; last_evt["lps_only"] = t
                sos_only_ctx = None

        # ---- 主状态机：先处理已有结构的推进/失效，再看新下破，再看收回 ----
        if st == "SPRING" and t > ctx["ts"]:
            if l[t] < ctx["low"]:
                st = "IDLE"                                   # 打穿 Spring 极值，失效
            elif t - ctx["ts"] > p.test_window:
                st = "IDLE"
            elif (l[t] <= ctx["S"] + p.test_band * ctx["W"] + (0 if np.isnan(a) else p.test_atr_band * a)
                  and v[t] <= p.test_vol_ratio_max * vol_ma[t] and v[t] < ctx["pv"]
                  and close_q[t] >= p.test_close_q):
                cols["raw_test"][t] = True; ctx["tt"] = t; st = "TESTED"
        elif st == "TESTED" and t > ctx["tt"]:
            if l[t] < ctx["low"] or t - ctx["tt"] > p.tested_max_bars:
                st = "IDLE"
            elif c[t] > ctx["R"] * (1 + p.sos_break_pct) and vol_z[t] >= p.sos_vol_z:
                cols["raw_sos"][t] = True; ctx["tsos"] = t; st = "SOS"
        elif st == "SOS" and t > ctx["tsos"]:
            mid = (ctx["S"] + ctx["R"]) / 2
            if c[t] < mid or t - ctx["tsos"] > p.lps_window:
                st = "IDLE"
            elif l[t] >= mid and l[t] <= ctx["R"] * (1 + p.lps_hi_tol) and v[t] <= p.lps_vol_ratio_max * vol_ma[t]:
                cols["raw_lps"][t] = True; st = "IDLE"
        if st == "IDLE":
            if (z is not None and z[2] and not np.isnan(a) and l[t] < z[0] - p.pierce_min_atr * a
                    and t - last_evt["spring"] >= p.cooldown):
                S, R, _, W = z
                depth = (S - l[t]) / a
                vr = v[t] / vol_ma[t] if vol_ma[t] > 0 else np.nan
                vol_ok = (p.pierce_vol_mode == "none" or
                          (p.pierce_vol_mode == "dry" and vr < p.pierce_vol_dry) or
                          (p.pierce_vol_mode == "climax" and vr > p.pierce_vol_climax))
                if depth <= p.pierce_max_atr and vol_ok:
                    ctx = {"S": S, "R": R, "W": W, "tp": t, "low": l[t], "pv": v[t]}
                    st = "PIERCE"
        if st == "PIERCE" and t >= ctx["tp"]:
            if t > ctx["tp"]:
                ctx["low"] = min(ctx["low"], l[t])
            if not np.isnan(a) and (ctx["S"] - ctx["low"]) / a > p.pierce_max_atr:
                st = "IDLE"                                   # 真破位
            elif c[t] > ctx["S"] * (1 + p.reclaim_min_pct) and (p.reclaim_vol_ratio <= 0 or v[t] >= p.reclaim_vol_ratio * ctx["pv"]):
                cols["raw_spring"][t] = True; last_evt["spring"] = t
                ctx["ts"] = t; st = "SPRING"
            elif t - ctx["tp"] + 1 >= p.reclaim_bars:
                st = "IDLE"
        state[t] = st
        if st in ("SPRING", "TESTED", "SOS"):
            spring_low_col[t] = ctx["low"]

    out = pd.DataFrame(index=d.index)
    out["state"] = state
    out["support"] = support; out["resistance"] = resist; out["range_ok"] = range_ok
    out["spring_low"] = spring_low_col
    for k, arr in cols.items():
        out[k] = arr
    # 对外入场信号：shift(1)
    out["entry_spring_next_open"] = out["raw_spring"].shift(1, fill_value=False)   # E1
    out["entry_after_test"] = out["raw_test"].shift(1, fill_value=False)           # E2
    out["entry_sos"] = out["raw_sos"].shift(1, fill_value=False)                   # 研究
    out["entry_lps"] = out["raw_lps"].shift(1, fill_value=False)                   # 研究
    out["entry_ctrl_touch"] = out["raw_range_touch"].shift(1, fill_value=False)    # 对照
    out["entry_ctrl_sos_only"] = out["raw_sos_only"].shift(1, fill_value=False)
    out["entry_ctrl_lps_only"] = out["raw_lps_only"].shift(1, fill_value=False)
    out["stop_level"] = out["spring_low"].shift(1)
    return out


VARIANTS = {
    "V1_base":        Params(),
    "V2_pierce_dry":  Params(pierce_vol_mode="dry"),
    "V3_pierce_clx":  Params(pierce_vol_mode="climax"),
    "V4_reclaim_vol": Params(reclaim_vol_ratio=1.15),
    "V5_minlow":      Params(support_mode="min_low"),
    "V6_tight":       Params(pierce_max_atr=1.0, reclaim_bars=1),
    "V7_downtrend":   Params(downtrend_filter="ret_neg"),
    "V8_sc_chain":    Params(require_sc=True),
}


if __name__ == "__main__":
    import sys
    import yfinance as yf
    tickers = sys.argv[1:] or ["AAPL", "UPWK", "XLK", "MSFT", "IWM"]
    for tk in tickers:
        raw = yf.download(tk, start="2010-01-01", auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        out = run_wyckoff(raw)
        ent = [c for c in out.columns if c.startswith("entry_")]
        print(f"{tk}: bars={len(out)} range_ok日数={int(out.range_ok.sum())} "
              + " ".join(f"{c[6:]}={int(out[c].sum())}" for c in ent))
        print("   state 分布:", out.state.value_counts().to_dict())
