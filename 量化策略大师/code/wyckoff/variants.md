# 威科夫筑底法：V1–V8 变体说明

所有变体都在 `wyckoff_v0.py` 末尾的 `VARIANTS` 字典里定义，本质上是 `Params` 的不同取值。表中没有列出的参数，一律沿用 `Params` 默认值。

## 默认参数（V1_base）
- 区间：`range_window=60`。支撑按 `support_mode="swing_median"` 计算，即摆动低点的中位数。振幅上限取 ATR%×4 和 30% 中较大的一个，且不超过 60%。漂移 ≤12%，触边 ≥3 次。
- Spring：跌破支撑 0～1.5 ATR（`pierce_max_atr=1.5`），并在 3 根 K 线内收回（`reclaim_bars=3`）。下破量不做限制（`pierce_vol_mode="none"`），收回量也不做限制（`reclaim_vol_ratio=0`）。
- Test：出现在 Spring 后 10 根 K 线内（`test_window=10`），量比 ≤0.9（`test_vol_ratio_max`），低点距支撑不超过区间宽度的 3%（`test_band=0.03`），收盘位于当日振幅的上半部（`test_close_q=0.5`）。
- 背景过滤：关闭（`downtrend_filter="off"`，`require_sc=False`）。

## V1–V8
| 版本 | VARIANTS 键 | 相对 V1 改动的参数 | 思路 |
|---|---|---|---|
| V1 | `V1_base` | 无 | 基准：区间 → Spring（跌破支撑后收回）→ 缩量 Test |
| V2 | `V2_pierce_dry` | `pierce_vol_mode="dry"`（下破那根 K 线的量 ≤ 均量×`pierce_vol_dry`，即 1.0） | 缩量下破：卖压已经枯竭 |
| V3 | `V3_pierce_clx` | `pierce_vol_mode="climax"`（下破那根 K 线的量 > 均量×`pierce_vol_climax`，即 1.5） | 放量下破：恐慌抛盘被接住，类似 shakeout |
| V4 | `V4_reclaim_vol` | `reclaim_vol_ratio=1.15`（收回量/下破量 ≥1.15） | 收回时有买盘进场 |
| V5 | `V5_minlow` | `support_mode="min_low"` | 支撑改用区间最低价，Spring 需要跌得更深 |
| V6 | `V6_tight` | `pierce_max_atr=1.0`、`reclaim_bars=1` | 收紧条件：下破更浅，次日就要收回 |
| V7 | `V7_downtrend` | `downtrend_filter="ret_neg"`（`downtrend_lookback=60` 日收益为负） | 只取下跌之后的筑底 |
| V8 | `V8_sc_chain` | `require_sc=True`（之前必须出现卖出高潮 SC：成交量 z 值 ≥2.5，且真实波幅 ≥2 ATR） | 要求完整的 SC → 区间 → Spring 链条 |

## 入场方式 E1 / E2
所有信号都在 T 日收盘确认，T+1 日开盘执行（`entry_* = raw_*.shift(1)`），以避免前视。
- **E1** `entry_spring_next_open`：Spring 确认后的次日开盘入场。
- **E2** `entry_after_test`：Test 确认后的次日开盘入场。信号比 E1 少，但多一步确认。
- 研究与对照：`entry_sos`、`entry_lps`、`entry_ctrl_touch`、`entry_ctrl_sos_only`、`entry_ctrl_lps_only`。

## 运行方法
```python
import wyckoff_v0 as W
out = W.run_wyckoff(df, W.VARIANTS["V3_pierce_clx"])   # df 是 OHLCV 日线数据
e1, e2 = out["entry_spring_next_open"], out["entry_after_test"]
```
- 快速试跑（使用 V1 默认参数，行情通过 yfinance 获取）：`python wyckoff_v0.py AAPL MSFT`
- 单元测试：`pytest test_wyckoff_v0.py`
- 迭代实验：`cd bt && python r1.py`（r1～r8 分别对应第 1～8 轮）。需要本地行情库 `tv_db`，本仓库不提供。
- 全样本回测：先运行 `full_bt/run_full.py` 生成信号和交易，再依次运行 `analyze.py`（统计）、`current_list.py`（当前清单）、`make_report.py`（报告）。默认只跑 `V1_base` 和 `V3_pierce_clx`。如果要换其他变体，就修改 `run_full.py` 里的 `VARS` 字典，例如加入 `"V6_tight": W.VARIANTS["V6_tight"]`。脚本里的数据路径是写死的 `/workspace/wyckoff/...`，请按自己的环境修改。行情数据和 `universe.csv` 均不提供。报告收件人从环境变量 `WYCKOFF_MAIL_TO` 读取。

## 已有回测结论（摘自 evolution-log.md 和 full_bt/结论.md）
- **R1 预注册主试验（V1–V8 × E1/E2）**：加了 Spring 低点止损后，16 个组合的 20 日超额（exs20）全部为负，在 -0.43%～-1.17% 之间；月度 t 在 -1.6～-4.9 之间，DSR≈0。不止损时，ex20 在 -0.33%～+0.08% 之间，和随机对照（-0.01%）没有差别。表现最好的是 V3|E2（ex20 +0.08%，n=2163）。
- **出场**：止损越宽、越依赖确认，效果越好；不止损、按波动率缩放仓位的效果最好。扣除成本后，任何止损都会让超额再下降 0.2–2.5 个百分点。
- **过滤**：最好的研究候选是 V3 + E2 + 收盘价>MA200 + 不止损、按波动率缩放仓位。未扣成本时，20/40/60 日超额分别为 +0.18%/+0.36%/+0.15%，月度 t=0.72；扣除 20bp 成本后，exs20 为 -0.05%，t=-0.17。完整的 LPS 确认链全部为负。
- **结论**：没有任何候选同时满足 t>3 且 DSR≥0.95，所以没有生成 v1。
- **全样本回测（市值>10 亿美元的美股，2005-01-01～2026-11-03）**：40 个组合（V1/V3 × E1/E2 × 5 个持有期 × 2 种出场）中，相对 SPY 的平均超额没有一个为正。表现最好的是 V1_base E2、持有 60 日、不止损：胜率 57.46%，平均超额 -0.16%，按月聚类 t=0.45。不止损时胜率在 50–58% 左右，和随机日期入场几乎一样；止损设在 Spring 低点时，胜率降到 17–44%，超额也更差。PBO=0.143，DSR=0.000。
- 局限：存在幸存者偏差，且没有保留样本外数据。详见原文。
