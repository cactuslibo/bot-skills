s=open('report_v1.md').read()
def R(a,b):
    global s
    assert a in s, a[:60]
    s=s.replace(a,b)
R('date: "2026-11-02（美东时间）"','date: "2026-11-02（美东时间）v2：按 GoogleAI R1 复核修订"')
R('- Upwork 的第三季度财报定在 2026-11-02 美东时间盘后发布。本报告写作时（美东 14:54 前后）还没有发布，所以对比用的是 Upwork 最近一季，即 2026 年第二季度的原始数据。',
'- Upwork 的第三季度财报定在 2026-11-02 美东时间盘后发布。v2 定稿时（美东 15:10 前后），SEC EDGAR 上 Upwork 最新的 8-K 仍是 2026-08-10 那份，第三季度数据还没发布，所以对比继续使用 Upwork 2026 年第二季度的原始数据（8-K 新闻稿）。')
# Upwork row
R('| 26Q2 GSV $966.4M（-4%）；营收 $191.7M（-2%）；活跃客户 763K；每客户 GSV $5,230（+5%）；Adj. EBITDA $64.1M（33%）；全年营收指引从 $835–850M 下调到 $730–750M；第三季度指引 $176–184M | [26Q2 新闻稿（SEC 8-K 附件）, 2026-08-10](https://www.sec.gov/Archives/edgar/data/1627475/000162747526000046/upwork2q26-pressrelease.htm)；[IR 新闻列表](https://investors.upwork.com/news-releases/) | GSV/营收/客户数：已核实；指引区间：第三方未核实（[Investing.com, 2026-11-02](https://www.investing.com/news/earnings/upwork-faces-earnings-test-as-ai-reshapes-freelance-work-93CH-4992115)、[AInvest](https://www.ainvest.com/news/upwork-cheap-eps-marketplace-shrinking-q3-test-2611/) 转述，待对照 8-K 原文） |',
'| 26Q2 GSV $966.4M（-4%）；营收 $191.7M（-2%）；活跃客户 763K（去年同期 796K，-4%）；每客户 GSV $5,230（+5%）；Adj. EBITDA $64.1M（33%）；AI 相关工作 GSV 同比 +22% 以上；26Q3 营收指引 $176–184M；FY26 营收指引 $730–750M。年初原指引 $835–850M 不在这份 8-K 中 | [26Q2 新闻稿（SEC 8-K 附件）, 2026-08-10](https://www.sec.gov/Archives/edgar/data/1627475/000162747526000046/upwork2q26-pressrelease.htm) | 上述各项：【已核实-8-K】（v2 由本人重新对照 8-K 原文）；$835–850M：第三方未核实（[Investing.com, 2026-11-02](https://www.investing.com/news/earnings/upwork-faces-earnings-test-as-ai-reshapes-freelance-work-93CH-4992115)） |')
R('- **Upwork 的说法**：AI 相关工作的 GSV 同比 +22%（2026 年 8 月口径）。【第三方未核实，Investing.com 转述，待对照 Upwork 26Q2 股东信】',
'- **Upwork 的说法**："GSV from AI-related work increased more than 22% year-over-year in Q2 2026"；其中 AI Strategy & Consulting 子类同比 +50% 以上。【已核实-8-K，2026-08-10】')
# SIA
R('| A. **全球人才平台（Talent Platforms）毛支出**（交易额口径，包含 Upwork/Fiverr/Toptal 等） | **2025 年 $15.3B** | 2025 年 -2%；SIA 预测到 2027 年大体持平，2019–2027 年 CAGR 约 7% | [SIA, 2026-08-13](https://www.staffingindustry.com/news/global-daily-news/talent-platform-global-gross-spend-falls-2) | 第三方未核实 |',
'| A. **全球人才平台（Talent Platforms）毛支出**（交易额口径，包含 Upwork/Fiverr/Toptal 等） | **2025 年 $15.3B** | 2025 年 -2%；SIA 预测到 2027 年大体持平，2019–2027 年 CAGR 约 7%；美洲/EMEA/APAC 占比 47%/30%/23% | [SIA, 2026-08-13](https://www.staffingindustry.com/news/global-daily-news/talent-platform-global-gross-spend-falls-2) | 已核实（SIA 官方新闻稿；完整报告需付费） |')
R('| C. **上市平台合计交易额（下限锚点）** | 年化约 $4.8–5.0B | 负增长 | Upwork 26Q2 GSV $966.4M×4≈$3.9B；Fiverr marketplace 年化 GMV≈2.447M×$373≈$0.91B | 估算 |',
'| C. **两家上市龙头合计交易额（集中度参考，不是行业下限）** | 约 $4.8B（CR2 约 31%） | 负增长 | Upwork 26Q2 GSV $966.4M×4≈$3.9B；Fiverr marketplace TTM GMV≈2.447M×$373≈$0.91B；$4.8B÷$15.3B≈31% | 估算 |')
R('3. 结论：本报告把可服务的"在线自由职业平台"市场取为 **$15B 上下（2025 年，SIA 口径；区间 $5B（上市平台下限）–$15.3B）**，增速判断为**接近零或为负**。广义灵活用工以万亿美元计，但不是平台能直接拿到的盘子。',
'3. 结论：**在线人才平台行业规模取 $15.3B（2025，SIA）**。Upwork 与 Fiverr 合计约 $4.8B，CR2 约 31%【估算】，这是集中度参考，不是行业规模的下限。增速判断为**接近零或为负**。广义灵活用工以万亿美元计，但不是平台能直接拿到的盘子。')
# share
R('''- Fiverr marketplace 年化 GMV 约 $0.91B（2,447K×$373），【估算】。占 SIA 口径 $15.3B 的约 **6%**，【估算，分子分母年份和口径不完全一致】。Upwork 年化 GSV 约 $3.9B，占约 25%，【估算】。''',
'''- **2025 年（同期口径）**：Fiverr marketplace GMV ≈ Marketplace 营收 $297.5M ÷ take rate 27.7% ≈ **$1.07B**；交叉验证：买家 3,135K × 每买家支出 $342 ≈ $1.07B。占 SIA 2025 年 $15.3B 的约 **7.0%**【估算】。原始数据【已核实】：[Fiverr FY25 新闻稿, 2026-02-18](https://www.globenewswire.com/news-release/2026/02/18/3239912/0/en/fiverr-announces-fourth-quarter-and-full-year-2025-results.html)。
- **2026 年 Q3 TTM**：GMV ≈ 2,447K × $373 ≈ **$0.91B**，$373 本身就是 TTM 口径。假设 2026 年行业规模与 2025 年持平（参照 SIA 的"大体持平"预测），份额约 **6%**【估算】。
- 分子**不计 Services（AutoDS 等）**。理由：Services 是 SaaS/工具订阅收入，不是撮合自由职业交易产生的 GMV，不属于 SIA 人才平台毛支出口径。
- Upwork 年化 GSV 约 $3.9B，占约 25%【估算】。Upwork 的 GSV 包含 Lifted 企业业务和 Connects 等增值服务，口径比 Fiverr GMV 略宽。''')
R('| 买家/客户 | 2,447K / -25.8% | 763K（同比降幅未在本次读到的原文中确认） |','| 买家/客户 | 2,447K / -25.8% | 763K / -4%（796K→763K，8-K） |')
R('| 指引 | Q4 -25%～-20% | Q3 $176–184M（第三方转述），约同比 -11%～-13%（估算） |','| 指引 | Q4 -25%～-20% | Q3 $176–184M（8-K），对比 25Q3 的 $201.7M 约同比 -9%～-13%（估算）；FY26 $730–750M（8-K） |')
R('''- **判断**：网络效应从"流量和供给规模"转向"履约数据和信任"。护城河变窄了，但没有消失。决定成败的是 agent 渠道能否接替搜索渠道（管理层原话："It is a funnel problem"）。''',
'''- **判断**：网络效应从"流量和供给规模"转向"履约数据和信任"。护城河变窄了，但没有消失。管理层把问题定性为"It is a funnel problem"，这是**管理层的说法**，不是本报告的结论。本报告的看法是：**表面是获客漏斗的问题，实质是低端需求被 AI 替代**，这部分交易补回流量也补不回来；**供给侧也存在结构性失衡【判断】**，例如可能出现 AI 低质交付泛滥、高端人才因约 28% 的 take rate 流失【判断，暂无数据支撑】。''')
# ranking section
import re
start=s.index('## 5.2 排序'); end=s.index('# 6. 结论')
s=s[:start]+'''## 5.2 分场景排序（v2：不再做一维总排序）

| 场景 | 排序 | 理由 |
|---|---|---|
| **标准化、小额数字任务**（logo、短文案、小段代码） | **Fiverr > Contra > Upwork** | Fiverr 的 Gig 是预先定价、范围明确的 SKU，正适合 agent 比价和下单；已有公共 API、CLI、MCP；Mira 加 Knowledge Graph 给出"唯一最佳匹配"。Contra 有 MCP 且对自由职业者 0 佣金，但规模未核实。Upwork 走提案和面试流程，偏重 |
| **复杂、长期或企业合规任务** | **Upwork > Fiverr** | Upwork 规模最大（GSV 年化约 $3.9B，估算），有按时计费保障和企业合规（Lifted），已有 Claude Connector 和 MCP。Fiverr 正往高价值项目迁移，$1K+ 项目占订单金额 16% |
| **线下任务** | **RentAHuman / TaskRabbit**（按需求选择，不分先后） | RentAHuman 为 agent 原生设计（自助注册、MCP/REST、托管、webhook），但规模和信任未经验证。TaskRabbit 提供 Partner API（需审批）和 Claude Connector，但 Connector 只做查可用性、查价格和生成预订链接，不会代为预订或付款，且仅限美国 |
| **AI 训练数据 / 人类反馈** | **Scale AI / Surge**（单列为企业数据服务） | 需要企业签约，agent 不能自助调用 |
| 微任务众包 | **MTurk 已退出** | 2026-09-30 关闭 |

**结论**：没有通用的"最佳渠道"。在"agent 采购标准化数字服务"这一场景，Fiverr 最适配；复杂和企业任务选 Upwork；线下任务选 RentAHuman 或 TaskRabbit。真正的竞争点在于谁先做成"agent 端到端付款 + 结果担保"，以及能否守住 take rate。

'''+s[end:]
R('| **TaskRabbit** | Partner API（需申请审批、OAuth M2M）：估价、档期、报价、预订 |','| **TaskRabbit** | Partner API（需申请审批、OAuth M2M）：估价、档期、报价、预订。另有 Claude Connector（2026 年 4 月上架；工具包括 check_service_availability、list_supported_services、generate_deep_link，只生成预订链接，不代为预订，仅限美国） |')
R('| 开发者文档，已核实 |','| 开发者文档，已核实；[Claude Connector 页](https://claude.com/connectors/taskrabbit)、[TaskRabbit 博客](https://www.taskrabbit.com/blog/taskrabbit-is-now-available-in-claude/)，已核实 |')
R('| **已于 2026-09-30 永久关闭**，API 不再可用；SageMaker Ground Truth 的 MTurk 劳动力也已停用 |','| **已于 2026-09-30 永久关闭**，API 不再可用；SageMaker Ground Truth 和 Amazon A2I 中的 MTurk 劳动力同时停用；HIT 审批和奖金发放截止 2026-10-30，交易记录保留到 2027-01-28 |')
R('**结论**：FVRR 的问题在获客漏斗：搜索流量迁移、低端需求被替代，而不是供给侧。',
'**结论**：FVRR 的问题，表面是获客漏斗（搜索流量迁移；"funnel problem"是管理层的说法），实质是低端需求被 AI 替代；供给侧也存在结构性失衡【判断】。')
R('7. Upwork 26Q3（2026-11-02 盘后）：GSV、活跃客户、AI 工作 GSV、是否第三次下调指引。','7. Upwork 26Q3（2026-11-02 盘后）：GSV、活跃客户（26Q2 为 -4%）、AI 工作 GSV（26Q2 为 +22% 以上）、是否再次下调 FY26 指引（$730–750M）。')
# appendix
a=s.index('# 附录')
s=s[:a]+'''# 附录：未核实数据清单（v2）
1. Upwork 年初原 FY26 指引 $835–850M、5 月裁员 24%：媒体转述，不在 26Q2 的 8-K 中。
2. Upwork 26Q3 实际数据：截至美东 15:10 尚未发布。
3. SIA 的 $3.7T 零工经济（2023 年）：没有打开 SIA 原文。
4. Freelancer 1H26 GPV A$574.6M（+30.9%）、marketplace GMV A$42.4M（-20.3%）：没有逐页核对 ASX 的 PDF。
5. Surge 2024 年营收 >$1B、Scale 约 $870M、Meta 以 $14.3B 取得 Scale 49%（估值约 $29B）：媒体报道。
6. Toptal 35,000+ 客户、Contra 1.5M+ 网络：营销口径或第三方说法。
7. RentAHuman、TaskRabbit 的规模：没有可靠数据。
8. 所有份额（7.0%、约 6%、约 25%、CR2 约 31%）和年化 GMV/GSV 均为估算；2026 年份额假设行业规模持平。
9. "AI 低质交付泛滥""高端人才流失"：仅为【判断】，没有数据。
'''
open('report_v2.md','w').write(s)
