---
name: github-skill-search
description: 在 GitHub 上全面检索某一主题的 AI agent skill（SKILL.md/插件/MCP），逐个核实、分级、汇总成中文调研报告，并按需分发给其他 bot 安装。
---
# Github检索 —— GitHub Skill 全面检索与分发

## 用途
为指定主题（如股市信息检索、企业估值、产业链、市场规模、社媒舆情汇总、Serenity 卡脖子方法论）找出 GitHub 上所有相关的 AI agent skill，给出可信度分级与推荐，并在用户同意后交给对应 bot 学习/安装。

## 触发场景
- “去 GitHub 上帮我找……的 skill”
- “把这些 skill 发给 XX bot 让它装上/学一遍”
- “新建一个 bot，把这些 skill 交给它”

## 步骤
1. 明确主题与硬性要求（如“必须是华尔街/权威机构认可的标准方法”“要能追到终端用户”“要精准、有来源”）。
2. 按全面检索方法论（/workspace/method/plan_final.md）执行：
   - 来源地图 + 中英文关键词矩阵；
   - 多渠道：GitHub 仓库/topic/代码搜索、skills.sh 排行、awesome-claude-skills 等 awesome 列表、官方 org（anthropics、openai、数据商 org）；
   - 滚雪球扩展；
   - 逐个打开 README/SKILL.md 核实，按 A/B/C 分级；
   - 饱和检验：连续两轮新增 <5% 才停止；
   - 全部查询写入 query_log。
3. 每个 skill 记录：链接、星标、最近更新、功能、方法、数据源、是否需付费 key/登录、分级、适用场景。
4. 安全审查：标出搬运/改版/可疑仓库，只推荐原作者仓库；提醒先读脚本再装。
5. 产出 /workspace/<主题>_skills/survey.md，向用户用中文汇报：Top 推荐（分类）、覆盖空白、付费/登录注意、局限。
6. 用户同意后：SendToAgent 把清单发给目标 bot（或 CreateAgent 新建 bot 并放入指定分组），附注意事项：只从原仓库安装、先核实、付费 key/注册先问 Taz、key 只在该 bot 自己聊天中提交、用中文汇报。

## 数据源/工具
GitHub API 与 cursor-github 连接器、WebSearch/WebFetch、skills.sh、awesome 列表、SendToAgent、CreateAgent、ListSections。

## 原则
- 全程中文；不编造星标或内容，未核实的标明。
- 只做调研不擅自安装；对外发布/提交需用户本人确认。
