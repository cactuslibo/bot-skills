---
name: Github股市信息
description: 美股新闻管线：按 ticker / ETF 抓取新闻、去重、用 Gemini 做中文 AI 摘要与涨跌归因；也做行业专题研究报告。只做美股，不做 A 股和量化策略。
---

# Github股市信息

## 用途
- 按个股或 ETF 抓取美股新闻，去重后生成中文摘要，并给出附来源链接的涨跌原因。
- 解读财报日的大涨大跌，例如 LLY、MRK 财报后的走势。
- 做主题汇总，例如过去一个月的 AI 医疗新闻。
- 做行业专题报告，例如 Physical AI 医疗里卡脖子的公司（输出为 Canvas 页面）。
- 做 ETF 每日增量归因，覆盖 QQQ、11 只 XL 板块 ETF、ARK 系、IZRL、PRNT，并包含宏观新闻（美联储、PCE、GDP、美债、关税）。

## 触发场景
- “为什么 XX 今天大涨/大跌”“XX 财报后的新闻”。
- “过去 N 天 / 一个月某主题的新闻总结”。
- “今天这些 ETF 的新闻增量”，通常由 每日量化策略检测 转来。
- “某产业里谁卡脖子、核心竞争力是什么”。

## 数据源（免费）
- TickerTick API：`https://api.tickertick.com/feed?q=z:<ticker>`
- Yahoo Finance RSS：`https://feeds.finance.yahoo.com/rss/2.0/headline?s=<T>&region=US&lang=en-US`，必须带 `User-Agent: Mozilla/5.0`。
- Google News RSS（按关键词搜索）。
- Finviz 个股页面，用 requests 加 BeautifulSoup 抓取。
- 涨跌幅用 yfinance 收盘价。
- 补充：WebSearch / WebFetch，以及文献工具 Undermind。

## 工具与代码（/workspace/us-news）
- `pipeline.py`：按 ticker 抓取 → 去重（URL 相同或标题相似度 0.85 以上）→ 存入 SQLite `news.db` → 生成摘要。运行：`python3 pipeline.py --tickers AAPL,MSFT`
- `earnings_fetch.py`：抓取财报日新闻。
- `ai_health.py`：做主题月度汇总，`CACHED=1` 时用缓存重建。
- `etf_daily.py`：做 ETF 当日增量，含宏观查询。运行：`DAY=YYYY-MM-DD python3 etf_daily.py`
- 输出目录 `output/`，包括 `etf_drivers.md`（累计汇总，每天在末尾追加“增量”章节）和 `etf_daily_<日期>.md`。

## AI 摘要
- 使用 Gemini REST `generateContent`，key 放在 `x-goog-api-key` 请求头里，取自环境变量 `GEMINI_API_KEY`，绝不打印。
- 模型依次为 `gemini-3.5-flash`、`gemini-flash-latest`、`gemini-3.5-flash-lite`。遇到 503 先重试，再换下一个模型。
- 防编造：让模型只输出 `[#n]` 编号，由代码替换成真实链接；`filter_links()` 删除不在抓取列表里的链接。

## 步骤
1. 明确标的和日期范围（默认美东时间）。只做增量时，不重搜历史。
2. 从多个数据源抓取，去重，按日期过滤。注意把 RSS 时间换算成美东时间。
3. 用 Gemini 归类和摘要，每条附公司层面原因和来源链接。
4. 人工核对：剔除不相关的匹配（例如 PTC Therapeutics 和 PTC Inc.、币种和单位错误）；核对关键数字；只凭标题推断的内容要注明。
5. 输出中文 Markdown，必要时写成 Canvas 报告，再回复用户或请求方 bot。

## 规则
- 全程中文。不编造数字和链接。查不到的写“未核实”。
- 只做美股。不发消息、不对外发布，除非用户本人确认。
