# 网络信息搜索 bot

## Skills
- `skill-1793476014685/` — 源头优先全面新闻检索工作流
- `skill-1793247327473/` — 文献下载流程（文献搜索 bot 检索 → SciHub bot 下载）

## Code
### code/bluey_watch/ — Bluey 玩具比价/降价监控
- `build.py` — 根据当日核价数据生成状态 JSON 与邮件报告（HTML/TXT）
- `build_2026-11-03.py` — 读取前一日状态备份，增量更新价格并生成当日报告

### code/literature_search/ — 文献检索与核验
- `q.py` — 按标题批量查询 Crossref，模糊匹配取 DOI
- `d.py` — 按 DOI 批量查询 Crossref 元数据（年份/标题/作者/期刊）
- `cr.py` — 校验论文 CSV 中 DOI 与标题是否一致（Crossref + difflib）
- `v.py` — 批量核验指定 DOI 的作者/年份/期刊，并取摘要
- `run_gai.py` / `run_gai_r2.py` — 调用 Gemini API（需环境变量 `GEMINI_API_KEY`）对综述草稿做两轮评审

数据文件（PDF/zip/csv/HTML/邮件）均未上传。
