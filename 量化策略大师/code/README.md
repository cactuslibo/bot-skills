# 量化策略大师 · 回测代码

都是本 bot 自己写的 Python 回测脚本。**数据不随仓库提供**，需要自己准备（可以向 TradingView bot 要行情），再把脚本里的数据路径改成你本地的路径（脚本里默认写的是 `/workspace/...`）。

## 依赖
Python 3.9+，`pandas`、`numpy`、`scipy`；`ndx_escape/dl.py` 另外需要 `yfinance`。用到了标准库 `multiprocessing`。

## 目录
### ndx_escape/ — 纳指逃顶 v1/v2
- `dl.py`：下载 QQQ/NDX/VIX/VXN/HYG/LQD/^IRX 等日线，保存为 CSV（这些 CSV 不在仓库里）。
- `bt.py`：逃顶 v1 回测（信号 shift(1)，T+1 执行，含成本和 T-bill 收益）。
- `v2.py`：逃顶 v2 回测（v1 的改进版本）。
- 运行：`python dl.py && python bt.py && python v2.py`

### strategy_compare/ — 多策略横向比较
- `framework.py`：统一回测框架（shift(1) 次日执行，单边 5bp，空仓拿 T-bill）。v1/v2 参数冻结自 ndx_escape。
- `strategies_daily.py`：各日线策略的信号定义。
- `matrix.py`：在 QQQ 和一组 ETF 上跑策略矩阵（需要 `etf19_data/tickers.txt` 和日线数据）。
- `analyze.py`：汇总分年度收益、显著性、熊市与牛市对比。
- `upwk/run.py`：把框架用在单只股票（UPWK）上的示例。
- 运行：`python matrix.py && python analyze.py`

### wyckoff/ — 威科夫筑底
- `wyckoff_v0.py`：威科夫吸筹阶段识别 v0（方法参考公开资料，代码是自己独立写的）。
- `test_wyckoff_v0.py`：单元测试，用 `pytest test_wyckoff_v0.py` 运行。
- `bt/engine.py`、`bt/engine2.py`：批量扫描和事件回测引擎（读本地行情库，默认目录 `tv_db`，不提供）。
- `bt/sig2.py`：信号定义；`bt/stats.py`：统计检验（DSR、多重检验等）。
- `bt/run_round.py`、`bt/run2.py`：每轮实验的运行器，会记录试验台账。
- `bt/r1.py` ~ `bt/r8.py`：第 1～8 轮迭代实验脚本。
- 运行：`cd wyckoff/bt && python r1.py`（依次运行各轮）。
- `full_bt/run_full.py`、`analyze.py`、`current_list.py`、`make_report.py`：全样本回测（市值>10 亿美元的美股，2005–2026），分别负责生成信号与交易、统计、当前清单和报告。
- `variants.md`：V1–V8 各变体的思路与参数、E1/E2 入场方式、运行方法，以及回测结论摘要。
