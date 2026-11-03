import numpy as np, pandas as pd, pytest
from wyckoff_v0 import run_wyckoff, Params, VARIANTS, _confirmed_swings

def rand_df(n=400, seed=0):
    r = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(r.normal(0, 0.015, n)))
    o = c * (1 + r.normal(0, 0.004, n))
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.008, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.008, n)))
    v = r.lognormal(13, 0.4, n)
    return pd.DataFrame(dict(open=o, high=h, low=l, close=c, volume=v), index=pd.bdate_range("2020-01-01", periods=n))

def spring_df():
    """下跌→震荡区间(95~105)→下破至~93后收回→缩量测试。"""
    r = np.random.default_rng(1)
    down = np.linspace(140, 100, 60)
    rng = 100 + 4.5 * np.sin(np.arange(90) / 5.0)
    c = np.concatenate([down, rng, [97, 96, 99.5, 98.5, 98.2, 99, 100, 101, 102, 103] , np.linspace(103, 110, 20)])
    n = len(c)
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * 1.006; l = np.minimum(o, c) * 0.994
    v = np.full(n, 1e6) * r.uniform(0.9, 1.1, n)
    k = 150  # 第一根新段
    l[k + 1] = 93.0; v[k + 1] = 1.6e6           # 下破根
    c[k + 2] = 99.5; v[k + 2] = 1.9e6           # 收回根
    l[k + 4] = 95.3; v[k + 4] = 0.6e6; c[k + 4] = 96.6; h[k+4] = 96.8; o[k+4] = 95.8   # 缩量测试
    return pd.DataFrame(dict(open=o, high=h, low=l, close=c, volume=v), index=pd.bdate_range("2021-01-01", periods=n))

@pytest.mark.parametrize("name", list(VARIANTS))
@pytest.mark.parametrize("seed", [0, 3])
def test_no_lookahead_truncation(name, seed):
    """核心防未来检验：只用 [0..t] 数据算出的第 t 行，必须与全样本结果的第 t 行一致。"""
    df = rand_df(320, seed)
    full = run_wyckoff(df, VARIANTS[name])
    for t in [120, 180, 239, 300, 319]:
        part = run_wyckoff(df.iloc[: t + 1], VARIANTS[name])
        pd.testing.assert_frame_equal(part, full.iloc[: t + 1], check_freq=False)

def test_future_perturbation_invariance():
    """改写 t 之后的数据，t 及以前的输出不变。"""
    df = rand_df(300, 7); t = 200
    df2 = df.copy(); df2.iloc[t + 1:] *= 0.5; df2.iloc[t + 1:, 4] *= 9
    a, b = run_wyckoff(df), run_wyckoff(df2)
    pd.testing.assert_frame_equal(a.iloc[: t + 1], b.iloc[: t + 1], check_freq=False)

def test_entry_is_shifted():
    out = run_wyckoff(rand_df(400, 5))
    for raw, ent in [("raw_spring", "entry_spring_next_open"), ("raw_test", "entry_after_test"), ("raw_sos", "entry_sos")]:
        assert (out[ent].to_numpy()[1:] == out[raw].to_numpy()[:-1]).all()
        assert not out[ent].iloc[0]

def test_swing_confirmation_lag():
    x = np.array([5, 4, 3, 1, 3, 4, 5, 6.0])
    idx, conf = _confirmed_swings(x, 3, "low")
    assert list(idx) == [3] and list(conf) == [6]

def test_synthetic_spring_detected():
    df = spring_df()
    out = run_wyckoff(df, Params(range_min_touches=2, range_drift_max=0.2, pierce_min_atr=0.3, cooldown=0))
    k = 150
    # 下破根 k+1 当日收盘已收回支撑之上 → Spring 记在 k+1，次日 k+2 才出入场信号
    assert out["raw_spring"].iloc[k + 1]
    assert not out["entry_spring_next_open"].iloc[k + 1]
    assert out["entry_spring_next_open"].iloc[k + 2]
    assert out["raw_test"].iloc[k + 4]
    assert out["entry_after_test"].iloc[k + 5]

def test_deep_breakdown_rejected():
    df = spring_df(); k = 150
    df.iloc[k + 1, df.columns.get_loc("low")] = 80.0   # 远超 1.5ATR
    out = run_wyckoff(df, Params(range_min_touches=2, range_drift_max=0.2, pierce_min_atr=0.3, cooldown=0))
    assert not out["raw_spring"].iloc[k: k + 5].any()
