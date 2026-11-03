---
name: tradingview-data
description: 当用户或其他 bot 需要美股/ETF 日线历史数据、全市场数据库、形态扫描数据或每日 P2 状态时使用。数据从用户的 TradingView 高级账户导出，不用 Yahoo。
---
# TradingView 数据导出与行情数据库

## 用途
- 从 TradingView 导出复权日线 OHLCV 全历史（从上市日起）
- 维护全市场数据库（市值 >100 亿美元的美股 + 板块/主题 ETF）
- 给量化类 bot（自主学习、自主学习股市量化版、每日量化策略检测等）供数
- 每个交易日推送 P2 状态和卖出信号

## 触发场景
- “给我 XX 的历史价格/日线数据”
- 其他 bot 请求行情数据或数据库更新
- 交易日 16:03 ET 的定时例程

## 导出步骤
1. 用 box 浏览器打开 TradingView，图表布局只用 `tmp_export_QQQ`（不要动用户的其他布局）。
2. 输入代码，确认交易所是美国本土（NYSE / NASDAQ / NYSE Arca / AMEX / Cboe BZX）；不选外国上市版本。
3. 周期选 1D，打开 ADJ（复权）。
4. Alt+G 跳到 1970-01-01，确认加载到上市首日。
5. 用 Download chart data 下载，时间格式选 ISO。
6. 用 `grab.sh` 把最新下载复制到目标位置；`normalize.py` 统一成 date, open, high, low, close, volume 四价加成交量。
7. 不接受任何数据订阅协议，失败的代码记下来重试。

## 数据库结构（/workspace/tv_db）
- `universe_10B.csv`：股票池（screener 导出）
- `daily/<T>.csv`：各代码日线；`raw/` 存原始导出文件
- `daily.sqlite`：表 `bars`
- `manifest.csv`：ticker, type, exchange, first_date, last_date, rows, flag, issues
- `failed.csv`、`progress.md`、`progress_log.txt`
- 注意：重跑 normalize 会重写 manifest，要把人工备注补回去。

## 质量检查
- 单日涨跌超过 ±30% 的打标记，人工核对（可能是未复权的拆股）
- 检查历史是否被截断（起始日期晚于实际上市日）
- 美股小时线最早只到约 2015 年

## 定时例程
- P2 每日状态推送：工作日 16:03 ET，把 P2 状态和卖出信号发给“每日量化策略检测”。

## 工具
- box 浏览器（TradingView 高级账户）、Shell（Python/SQLite）、SendToAgent（跨 bot 交付）
