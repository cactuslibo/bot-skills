# Github股市信息：美股新闻管线代码

- `pipeline.py`：按股票代码抓取 TickerTick、Yahoo RSS、Google News、Finviz 的新闻，去重（URL 相同或标题相似度≥0.85）后存入 SQLite，再用 Gemini 生成中文摘要。运行：`python3 pipeline.py --tickers AAPL,MSFT`
- `earnings_fetch.py`：抓取财报日新闻，例如 LLY、MRK。
- `ai_health.py`：按主题汇总一个月的新闻（AI 医疗）；设 `CACHED=1` 时用缓存重建。
- `etf_daily.py`：抓取 ETF 当日新闻和宏观新闻，并做涨跌归因。运行：`DAY=YYYY-MM-DD python3 etf_daily.py`
- `config.json`：标的和参数配置。`requirements.txt`：依赖。

依赖安装：`pip install -r requirements.txt`。使用 Gemini 前先设置环境变量 `GEMINI_API_KEY`，代码里不含任何密钥。数据库和输出文件不包含在仓库里。
