# GoogleAI 代码

GoogleAI bot（Google AI Studio / Gemini Interactions·Agents API 代理、独立审稿/红队复核）相关脚本。
密钥只通过环境变量 `os.environ['GEMINI_API_KEY']` 读取；不含数据文件、history.json 与输出结果。

| 目录 | 用途 |
|---|---|
| fvrr/ | Fiverr（FVRR）估值模型、报告构建，以及调用 Gemini 做多轮中文红队复核（run_gai*.py） |
| isrg_ai/ | ISRG 研究报告的 Gemini 多轮红队复核 |
| quant-skill-study/ | 量化指标底稿生成（gen_doc*）、纳指逃顶事件研究，及 Gemini 两轮复核 |
| multiscale_forces_papers/ | 160 篇跨尺度相互作用文献清单：抓取/下载/Crossref·Unpaywall 核验，Gemini 引文审计 |
| levin/bioelectric/ | Levin 生物电文献核对（Crossref）与 Gemini 两轮复核 |
| qqq_bottom/ | QQQ 抄底模型：Gemini 提出候选、辩论（deb*）、回测/样本外；tv_bt/ 为 TradingView 指标移植与多轮回测、门槛检验 |
| qqq_bottom_1h/ | QQQ 小时线抄底模型候选征集（Gemini） |
| qqq_hourly_rl/gemini_chat/ | 通用 Gemini 多轮对话命令行工具 |
| bottleneck_metric/、lifesci_barriers/、tem_analysis/ | 研究结论复核与文献引用批量核验（Gemini） |
| ai_pharma/、ai_pharma_news/、ai_health_stocks/ | AI 制药/医疗股草稿的对抗式审稿与资讯检索 |
| analog_review/、indicator_review/、indicator_correlation/、alphago_rl/ | 指标、类比、相关性、强化学习方案的 Gemini Agent 问答与审核 |
| audit/ | QQQ 小时线研究的前视偏差/数据泄漏独立审计 |
| report/gai*/ | “平台假跌破→新高→崩盘”形态研究的多轮 Gemini 分析与复核 |
| quant_myrsi_v3/、quant_topdiv/、myrsi_top/、rsi_top/、ppo_top/ | MyRSI/RSI/PPO 逃顶指标的 Gemini 独立复核（提交与轮询） |
| search_method/ | 检索方法论的多轮 Gemini 讨论 |
| us-news/ | 美股新闻抓取管线，可选 Gemini 摘要 |
