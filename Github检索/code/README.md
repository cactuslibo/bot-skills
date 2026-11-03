# Github检索 辅助脚本

本机做 GitHub skill 检索时自己写的小脚本（不含下载的他人开源代码，也不含回测/画图脚本）。已做密钥扫描并脱敏：密钥一律从环境变量读取。

| 文件 | 用途 |
|---|---|
| industry_chain_skills/p.py | 解析 GitHub 搜索 API 结果，按轮次记录查询日志(qlog.json)并合并去重仓库库(repos.json)，统计每条查询新增数（饱和检验用） |
| industry_chain_skills/rel.py | 按关键词（产业链/供应链/BOM 等 + skill/agent/MCP）判断候选仓库是否相关 |
| market_size_skills/p.py | 同上，市场规模主题版：解析搜索结果、写 raw/log.json 与 raw/db.json、统计新增 |
| quant-skill-study/run_gai.py | 调用 Gemini 接口提交报告做跨 AI 复核（需 GEMINI_API_KEY、GAI_ENV_ID 环境变量） |
| quant-skill-study/run_gai2.py | 跨 AI 复核第 2 轮，接续上一轮会话（GAI_PREV_INTERACTION_ID） |
| wyckoff/ext.py | 从聊天记录 jsonl 中抽取与威科夫相关的用户需求/消息 |
| wyckoff/fetch.sh | 用 `gh api` 只下载指定仓库的指定源码/规则文件到 sources/ |
| wyckoff/grab.sh | 把浏览器下载的 TradingView 日线 CSV 复制到 raw/ 并显示起始日期和行数 |
