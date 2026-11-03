# 股市信息检索

## 用途
为 Taz 和其他 bot 检索、核实上市公司与资本市场数据（美股、港股、A股），全程中文交付。

## 触发场景
- 查某只股票/公司的基本面、财务、估值、新闻、财报、分析师评级
- 核实交易条款（首付款、里程碑、总额）是否与原始公告一致
- 为产业链研究（如产业研究、自主学习群聊）提供资本市场数据

## 步骤
1. 明确标的与问题，列出需要的指标。
2. 优先查原始披露：SEC EDGAR（10-K/10-Q/8-K/Form 4/13F）、HKEXnews 公告。
3. 用 yfinance 等免费源取行情、市值、EV/Sales、现金流。
4. 交叉验证：行业统计（DealForma、Nature Biopharma Dealmakers）按阶段对比，如首付款占总额比例。
5. 每个数字写明来源和日期；无法确认的标“待核实”。
6. 整理成 Markdown 文件（如 /workspace/<主题>/market.md），以附件或 SendToAgent 交付。

## 数据源与工具
- SEC EDGAR、HKEXnews、yfinance、公司官网与投资者关系页、网页搜索
- 已装技能：yfinance-data、sec-filings-and-ownership、edgartools-sec、global-stock-data、stock-news-and-earnings、analyst-ratings-and-sentiment、macro-and-event-odds、valuation-* 系列

## 规则
- 只用免费数据源；需要付费 key 的先报告 Taz，不自行付费或注册
- 禁止编造数字
- 用中文交付
