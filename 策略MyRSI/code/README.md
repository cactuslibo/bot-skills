# 策略MyRSI 代码

- `myrsi.pine` / `MyRSI.pine`：TradingView 上的 MyRSI（买RSI）指标源码
- `myrsi_opt_3.pine`：规则三策略的 Pine 版本（还没在 TradingView 里验证）
- `rule3.md`：规则三的定义（green 上穿 red 且 close>SMA200 时买入，close<SMA200 时卖出，次日开盘成交）
- `bt.py`：QQQ 单标的回测，用来复现 TradingView 的结果
- `grid.py`：参数网格搜索
- `bt3.py`：20 只 ETF（ARK 系列和 XL 行业 ETF）批量回测，和长期持有对比
- `status.py`：列出近期的信号切换
- `daily.py`：每日收盘后报告每只 ETF 是持仓还是空仓、当天有没有切换

数据放在 `/workspace/data/etf/`，不在这个仓库里。
