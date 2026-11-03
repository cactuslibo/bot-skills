# 产业研究-2 / code

产业研究、入行壁垒、AI 制药相关的辅助脚本（已脱敏）。所需 key 走环境变量（`GEMINI_API_KEY`）；邮箱占位为 `YOUR_EMAIL@example.com`，使用前改成你自己的。脚本里的路径仍是原来的 /workspace/... 路径，需按需修改。

- `01_FVRR估值建模/`：Fiverr 估值。model.py 估值模型，build_final.py / edit.py 生成和修改报告，run_gai*.py 调用 Gemini 做检索/复核。
- `02_ISRG_AI/`：直觉外科 AI 主题研究，run_gai*.py 调用 Gemini 检索。
- `03_生命科学入行壁垒/`：文献流程。run_gai 检索，cr/cr2/xref 做 Crossref 校验，oa 查 Unpaywall/OpenAlex 开放获取，dl 下载，grades/new_entries/build_lit/assemble 做分级和文献表汇总，r3/ 是第三轮。
- `04_AI制药/`：AI 制药及受益股研究。ai_pharma_run*、beneficiary run_gai*、health_stocks run 调用 Gemini 分批检索；cfetch.sh 是带 UA 的 curl 抓取器（SEC 要求填联系邮箱）。
- `05_药物价值链/`：药物价值链研究。run_gai* 检索，work/ 下是 Crossref/Unpaywall 校验、下载、去重和文献表构建。
