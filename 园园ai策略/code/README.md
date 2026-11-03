# 园园ai策略：代码

纳指四季 V22.3 策略的回测脚本。仓库里不含数据和密钥，运行前需要自己准备日线 CSV，列为 date,open,high,low,close,volume。

- `backtest.py`：QQQ+TQQQ 回测，和买入持有 QQQ 对比，并打印最新状态快照。读取 `/workspace/data/QQQ_daily.csv` 和 `/workspace/data/TQQQ_daily.csv`。
- `backtest_tv.py`：同一个回测，改用 TradingView 导出的数据。
- `siji_1x.py`：1 倍 ETF 版本。NORMAL、ATTACK、DESPAIR 满仓，DEFEND、TOP_ESCAPE、HI 半仓，现金类状态空仓。
- `batch.py`：用 `siji_1x.py` 批量回测多只 ETF（读取 `/workspace/data/etf/<TICKER>.csv`），输出汇总表和对比图。

依赖：pandas、numpy、matplotlib。
