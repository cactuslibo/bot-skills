---
name: 策略MyRSI
description: 运行 Taz 的 MyRSI（买RSI）“规则三”日线策略：Python 计算信号、回测 ETF、每日收盘后报告持仓/空仓与切换。
---

# 策略MyRSI — 规则三

## 用途
- 把 TradingView 指标「买RSI」(MyRSI) 的“规则三”策略用 Python 实现并长期运行。
- 对 ARK 系列和 SPDR XL 行业 ETF 做回测，和长期持有 (B&H) 对比。
- 每日收盘后给出 20 只 ETF 的信号状态（应其他 bot 如“每日量化策略检测”的请求）。

## 触发场景
- “跑一下规则三 / MyRSI”“今天哪些 ETF 持仓、有没有切换”“回测某 ETF 是否跑赢长期持有”。

## 指标定义（L=21）
- boo = 100*(close + 2*stdev(close,21) - sma(close,21)) / (4*stdev(close,21))，总体标准差 (ddof=0)
- green = ema(boo,12)，blue = ema(boo,26)，red = ema(boo,120)，参考线 -40
- EMA 为 Pine 风格：alpha=2/(n+1)，从第一个有效 boo 起算

## 规则三（日线，只做多，满仓，无手续费）
- 买入：green 上穿 red 且 close > SMA200
- 卖出：close < SMA200
- 收盘出信号，次日开盘成交

## 步骤
1. 数据：向 TradingView bot 索取复权日 K（或由每日量化策略检测提供最新一根），存 `/workspace/data/etf/<TICKER>.csv`，新增行放 `/workspace/data/etf/new/`。
2. 每日：确认 new/ 数据日期最新后运行 `python3 /workspace/myrsi/batch/daily.py`，输出每只的持仓/空仓、当日是否切换、close、SMA200、green、red。
3. 回测：`/workspace/myrsi/batch/bt3.py` 输出总收益、最大回撤、Sharpe 对比 B&H（summary.csv、equity.png）。
4. 用中文回复，标出贴近 SMA200 的临界标的。

## 标的
XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY ARKK ARKG ARKW ARKQ ARKF ARKX PRNT IZRL ARKB

## 已知结论
- QQQ：策略 +449% / 回撤 18.3% / Sharpe 1.14，B&H +512% / 回撤 35.6%。
- 20 只 ETF：总收益仅 XLC、ARKG 跑赢 B&H；19/20 回撤更低；6/20 Sharpe 更好。主要价值是降回撤。

## 数据源/工具
TradingView bot（K 线）、Python (pandas/numpy)、`/workspace/myrsi/` 代码。
