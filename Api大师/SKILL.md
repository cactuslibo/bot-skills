---
name: Api大师
description: 调研、对比和接入 API，尤其是金融行情和实时新闻类 API。用户需要找数据源、比较 API、调试请求或写对接代码时使用。
---

# Api大师

## 用途
帮助 Taz 找到合适的 API 和数据源，比较时效、覆盖范围和费用，并协助调试和写对接代码。全程使用中文交流。

## 触发场景
- 需要某类数据（如个股实时新闻、行情、财报）的数据源或 API 清单
- 比较多个 API 的价格、免费额度、延迟、是否支持按股票代码检索
- 调试 API 请求或报错，编写对接脚本

## 步骤
1. 按信息传播的路径分层列出提供方：官方一手披露（SEC EDGAR 8-K、公司 IR、PR Newswire/Business Wire/GlobeNewswire），然后是通讯社和终端（Reuters/LSEG、Bloomberg、Dow Jones、MT Newswires、Benzinga Pro），再到新闻和数据 API（Massive/Polygon、Finnhub、Alpaca、Alpha Vantage、Tiingo、Marketaux、FMP、EODHD），最后是社交和转录（X 快讯账号、StockTwits、财报电话会议转录）。
2. 以官方价格页和 API 文档为准，核实费用、免费额度、时效，以及能否按股票代码和时间筛选；第三方比价页的数据只用来补充，并注明来源。
3. 查不到的标为"未核实"，不编造数字。
4. 输出中文表格（名称、类型、时效、按代码检索、文档链接、费用），附推荐组合和找源思路。
5. 需要时编写脚本，按股票代码和最近时间窗口拉取数据，按时间倒序合并后再交给 AI 总结，避免拿到旧新闻。

## 用到的工具和数据源
网页搜索和网页抓取、box 上的 Shell（写和运行脚本）、各家 API 的官方文档。
