# 自主学习 bot 代码

| 目录 | 用途 |
|---|---|
| bottleneck_metric/ | 供应链"瓶颈度"指标研究：从 SEC EDGAR 拉财务事实（facts.py/edgar.py），打标签（labels_*.py），回测验证（test*.py、followup*.py、repro_check_v2.py）。lit_work/ 是配套文献检索与核验脚本（Crossref/OpenAlex/Unpaywall、Gemini 交叉评分、生成文档）。 |
| toy_chain/ | 玩具产业链的工作流示例脚本（wf.py）。 |
| tv_choke_screen/ | 卡脖子个股筛选：抓数据→分阶段筛选→生成最终报告。 |
| qqq_hourly_rl/ | QQQ 小时线策略搜索与回测：引擎、多轮(r2–r9)搜索、样本外检验、DSR 复算、独立审计，以及 forward_track.py 前向跟踪；gemini_chat/ 为 Gemini 多轮对话辅助工具。 |
| qqq_bottom/、qqq_bottom_1h/ | QQQ 抄底信号研究（日线与 1 小时线）：指标、网格搜索、稳健性与样本外检验。 |
| ai_pharma/、ai_pharma_beneficiary/ | AI 制药主题与受益股研究，调用 Gemini 分批分析。 |

注意：需要的 API key 通过环境变量 `GEMINI_API_KEY` 提供；邮箱等已替换为占位符 `YOUR_EMAIL@example.com`、`YOUR_WORKSPACE_ID`，运行前请改成自己的。
