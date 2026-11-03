---
name: 每日量化策略检测
description: 每个美股交易日收盘后（约 16:15 ET），汇总 QQQ、行业 ETF 与 ARK 系列 ETF 的五个策略状态、QQQ 抄底模型 P2 信号、阈值预警和 Serenity 推文要点，生成一封中文总结邮件。
---

# 每日量化策略检测

## 用途
每个美股交易日收盘后生成一封中文策略持仓总结邮件（收件人由使用者自行配置）。邮件正文不放任何链接。

## 触发
- 例程：交易日约 16:15 ET（cron `15 16 * * 1-5`），休市日跳过。
- 手动补发某日总结。

## 数据
- TradingView 日线导出为主，yfinance 作补充/交叉校验；VIX、VIX3M 用于 P2。
- 标的：QQQ；ARKG；XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY；ARKK ARKQ ARKW ARKF ARKX ARKB；IZRL；PRNT。

## 五个策略（全部日线）
1. **MyRSI（规则三）**：boo=100·(C+2SD−SMA21)/(4SD)，G=EMA(boo,12)，R=EMA(boo,120)。G 上穿 R 且收盘>SMA200 买入；收盘<SMA200 卖出。代码 `code/myrsi/daily.py`。
2. **园园 1x（纳指四季 V22.3 单一 1x ETF+现金版）**：`code/nazhi_siji/siji_1x.py`。
3. **v1 纳指逃顶**：`code/ndx_escape/bt.py`。
4. **v2 纳指逃顶**：`code/ndx_escape/v2.py`。
5. **P2 抄底**：RSI(2)(Wilder)<15 且 VIX/VIX3M<1 → 次日开盘买入；持仓时收盘>SMA5 → 次日开盘卖出；只做多、不加杠杆、无止损。`code/qqq_bottom/p2_daily.py`。
另：**园园AI**（纳指四季 V22.3，QQQ 信号，ATTACK/NORMAL 持 TQQQ）只针对 QQQ，`code/nazhi_siji/backtest.py`。

## 步骤
1. 拉取当日收盘数据并校验（日线与小时线合成日线比对；缺数据则不发，并说明卡在哪一步）。
2. 运行 `code/strategy_compare/strategies_daily.py` / `matrix.py` 生成各标的五策略状态矩阵与当日变化。
3. 计算园园AI 状态与 P2 信号。
4. 检查各策略距离触发阈值的距离，生成预警。
5. 拉取 Serenity（@aleabitoreddit）自上次以来的新推文（排除转推），写中文要点；发送后更新游标状态。
6. 组装邮件并发送；发前查重，每天只发一封。

## 邮件结构
- 标题：XL / ARK ETF 及 QQQ 策略持仓状态（截至 YYYY-MM-DD 收盘）
1. **园园AI**：当前状态（ATTACK/NORMAL/防守等）、QQQ/TQQQ/现金配比、最近 4 次状态切换、关键阈值与当前距离。
2. **五策略表**（ETF | MyRSI | 园园1x | v1 | v2 | P2），行序：QQQ、ARKG、XLB…XLY、ARKK ARKQ ARKW ARKF ARKX ARKB、IZRL、PRNT。
3. P2 信号（卖出信号醒目标注【P2卖出信号】）。
4. v1 / v2 细节。
5. 规则简述。
6. 今日变动（先策略原因，后新闻/公司原因）。
7. 阈值预警。
8. Serenity 推文摘要。
- 无链接。
