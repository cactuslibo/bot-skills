---
name: 每日量化策略检测
description: 每个美股交易日收盘后，汇总 XL/ARK ETF 和 QQQ 的多策略持仓状态、QQQ 抄底模型 P2 信号、当日新闻和 Serenity 新推文，并直接发邮件给 Taz。
---

# 每日量化策略检测

## 用途
每个交易日收盘后，生成一封中文策略持仓总结邮件，发送到 bli10@kennesaw.edu（发件邮箱为 Taz 的 Gmail，cactuslibo@gmail.com，已授权直接发送）。

## 触发场景
- 例程：工作日 16:15 ET（cron `15 16 * * 1-5`）；休市日跳过。
- Taz 手动要求补发某天的总结。

## 标的
- QQQ：只交给 园园ai策略（纳指四季 V22.3）。
- XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY、ARKK ARKQ ARKW ARKG ARKF ARKX ARKB IZRL PRNT：交给 策略MyRSI 和 园园策略调整。

## 步骤
1. **数据**：TradingView bot 在 16:03–16:07 ET 发来当日 OHLCV（用小时线合成的日线与日K比对校验）、VIX/VIX3M 收盘值和 P2 结论。数据写入 `/workspace/data/etf/new/<TICKER>.csv`、`/workspace/qqq_bottom/p2_daily.csv` 和 `p2_state.json`。不用 Yahoo 数据。
2. **策略状态**：把数据所在路径告诉三个策略 bot，收回各标的的状态（持有 / 半仓 / 空仓）以及当日切换。
3. **QQQ 抄底模型 P2**（只做多、不加杠杆、不设止损，空仓时持有短债）：收盘 RSI(2)（Wilder）<15 且 VIX/VIX3M<1 时，次日开盘满仓买入；持仓期间收盘价 > SMA5 时，次日开盘全部卖出。以 TradingView 的结论为准，自己用 `/workspace/data/QQQ_daily.csv` 和 `/workspace/qqq_bottom/data/full/` 交叉校验。出现卖出信号时，在当天邮件里醒目标注【P2卖出信号】。规则和回测见 `/workspace/qqq_bottom/tv_round3.md`，代码在 `tv_bt/`。
4. **新闻**：Github股市信息 bot 只在 `/workspace/us-news/output/etf_drivers.md` 的基础上补充当天新闻。
5. **Serenity（@aleabitoreddit）新推文**：用 x 命名空间的 `get_users_posts`（user id 1940360837547565056，排除转推，since_id 取 `/workspace/serenity/state.json` 中的值）拉取，写成中文要点并附链接；邮件发出后更新 state。
6. **邮件结构**：
   - 标题：XL / ARK ETF 及 QQQ 策略持仓状态（截至 YYYY-MM-DD 收盘）
   - 表格（ETF | MyRSI | 园园策略 | 园园 AI 策略），行顺序：QQQ、ARKG、XLB…XLY、ARKK ARKQ ARKW ARKF ARKX ARKB IZRL PRNT
   - P2 一节
   - 规则简述
   - 今日持仓变动（先写策略原因，再写新闻 / 公司原因）
   - Serenity 板块
   - 署名 Taz
7. **发送**：用 user-Gmail 的 `send_email` 发送；发之前用 `search_emails` 查重，每天只发一封。发完后在聊天里用一句中文确认。如果有数据源失败，就不发送，并说明卡在哪一步。

## 工具与数据源
TradingView、策略MyRSI、园园策略调整、园园ai策略、Github股市信息 这几个 bot；Gmail MCP；x MCP；共享电脑 `/workspace` 下的数据文件。
