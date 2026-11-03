# 园园ai策略：纳指四季 V22.3（QQQ+TQQQ）

## 用途
运行纳指四季 V22.3 状态机策略：回测、每日收盘状态检查、与持有 QQQ 对比。

## 触发场景
- 回测纳指四季，并和买入持有 QQQ 比较
- 问当前状态、仓位、最近信号，以及今天有没有切换
- 其他 bot（如「每日量化策略检测」）发来的每日收盘状态请求

## 数据源
- `/workspace/data/QQQ_daily.csv` 和 `/workspace/data/TQQQ_daily.csv`：历史数据来自 TradingView bot，只做拆股调整，没有分红调整
- 当日 K 线：用 yfinance 拉 Yahoo 的 OHLCV，或用 TradingView bot 提供的文件，追加到上面两个 CSV 末尾

## 规则要点
- 指标：MA200、MA20 及其斜率；从 ATH 算起的回撤（ATH 先用之前 252 根的最高价初始化，之后按收盘价更新）；高于 MA200 的乖离
- 乖离超过 20%：转 HI，100% QQQ；之后走 HI_CASH 解锁链，仓位 0%
- TOP_ESCAPE：收盘 ≥ 0.95×ATH、成交量 > 前 60 日均量的 2.2 倍、当天收跌，三条同时满足时目标 90% QQQ
- 收盘在 MA200 上方：NORMAL，90% TQQQ；回撤超过 -10% 时转 ATTACK
- 收盘在 MA200 下方：
  - 回撤 ≤ -30%：MA20 上行转 DESPAIR，99% TQQQ；否则转 DEFEND，90% QQQ
  - 回撤在 -10% 到 -30% 之间：收盘高于 MA20 转 ATTACK，99% TQQQ；否则转 DEFEND
  - 回撤不到 10%：BEAR_CASH，空仓
- 回到风险仓位前有 2 天冷却期和 MA20 斜率过滤
- T+1 执行：当天卖出，次日买入；只在状态切换时调仓

## 步骤
1. 补齐 QQQ 和 TQQQ 的最新日线
2. 运行 `python3 /workspace/nazhi_siji/backtest.py`，输出回测结果和最新快照
3. 汇报内容：状态、仓位、最近信号、今天是否切换、关键数值（收盘、MA200、MA20、回撤、乖离），以及下一个切换的触发价
