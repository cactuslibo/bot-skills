"""纳指四季 V22.3 —— 单一 1 倍 ETF + 现金通用版
用法: from siji_1x import run; m = run("/workspace/data/etf/XLK.csv")
CSV: date,open,high,low,close,volume（复权日线）。信号用该 ETF 自身计算，收盘成交，现金收益 0。
"""
import pandas as pd, numpy as np

DEFAULT_WEIGHTS = {  # 状态 -> ETF 目标仓位
    "NORMAL": 1.0, "ZONE_BATTLE_ATTACK": 1.0, "ZONE_DESPAIR_TQQQ": 1.0,
    "ZONE_BATTLE_DEFEND": 0.5, "TOP_ESCAPE": 0.5, "HI": 0.5,
    "BEAR_CASH": 0.0, "HI_CASH": 0.0,
}
RISK_OFF = ("BEAR_CASH", "ZONE_BATTLE_DEFEND", "TOP_ESCAPE")
RISK_ON = ("ZONE_BATTLE_ATTACK", "NORMAL")

def load(path):
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df[~df.index.duplicated()].dropna(subset=["close"])
    return df

def indicators(df, hi_mode="fixed", hi_dev=0.20, ref_vol=0.25, vol_lookback=756, hi_clip=(0.08, 0.40)):
    d = df.copy()
    d["ma200"] = d.close.rolling(200).mean()
    d["ma20"] = d.close.rolling(20).mean()
    d["pma20"] = d.ma20.shift(1)
    d["vma60"] = d.volume.shift(1).rolling(60).mean()
    if hi_mode == "fixed":
        d["hi_thr"] = hi_dev
    elif hi_mode == "vol":
        # 乖离阈值按 ETF 自身已实现波动率缩放（只用过去数据，无前视）：
        # thr = hi_dev * (过去 vol_lookback 日年化波动 / ref_vol)，ref_vol≈QQQ 长期波动 25%
        r = np.log(d.close).diff()
        vol = r.rolling(vol_lookback, min_periods=252).std() * np.sqrt(252)
        d["hi_thr"] = (hi_dev * vol / ref_vol).clip(*hi_clip)
    else:
        raise ValueError(hi_mode)
    return d

def backtest(df, weights=None, start=None, end=None, cost=0.0, cap=1e5, min_tr=500.0,
             min_risk_off_days=2, vol_factor=2.2, high_zone=0.95, **ind_kw):
    W = dict(DEFAULT_WEIGHTS, **(weights or {}))
    d = indicators(df, **ind_kw)
    first_ok = d.index[252] if len(d) > 300 else None
    if first_ok is None: raise ValueError("数据不足 300 根")
    s = max(pd.Timestamp(start), first_ok) if start else first_ok
    idx = d.index[d.index >= s]
    if end: idx = idx[idx <= pd.Timestamp(end)]
    ath = d.high[d.index < idx[0]].iloc[-252:].max()   # 过去 252 根 high 初始化
    st, pend, rod = "INIT", None, 0
    cash, sh, ntr = cap, 0, 0
    eq, states = [], []
    def buy(tw, px):
        nonlocal cash, sh, ntr
        E = cash + sh * px; need = E * tw - sh * px
        if need > min_tr:
            n = min(int(need / px), int(cash / (px * (1 + cost))))
            if n > 0: cash -= n * px * (1 + cost); sh += n; ntr += 1
    for dt in idx:
        r = d.loc[dt]; p = r.close
        rod = rod + 1 if st in RISK_OFF else 0
        if pend is not None:                    # T+1：昨天卖出，今天买入，当日不判信号
            buy(pend, p); pend = None
        else:
            if p > ath: ath = p
            dd = p / ath - 1
            ma200, ma20, pm = r.ma200, r.ma20, r.pma20
            vol_ok = r.volume > 0 and pd.notna(r.vma60) and r.vma60 > 0
            top = vol_ok and p >= ath * high_zone and r.volume > r.vma60 * vol_factor and p < r.open
            a200, a20, b20 = p > ma200, p > ma20, p < ma20
            up, dn = ma20 > pm, ma20 < pm
            nxt, h = st, False
            if st == "HI" and a200:
                h = True; nxt = "HI_CASH" if (b20 and dn) else "HI"
            elif st == "HI_CASH" and a200:
                h = True; nxt = "NORMAL" if a20 else "HI_CASH"
            if not h:
                if p > ma200 * (1 + r.hi_thr): nxt = "HI"
                elif top: nxt = "TOP_ESCAPE"
                elif p < ma200:
                    if dd <= -0.30: nxt = "ZONE_DESPAIR_TQQQ" if up else "ZONE_BATTLE_DEFEND"
                    elif dd <= -0.10: nxt = "ZONE_BATTLE_ATTACK" if p > ma20 else "ZONE_BATTLE_DEFEND"
                    else: nxt = "BEAR_CASH"
                else:
                    nxt = "ZONE_BATTLE_ATTACK" if dd < -0.10 else "NORMAL"
            if st in RISK_OFF and nxt in RISK_ON and (rod < min_risk_off_days or not ma20 > pm):
                nxt = st                                  # 冷静期 + MA20 斜率过滤
            if nxt != st:
                st = nxt; tw = W[st]; E = cash + sh * p
                if E * tw - sh * p < -min_tr and sh > 0:
                    n = sh if tw == 0 else min(sh, int((sh * p - E * tw) / p))
                    if n > 0:
                        cash += n * p * (1 - cost); sh -= n; ntr += 1; pend = tw
                if pend is None: buy(tw, p)
        eq.append(cash + sh * p); states.append(st)
    eq = pd.Series(eq, idx); states = pd.Series(states, idx)
    return eq, states, ntr, dict(state=st, pending=pend, shares=sh, cash=cash, ath=ath)

def metrics(s):
    r = s.pct_change().dropna(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    return {"total": s.iloc[-1] / s.iloc[0] - 1, "cagr": (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1,
            "mdd": (s / s.cummax() - 1).min(), "sharpe": r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan,
            "vol": r.std() * np.sqrt(252)}

def run(ticker_csv, **kw):
    """返回 dict：策略与买入持有指标、交易数、状态占比、最终状态等"""
    df = load(ticker_csv)
    eq, states, ntr, last = backtest(df, **kw)
    bh = df.close.reindex(eq.index); bh = bh / bh.iloc[0] * eq.iloc[0]
    m = {"ticker": ticker_csv.split("/")[-1].rsplit(".", 1)[0], "start": eq.index[0].date(), "end": eq.index[-1].date()}
    m.update({f"strat_{k}": v for k, v in metrics(eq).items()})
    m.update({f"bh_{k}": v for k, v in metrics(bh).items()})
    m["trades"] = ntr; m["exposure"] = None
    m["state_pct"] = states.value_counts(normalize=True).round(4).to_dict()
    m["last"] = last; m["_eq"] = eq; m["_bh"] = bh; m["_states"] = states
    return m

if __name__ == "__main__":
    import sys
    f = sys.argv[1] if len(sys.argv) > 1 else "/workspace/data/QQQ_daily.csv"
    for label, kw in [("固定20%", {}), ("波动缩放", {"hi_mode": "vol"}), ("固定20%+0.05%成本", {"cost": 0.0005}),
                      ("固定20% 2010起", {"start": "2010-02-11"})]:
        m = run(f, **kw)
        print(f"{label:16s} {m['start']}~{m['end']} 策略 总{m['strat_total']:.0%} CAGR {m['strat_cagr']:.2%} MDD {m['strat_mdd']:.1%} "
              f"夏普 {m['strat_sharpe']:.2f} | 持有 总{m['bh_total']:.0%} CAGR {m['bh_cagr']:.2%} MDD {m['bh_mdd']:.1%} 夏普 {m['bh_sharpe']:.2f} | 交易 {m['trades']}")
        print("   状态占比", {k: f"{v:.1%}" for k, v in m["state_pct"].items()}, "| 末状态", m["last"]["state"])
