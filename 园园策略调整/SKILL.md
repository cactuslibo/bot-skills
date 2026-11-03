---
name: 园园策略调整
description: 运行和调参纳指四季 V22.3 的 1 倍 ETF 版（单只 ETF + 现金），每天输出 XL/ARK 共 20 只 ETF 的持仓状态和切换原因。
---

# 园园策略调整：纳指四季 1 倍 ETF 版

## 用途
- 负责纳指四季 V22.3 改成的单只 1 倍 ETF + 现金版本（原版 QQQ+TQQQ 由 园园ai策略 负责）。
- 每天收盘后给出 20 只 ETF 的状态：持有 100% / 半仓 50% / 空仓，说明当天是否切换，以及触发了哪条规则、用到哪些数值。
- 对策略做回测和调参，比如 DEFEND 仓位、MA200 缓冲带、ARK 单独参数，并做样本外验证防止过拟合。

## 触发场景
- 每日量化策略检测 发来当天的收盘数据，请求跑信号。
- 有人问某只 ETF 某段时间内为什么切换状态。
- Taz 要求调参或回测。

## 标的
- XL 系列：XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY
- ARK 系列：ARKK ARKQ ARKW ARKG ARKF ARKX ARKB IZRL PRNT

## 数据与代码
- 策略：`/workspace/nazhi_siji/siji_1x.py`，入口 `run(csv, **kw)` / `backtest(df)`；批量回测脚本：`batch.py`
- 日线：`/workspace/data/etf/<TICKER>.csv`，列为 date,open,high,low,close,volume，已做分红复权
- 新数据：`/workspace/data/etf/new/<TICKER>.csv`，由 每日量化策略检测 提供（来源 TradingView 或 Yahoo）
- 指标参考：`/workspace/nazhi_siji/ref/final_indicators_list.md`

## 规则（每天按收盘价判断，按收盘价成交）
各状态仓位：NORMAL、ATTACK、DESPAIR 为 100%；DEFEND、TOP_ESCAPE、HI 为 50%；BEAR_CASH、HI_CASH 为 0%。
- A. 价格高于 MA200 × (1+20%) 时进入 HI。HI 状态下，若价格跌破 MA20 且 MA20 下拐，转 HI_CASH；HI_CASH 状态下价格站回 MA20 之上，转 NORMAL。
- B. 放量见顶时进入 TOP_ESCAPE：价格不低于高点的 95%，成交量超过 60 日均量的 2.2 倍，且当天收阴。
- C. 价格低于 MA200 时：
  - 回撤 ≥ 30%：MA20 上拐则进入 DESPAIR，否则进入 DEFEND。
  - 回撤在 10%～30%：价格高于 MA20 则进入 ATTACK，否则进入 DEFEND。
  - 回撤小于 10%：进入 BEAR_CASH。
- D. 价格高于 MA200 时：回撤超过 10% 进入 ATTACK，否则进入 NORMAL。
- E. 从避险状态回到 NORMAL 或 ATTACK，需要已避险至少 2 天，且 MA20 上拐。
- 卖出后第二天（T+1）再买入。

## 每日步骤
1. 把 `new/` 里的新数据行追加到主 CSV（按日期去重）。
2. 对 20 只 ETF 运行 `backtest`，比较最后两天的状态。
3. 列出每只的价格、MA200 偏离、MA20 及其斜率、回撤、成交量与 60 日均量之比。
4. 回复：先写切换了哪几只及触发规则和数值，再按仓位分组列出其余标的，最后给出临界提示（价格贴近 MA200 或 MA20、回撤接近 -10%）。
5. 发现数据异常（例如 open < low）时，说明它会影响哪条规则。

## 已知问题与调参方向
- 19 只有效样本中，只有 2～4 只年化收益跑赢持有，但 18 只回撤更小，回撤中位数改善约 14 个百分点；防御类和 ARK 表现最差。
- XLI、XLRE、XLY 等在 MA200 或 -10% 回撤线附近频繁来回切换，待加缓冲带。
- 调参时用前半段数据调参、后半段数据做样本外验证。
