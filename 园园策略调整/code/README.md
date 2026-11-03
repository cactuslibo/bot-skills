# 纳指四季 V22.3 · 1x ETF 版

- `siji_1x.py`：单只 ETF + 现金的状态机回测与每日状态判断（NORMAL/ATTACK/DESPAIR=100%，DEFEND/TOP_ESCAPE/HI=50%，BEAR_CASH/HI_CASH=0%），T+1、收盘成交。
- `batch.py`：对 20 只 ETF（XL* 板块 + ARK 系列等）批量回测并汇总。

数据不在仓库内：需自备 `data/etf/<TICKER>.csv`（列：date,open,high,low,close,volume）。仅供研究，非投资建议。
