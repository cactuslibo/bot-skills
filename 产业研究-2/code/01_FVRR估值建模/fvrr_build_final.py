import re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import docx.opc.constants

import os
FONT_EA = os.environ.get("FONT_EA","Microsoft YaHei"); FONT_LAT = "Arial"
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("left_margin","right_margin"): setattr(sec, m, Cm(2.2))
sec.top_margin = sec.bottom_margin = Cm(2.0)

def set_font(run, size=None, bold=None, color=None):
    run.font.name = FONT_LAT
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in ('w:ascii','w:hAnsi','w:cs'): rf.set(qn(a), FONT_LAT)
    rf.set(qn('w:eastAsia'), FONT_EA)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if color: run.font.color.rgb = RGBColor.from_string(color)

st = doc.styles['Normal']; st.font.size = Pt(10.5); st.font.name = FONT_LAT
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT_EA)
st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.25
for name, size, color in (("Heading 1", 15, "1F3864"), ("Heading 2", 12.5, "2E5597"), ("Title", 20, "1F3864")):
    s = doc.styles[name]; s.font.size = Pt(size); s.font.bold = True
    s.font.color.rgb = RGBColor.from_string(color); s.font.name = FONT_LAT
    rpr = s.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in ('w:ascii','w:hAnsi','w:cs'): rf.set(qn(a), FONT_LAT)
    rf.set(qn('w:eastAsia'), FONT_EA)
    for a in ('w:asciiTheme','w:hAnsiTheme','w:eastAsiaTheme','w:cstheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
doc.styles["Heading 1"].paragraph_format.space_before = Pt(14)
doc.styles["Heading 2"].paragraph_format.space_before = Pt(8)

def add_hyperlink(p, url, text=None, size=None):
    part = p.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), r_id)
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts')
    for a in ('w:ascii','w:hAnsi','w:cs'): rf.set(qn(a), FONT_LAT)
    rf.set(qn('w:eastAsia'), FONT_EA); rpr.append(rf)
    c = OxmlElement('w:color'); c.set(qn('w:val'), '0563C1'); rpr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size*2))); rpr.append(sz)
    r.append(rpr); t = OxmlElement('w:t'); t.text = text or url
    t.set(qn('xml:space'), 'preserve'); r.append(t); h.append(r); p._p.append(h)

URL_RE = re.compile(r'(https?://[^\s，。；、）)]+)')
def rich(p, text, size=None, color=None):
    # **bold** and auto-link URLs
    for i, part in enumerate(re.split(r'\*\*', text)):
        if not part: continue
        for j, seg in enumerate(URL_RE.split(part)):
            if not seg: continue
            if j % 2 == 1: add_hyperlink(p, seg, size=size)
            else: set_font(p.add_run(seg), size=size, bold=(i % 2 == 1), color=color)
    return p

def para(text, size=None, color=None, align=None, after=None):
    p = doc.add_paragraph(); rich(p, text, size, color)
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p
def bullet(text, size=None, level=0):
    p = doc.add_paragraph(style='List Bullet' if level == 0 else 'List Bullet 2'); rich(p, text, size)
    p.paragraph_format.space_after = Pt(2); return p
def numbered(text, size=None):
    p = doc.add_paragraph(style='List Number'); rich(p, text, size)
    p.paragraph_format.space_after = Pt(2); return p
def h1(t): doc.add_heading(t, level=1)
def h2(t): doc.add_heading(t, level=2)

def shade(cell, hexcolor):
    tcPr = cell._element.get_or_add_tcPr(); s = OxmlElement('w:shd')
    s.set(qn('w:val'), 'clear'); s.set(qn('w:color'), 'auto'); s.set(qn('w:fill'), hexcolor); tcPr.append(s)
def table(rows, widths=None, size=9, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = ''
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.1
            rich(p, val if (i or not header) else f"**{val}**", size=size)
            if i == 0 and header: shade(c, 'D9E2F3')
            if widths: c.width = Cm(widths[j])
    if widths:
        t.autofit = False
        tblPr = t._tbl.tblPr
        lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
        for j, col in enumerate(t.columns): col.width = Cm(widths[j])
        grid = t._tbl.tblGrid
        for j, gc in enumerate(grid.findall(qn('w:gridCol'))): gc.set(qn('w:w'), str(int(widths[j]*567)))
    if header:
        trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ================= Title + Executive summary (one page) =================
p = doc.add_paragraph(style='Title'); rich(p, "Fiverr International（NYSE: FVRR）最终研究报告")
p.paragraph_format.space_after = Pt(2)
para("财报解读 · 产业地位 · 估值 · AI agent 雇人渠道　|　撰写日期：2026-11-02（美东时间）　|　致：Taz", size=9, color="595959", after=6)

h1("执行摘要")
table([
    ["项目", "结论"],
    ["财报（Q3'26，2026-10-29 发布）", "**超预期，但基本面恶化，整体偏负面。**营收 $90.9M、调整后 EBITDA $14.5M 双双超出指引上限（$88M / $12M），全年指引上调；但 Marketplace 营收 -24.7%、活跃买家 -25.8%、FCF -67.8%，Q4 营收指引同比 -25%～-20%，管理层预警 2027 年流量下滑更陡、利润率承压。"],
    ["合理价值", "**$9.5–15，中值约 $12.5**；现价约 **$8.68**（$8.675，11/2 美东 15:15 盘中价）。每股净现金 **$8.49**（$316.2M ÷ 37.24M 股），市场给经营业务的 EV 仅约 $7M。"],
    ["估值方法", "DCF（扣 SBC）熊/基/牛 **$9.0 / $12.5 / $21.9**；可比法约 $10–14；反向 DCF：若 FCF 维持 FY26 水平，现价隐含现金流**永续每年 -84%** 衰减。"],
    ["定性", "现价偏低，但便宜有理由：这是\"现金壳 + 下滑业务\"的定价，**可能是价值陷阱**。上行需要证据：2027 指引不崩、FCF 不转负、回购重启、agent 下单上线并贡献 GMV。"],
    ["行业位置", "在线人才平台行业 2025 年毛支出 $15.3B（SIA，-2%，至 2027 年大体持平）；Fiverr 份额由 2025 年约 7.0% 降至 26Q3 TTM 约 6%【估算】。表面是获客漏斗问题，实质是低端需求被 AI 替代。"],
    ["AI agent 雇人渠道", "**看场景**：标准化小额线上任务选 Fiverr；复杂/企业任务选 Upwork；线下任务选 RentAHuman 或 TaskRabbit；Scale/Surge 走企业合同；MTurk 已于 2026-09-30 关闭。截至 11/2，Fiverr 官方 MCP 只有一个只读工具 Find_freelancers，agent 可交易性落后 Upwork 一步。"],
    ["复核", "产业研究、估值分析与 GoogleAI 交叉复核三方结论一致；GoogleAI 无\"必须修改\"项，4 处细节修改已在本报告中落实。"],
], widths=[3.6, 13.0], size=9)
para("本报告不构成投资建议。数字均来自本次工作的源文件；【估算】【假设】【判断】为分析人自己的推算或判断。", size=8.5, color="595959")
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ================= 1. Earnings =================
h1("一、财报日期与解读")
h2("1.1 财报日期")
bullet("**最近一期：**2026 年 10 月 29 日（周四）美东时间盘前发布 Q3 2026 业绩，同日美东 8:30 召开电话会议 [PR]。")
bullet("**下一期（Q4/全年 2026）：**yfinance 显示约为 **2027-02-17**（预估，公司尚未确认）[YF]；公司将在 Q4 财报时给出 2027 全年指引 [PR]。")
h2("1.2 核心数据（Q3'26 vs Q3'25）[PR][SL]")
table([
    ["指标", "Q3'26", "Q3'25", "变化"],
    ["总营收", "$90.9M", "$107.9M", "-15.8%"],
    ["Marketplace 营收", "$55.4M", "$73.6M", "-24.7%"],
    ["Services 营收", "$35.5M", "$34.3M", "+3.4%"],
    ["年活跃买家", "2.447M", "3.297M", "-25.8%"],
    ["买家年均支出", "$373", "$330", "+12.9%"],
    ["平台抽成率（TTM）", "28.2%", "27.6%", "+60bp"],
    ["GAAP 毛利率 / Non-GAAP 毛利率", "81.3% / 84.4%", "81.7% / 84.2%", "-40bp / +20bp"],
    ["调整后 EBITDA（利润率）", "$14.5M（16.0%）", "$24.2M（22.4%）", "-640bp"],
    ["GAAP 营业利润", "-$0.7M", "+$0.1M", "由盈转亏"],
    ["GAAP 净利润（EPS）", "$1.3M（$0.03）", "$5.5M（$0.15）", "-77%"],
    ["Non-GAAP 净利润（摊薄 EPS）", "$16.0M（$0.43）", "$30.5M（$0.77）", "-47%"],
    ["经营现金流 / 自由现金流", "$9.5M / $9.4M", "$29.2M / $29.1M", "-67.6% / -67.8%"],
], widths=[5.6, 3.8, 3.8, 3.4])
bullet("**季度趋势：**调整后 EBITDA 利润率 Q3'25 22.4% → Q4'25 24.7% → Q1'26 21.4% → Q2'26 17.9% → Q3'26 16.0%；FCF $29.1M → $21.8M → $21.0M → $13.6M → $9.4M，持续下滑 [PR]。")
bullet("**费用：**总营业费用 $74.5M，同比 -15%（研发 -28%、G&A -23%）；股权激励 $6.7M vs $11.9M。利润主要靠削减成本撑住 [PR]。")
bullet("**现金与回购：**季末现金、存款及有价证券合计 **$316.2M**；Q3 没有回购，前 9 个月回购 $8.0M（去年同期 $22.5M）[PR]。")
bullet("**可转债：**9/30/26 和 12/31/25 两张资产负债表**均无可转债科目**；可转债摊销 Q3'25 为 $0.643M、Q4'25 为 $0.214M、2026 年为 0，说明可转债已在 **Q4'25 到期清偿** [PR；GoogleAI 复核核对]。")
bullet("**买家/客单价：**买家数下滑 26%，部分被客单价提升抵消；$1,000+ 高价值项目占 TTM 完成订单 GMV 的 16% [PR][TR]。")
h2("1.3 与预期对比")
bullet("Q3 指引：营收 $80–88M、调整后 EBITDA $8–12M；实际 $90.9M / $14.5M，**双双超指引上限** [SL]。")
bullet("营收比 Zacks 一致预期 $84.48M 高 7.6%；EPS $0.43 vs 一致预期 $0.36（+19%）[ZK]。yfinance 口径：EPS 预期 $0.30，意外 +43.7% [YF]。（一致预期为第三方数据，GoogleAI 复核亦未追到原始出处。）")
bullet("分项：活跃买家 2.45M vs 预期 2.39M；Marketplace $55.41M vs $53.94M；Services $35.49M vs $30.54M；抽成率 28.2% vs 27.9% [ZK]。**超预期主要来自 Services（AutoDS 电商工具）。**")
h2("1.4 指引 [PR][SL]")
table([
    ["", "Q4 2026", "2026 全年（上调）"],
    ["营收", "$80–86M（同比 -25%～-20%）", "$374–380M（-13%～-12%）"],
    ["调整后 EBITDA", "$6–10M", "$61–65M"],
], widths=[3.6, 6.5, 6.5])
bullet("yfinance 财报后一致预期：Q4 营收 $82.85M、全年 $376.35M，大致落在指引中点 [YF]。")
bullet("**2027 预警：**管理层预计\"从搜索转向 AI 驱动的发现\"会让平台流量到 2027 年下滑得比此前预期更陡，2027 调整后 EBITDA 利润率将承压 [PR]。yfinance 2027 一致预期营收约 $296.8M（-21.1%），EPS $0.56 [YF]。")
h2("1.5 管理层关于 AI 的表述")
bullet("AI 正在压缩低价值、交易型工作；\"低价值工作的萎缩快于我们向高端工作转型的速度\" [SL]。")
bullet("传统 SEO/SEM 流量受 AI 冲击；公司转向 GEO、嵌入外部 LLM 生态，用 Knowledge Graph 做基于交付结果的匹配，推广 Mira AI 猎头 [PR]。CEO Micha Kaufman 将平台定位为\"AI-first, agentic-friendly work platform\" [PR]。")
bullet("首席业务官 Jinjin Qian 离职（不愿迁居以色列），继任者搜寻中 [PR]。")
h2("1.6 股价反应（统一标注时点）[YF]")
table([
    ["日期", "价格", "口径", "变化"],
    ["10/28（财报前）", "$8.08", "收盘", "—"],
    ["10/29（财报日）", "$9.05", "收盘", "+12.0%"],
    ["10/30", "$8.39", "收盘", "-7.3%"],
    ["11/02（较早）", "$8.80", "盘中价（财报解读拉取时）", "较财报前 +8.9%"],
    ["11/02 美东 15:15", "$8.675（约 $8.68）", "盘中价（估值拉取时）", "较财报前约 +7.4%【估算】"],
], widths=[3.6, 3.6, 5.6, 3.8])
para("**说明：**$8.80 与 $8.675 **都是 11/2 的盘中价**，只是拉取时点不同；本报告估值与执行摘要统一采用 $8.675（约 $8.68）。市场先因超预期和上调指引大涨，次日因 2027 预警回吐一半以上。")
h2("1.7 结论：战术上的 beat，战略上的警告")
para("**亮点：**①营收、EBITDA、EPS 全面超指引和一致预期，全年指引上调；②Services +3.4%；③客单价 +12.9%、抽成率升至 28.2%；④Non-GAAP 毛利率 84% 以上，$316M 现金类资产、无可转债。")
para("**问题：**①核心平台营收 -24.7%、买家 -25.8%，结构性萎缩且加速；②Q4 营收指引降幅进一步扩大；③EBITDA 利润率 16%（去年 22.4%），FCF -68%，GAAP 营业利润转负；④2027 流量与利润率预警；⑤回购停滞、高管变动；⑥超预期主要因为预期被大幅调低和成本削减，是\"不如预期那么糟\"，不是增长恢复。")

# ================= 2. Industry =================
h1("二、产业地位与行业趋势")
h2("2.1 市场规模（多口径，不可相加）")
table([
    ["口径", "规模", "增速", "核实级别"],
    ["A. 全球人才平台毛支出（SIA）", "2025 年 $15.3B", "2025 年 -2%；至 2027 年大体持平；2019–2027 CAGR 约 7%；美洲/EMEA/APAC 47%/30%/23%", "已核实（SIA 官方新闻稿）"],
    ["B. 全球\"零工经济\"（SIA 广义）", "2023 年 $3.7T", "—", "第三方未核实"],
    ["C. Upwork + Fiverr 合计交易额", "约 $4.8B（CR2 约 31%）", "负增长", "估算（集中度参考，非行业下限）"],
    ["D. AI 数据标注/人类反馈", "Surge 2024 营收 >$1B；Scale 2024 约 $870M", "高增长", "第三方未核实（Reuters）"],
], widths=[4.4, 3.6, 5.6, 3.0])
para("结论：在线人才平台行业规模取 **$15.3B（2025，SIA）**，增速接近零或为负。平台营收≈GMV×take rate（Fiverr 约 28%，Upwork 约 20%），把平台营收当市场规模会低估 3–5 倍。")
h2("2.2 Fiverr 份额【估算】")
bullet("**2025 年：**Marketplace 营收 $297.5M ÷ take rate 27.7% ≈ GMV **$1.07B**（交叉验证：3,135K 买家 × $342 ≈ $1.07B），占 $15.3B 约 **7.0%**。")
bullet("**26Q3 TTM：**GMV ≈ 2,447K × $373 ≈ **$0.91B**，假设 2026 年行业持平，份额约 **6%**。分子不计 Services（AutoDS 为工具订阅收入，不属 SIA 口径）。")
bullet("Upwork 年化 GSV 约 $3.9B，占约 25%。")
h2("2.3 竞争格局")
table([
    ["平台", "定位", "关键数据", "核实级别"],
    ["Fiverr", "固定价 Gig 起家，延伸到高价值项目与 Services（AutoDS）", "26Q3 营收 $90.9M（-15.8%）；买家 2,447K（-25.8%）；take rate 28.2%", "已核实"],
    ["Upwork", "最大综合型平台，按时/按项目，企业业务（Lifted）", "26Q2 GSV $966.4M（-4%）；营收 $191.7M（-2%）；活跃客户 763K（-4%）；Adj. EBITDA 33%；AI 相关工作 GSV +22% 以上；FY26 指引 $730–750M", "已核实-8-K"],
    ["Freelancer（ASX: FLN）", "竞价型 + Escrow.com、Loadshift", "1H26 GPV A$574.6M（+30.9%）；核心 marketplace GMV A$42.4M（-20.3%）", "第三方未核实"],
    ["Toptal", "私营，\"Top 3%\"精选人才", "官网称 35,000+ 客户", "第三方未核实"],
    ["Contra", "对自由职业者 0 佣金，已推出 MCP", "\"1.5M+\"网络规模出自检索摘要", "模式已核实；规模未核实"],
    ["Malt、Freelance.com", "欧洲区域平台", "SIA 认为 EMEA 份额上升主要由其推动", "已核实（SIA）"],
], widths=[2.8, 4.4, 6.6, 2.8], size=8.5)
h2("2.4 Fiverr 与 Upwork 最近一季对比")
table([
    ["指标", "Fiverr 26Q3", "Upwork 26Q2"],
    ["营收 / 同比", "$90.9M / -15.8%", "$191.7M / -2%"],
    ["买家/客户", "2,447K / -25.8%", "763K / -4%"],
    ["单客价值", "$373 / +12.9%", "$5,230 / +5%"],
    ["变现率", "take rate 28.2%", "营收/GSV 约 19.8%（估算）"],
    ["利润率", "Adj. EBITDA 16.0%", "Adj. EBITDA 33%"],
    ["指引", "Q4 -25%～-20%", "Q3 $176–184M（约同比 -9%～-13%，估算）；FY26 $730–750M"],
], widths=[3.6, 6.0, 7.0])
para("Upwork 26Q3 财报定于 2026-11-02 美东盘后发布；产业研究定稿时尚未发布，故对比使用 26Q2 的 8-K 数据。")
h2("2.5 护城河与趋势判断")
bullet("**仍然存在：**Knowledge Graph 与履约数据（每月 3.3M 次技能抽取、约 70,000 项硬技能）；托管支付、争议处理、税务/合规等信任基础设施；高端人才社区；$316M 现金；AutoDS 带来的多元化。")
bullet("**正在被侵蚀：**以 SEO/SEM 为核心的获客引擎；标准化 Gig 被 AI 替代；28% 的高 take rate 在 agent 比价、Contra 0 佣金环境下难以维持。")
bullet("**判断：**管理层称\"It is a funnel problem\"（管理层说法）；本报告看法是**表面是获客漏斗问题，实质是低端需求被 AI 替代**，供给侧也存在结构性失衡【判断，暂无数据支撑】。")
bullet("**行业趋势：**低价值任务被替代、AI 答案引擎压缩自然流量、行业总盘子停滞；机会在客单价上升、agent 成为新分发渠道（Fiverr、Upwork、Contra、RentAHuman 都在抢 MCP 入口）、平台售卖\"AI labor\"（SIA 称近半数平台在布局）。份额向高价值、强信任平台集中。")

# ================= 3. Valuation =================
h1("三、估值")
h2("3.1 关键输入")
table([
    ["项目", "数值", "来源"],
    ["股价", "$8.675（11/2 美东 15:15 盘中价；$8.80 为同日较早盘中价）", "[YF]"],
    ["现金+存款+有价证券", "$316.2M = 现金 125.5 + 短期证券 26.0 + 银行存款 90.0 + 长期证券 74.8", "[PR] 9/30/26"],
    ["用户资金 $146.4M", "不计入（对应负债 User accounts $137.3M）；受限存款 $3.4M 亦未计入", "[PR]"],
    ["有息债务", "0。9/30/26 和 12/31/25 资产负债表均无可转债科目；Q4'25 摊销 $0.2M、2026 年为 0，可转债已于 Q4'25 到期清偿", "[PR]"],
    ["摊薄股数", "37.24M（Q3'26 摊薄加权）", "[PR]"],
    ["每股净现金", "$8.49（316.2 / 37.24）", "计算"],
    ["市值 / 企业价值", "$323M / 约 $7M", "计算"],
    ["FY26 FCF", "≈$49M（9M26 $44.0M + 假设 Q4 约 $5M）", "【假设】"],
    ["2027 一致预期", "营收 $296.8M（-21.1%），EPS $0.56", "[YF]"],
    ["SBC", "Q3'26 $6.7M（营收 7.4%），9M26 $23.9M", "[PR]"],
], widths=[3.8, 10.4, 2.4])
h2("3.2 DCF（FCFF，无债务 → WACC = 股权成本）")
para("Rf 4.89%（10 年期美债，11/2）[YF]；ERP 4.20%（Damodaran，2026-10-01）；Beta 基准 1.38（yfinance 5 年月度 1.55 与 2 年周线 1.22 的均值），熊 1.55、牛 1.22 → WACC 熊 11.4% / 基 10.7% / 牛 10.0%。起点 FY26 营收 $377M（指引中值）；FCFF 利润率为【假设】。")
table([
    ["情景", "2027–31 营收增速", "FCFF 利润率", "永续 g", "WACC", "每股（报告 FCF）", "每股（扣 SBC，主口径）"],
    ["熊", "-28%, -15%, -8%, -5%, -3%", "5→8%", "-2%", "11.4%", "$11.75", "**$9.04**"],
    ["基", "-21%, -8%, -2%, +1%, +2%", "8→12%", "+1%", "10.7%", "$16.97", "**$12.49**"],
    ["牛", "-15%, 0%, +5%, +6%, +6%", "12→18%", "+2.5%", "10.0%", "$29.14", "**$21.93**"],
], widths=[1.2, 4.4, 2.2, 1.6, 1.6, 2.6, 3.0], size=8.5)
para("扣 SBC 版本：各年利润率减 6pp，把股权激励视为真实成本（FVRR SBC 长期偏高）。基准情景 WACC 9%–13% × g -2%–3% 的敏感性区间为 $14.41–$21.40（报告 FCF 口径），区间窄，因为 $8.49/股是现金；真正的变量是利润率与下滑速度。")
para("**AI 情景权重【假设】：**A 智能体绕开（熊，~$9.0）40% / B 混合（基，~$12.5）45% / C Fiverr 成为智能体的人类交付层（牛，~$21.9）15% → 概率加权 ≈ **$12.5**（GoogleAI 重算 $12.53）。")
h2("3.3 可比公司（yfinance TTM，2026-11-02）")
table([
    ["公司", "营收增速（最近季 YoY）", "EV/Sales", "EV/EBITDA", "P/FCF"],
    ["FVRR（核实 EV≈$7M，FY26E）", "-15.8%", "0.02x", "0.1x", "6.6x（FY26E）/ 8.6x（Q3 年化）"],
    ["FVRR（yfinance 口径，现金仅计 $241M）", "-15.8%", "0.17x", "1.2x", "4.2x"],
    ["Upwork（UPWK）", "-1.7%", "1.15x", "6.1x", "7.9x"],
    ["Etsy（ETSY）", "+10.9%", "2.80x", "16.6x", "13.2x"],
    ["eBay（EBAY）", "+13.7%", "4.73x", "18.4x", "31.3x"],
], widths=[5.2, 3.2, 2.2, 2.2, 3.8], size=8.5)
para("FVRR 下滑速度约为 UPWK 的 8–10 倍、利润率只有一半，理应大幅折价。用 UPWK 倍数（加回 $316M 现金）：EV/Sales 折价 50% → $14.3；EV/EBITDA 折价 50% → $13.6；P/FCF 不折价 → $10.3。**可比法区间约 $10–14。**")
h2("3.4 反向 DCF")
bullet("市值 $323M − 净现金 $316M = 市场给经营业务的 EV 仅约 **$7M**（$6.8M）。")
bullet("在 10.7% WACC 下，$7M EV 只需每年约 $0.7M 永续 FCFF（g=0）即可支撑；而 FY26 经营性 FCF 约 $41M（扣除约 $8M 财务收入【假设】）。")
bullet("若 FCF 维持 FY26 水平，现价隐含**永续每年 -84%**（-84.3%）的现金流衰减：市场近乎认定平台业务价值归零，或认为现金会被消耗/低效使用，或对以色列风险/治理折价。")
h2("3.5 估值结论")
table([
    ["方法", "区间", "中值"],
    ["DCF（扣 SBC，熊/基/牛）", "$9.0 / $12.5 / $21.9", "$12.5"],
    ["DCF（按报告 FCF）", "$11.8 / $17.0 / $29.1", "$17.0"],
    ["可比法（UPWK 倍数折价 30–50%）", "$10–14", "~$12"],
    ["反向 DCF", "现价隐含经营业务≈0（-84%/年）", "—"],
    ["**综合合理价值区间**", "**$9.5–15**", "**≈$12.5**"],
], widths=[6.0, 6.6, 4.0])
para("现价 $8.68 ≈ 每股净现金 $8.49，较中值低约 30%（中值高出约 44%）。**现价偏低，但便宜有理由**——\"现金壳 + 下滑业务\"的定价，**可能是价值陷阱**，不是明显错杀。")

# ================= 4. Agent channel =================
h1("四、专题：AI agent 上网雇人类干活，哪个渠道最好？")
para("**结论：没有通用的\"最佳渠道\"，要看场景。**")
table([
    ["场景", "首选", "理由"],
    ["标准化、小额线上任务（logo、短文案、小段代码）", "**Fiverr** > Contra > Upwork", "Gig 是预先定价、范围明确的 SKU，适合 agent 比价和下单；Mira + Knowledge Graph 给出最佳匹配。但目前下单仍需人工完成"],
    ["复杂、长期或企业合规任务", "**Upwork** > Fiverr", "规模最大（GSV 年化约 $3.9B，估算），按时计费保障和企业合规（Lifted）；官方 MCP 可起草职位、提案和 offer"],
    ["线下任务", "**RentAHuman / TaskRabbit**（按需选择）", "RentAHuman 为 agent 原生设计（MCP/REST、托管、webhook），但规模和信任未经验证；TaskRabbit 有 Partner API（需审批），Claude Connector 只查可用性/价格并生成预订链接，不代为预订，仅限美国"],
    ["AI 训练数据 / 人类反馈", "**Scale AI / Surge**", "企业合同制托管服务，agent 不能自助调用"],
    ["微任务众包", "**MTurk 已退出**", "2026-09-30 永久关闭，API 不再可用；HIT 审批和奖金发放截止 2026-10-30，交易记录保留到 2027-01-28"],
], widths=[4.4, 3.8, 8.4], size=8.5)
h2("4.1 Fiverr 与 Upwork 的 MCP 现状（按 GoogleAI 复核改用官方出处）")
bullet("**Fiverr MCP：**官方页面 https://www.fiverr.com/mcp 写明\"In this first phase, Fiverr MCP Server offers one tool: freelancer search\"。**截至 2026-11-02，只有一个只读工具 Find_freelancers**（\"Read-only search\"，无需登录）。即 agent 目前只能搜人，不能下单付款；公司\"agent 找人、定范围、下单、付款全流程\"的目标仍是愿景 [SL]。")
bullet("**Upwork MCP：**官方页面 https://www.upwork.com/ai/mcp 与帮助中心 https://support.upwork.com/hc/en-us/articles/55446516654611-How-to-use-Upwork-with-AI-agents-through-MCP ：可起草并发布职位（\"Draft a job post… publish\"）、起草并提交提案、按范围和费率准备 offer。**offer 只生成草稿，用户在 upwork.com 付款后才会发出**（\"You complete the binding offer on upwork.com\"）。")
bullet("Upwork 另于 2026-06-17 推出 Claude Connector、2026-08-10 推出 MCP，11/2 推出 Upwork Now（在 AI 工具内\"几分钟内雇到在线专家\"，早期测试多数 30 分钟内雇佣）[UPN]。→ **在 agent 可交易性上 Fiverr 目前落后 Upwork 一步。**")
bullet("Fiverr 的积极信号：Q3 推出首批公开 API、CLI 及 MCP 集成，已上线 Claude 与 ChatGPT；AI 来源的首单买家 GMV 环比约 +64%；fiverr.com 发布 llms.txt [SL][LLM]。")
h2("4.2 对 FVRR 的含义")
para("固定价、标准化的 Gig 天生比时薪/竞标模式更适合 agent\"一键下单\"，Knowledge Graph 可成为 agent 的信任/匹配信号；但低价 Gig 恰恰最先被 AI 本身替代，agent 跨平台比价会削弱品牌与 SEO 护城河并**压低 28.2% 的抽成率**。净判断：agent 渠道对 Fiverr **流量净负面、单客价值正面**；机会在于成为 agent 调用的\"人类交付层\"，但抽成率大概率被压缩。")

# ================= 5. Risks =================
h1("五、风险")
for t in [
    "**下滑超预期：**2027 营收下滑超过 -21%、EBITDA 利润率进一步走低，FCF 转负后现金被侵蚀，熊市下限会跌破净现金。",
    "**资本配置：**管理层用现金做低回报收购/转型（AutoDS 类 earn-out 负债已存在；应计及其他应付 $72.4M、其他非流动负债 $13.6M，Q3 earn-out 重估 $3.4M）。",
    "**抽成率压缩：**agent 比价、Contra 0 佣金环境下，28.2% 的 take rate 难以维持。",
    "**竞争：**Upwork 在 agent 交易能力上领先（MCP 可起草 offer、Upwork Now）；agent 原生平台（RentAHuman）与 OpenAI/Anthropic 可能自建\"雇人\"能力。",
    "**流量结构性迁移：**AI 答案引擎压缩自然流量，管理层预计流量下滑延续至 2027。",
    "**地缘与治理：**以色列地缘风险；首席业务官离职；回购停滞。",
    "**SBC 稀释**（Q3'26 占营收 7.4%）。",
    "**模型假设：**FCFF 利润率、Q4 FCF 约 $5M、情景权重 40/45/15 均为分析人假设；份额与年化 GMV/GSV 为估算；一致预期为第三方数据。",
]: numbered(t)
para("**跟踪指标：**活跃买家降幅是否收窄（26Q3 -25.8%）；每买家支出与 $1K+ 项目占比（16%）；AI 来源 GMV 绝对值；take rate；2027 指引（随 Q4 财报，约 2027-02-17）；Upwork 26Q3（11/2 盘后）；Fiverr MCP 是否上线下单/付款工具。")

# ================= 6. Review =================
h1("六、复核过程说明")
table([
    ["环节", "内容", "结果"],
    ["财报解读", "基于 Q3'26 新闻稿、股东信、电话会、Zacks、yfinance", "超预期但基本面恶化，整体偏负面"],
    ["产业研究", "v1 → GoogleAI R1（有条件同意，4 项必改 + 5 项细节）→ v2 → GoogleAI R2（同意，无必改）", "定稿（report_final）"],
    ["估值分析", "DCF / 可比 / 反向 DCF，Python 模型输出 model_out.json", "$9.5–15，中值约 $12.5"],
    ["GoogleAI 交叉复核（三份材料）", "agent 用 code_execution 重算估值，离线复算一致；核对资产负债表、Upwork/Fiverr MCP 官方页面、MTurk 关闭", "**三项结论全部同意，无必须修改项**"],
], widths=[3.6, 8.6, 4.4], size=9)
para("**本报告已落实的 GoogleAI 细节修改：**①Fiverr MCP 改引官方 https://www.fiverr.com/mcp（截至 11/2 仅只读工具 Find_freelancers），替代第三方 SynapticRelay 的\"截至 9/26\"说法；②Upwork MCP 补充官方出处并注明 offer 需用户在 upwork.com 付款后才发出；③注明两张资产负债表均无可转债、Q4'25 到期清偿；④统一股价口径，$8.80 与 $8.675 均为 11/2 盘中价。")
para("**复核中被纠正、未写入本报告的说法：**agent 称 Fiverr MCP 含\"Gig 搜索、知识图谱检索、元数据提取\"（与官方页面不符）；可转债\"2020 年发行 $460M\"（未核实）；\"硬净现金每股 $6.18\"（把应计负债全额扣除，方法不当）。")

# ================= 7. Sources =================
h1("七、来源清单（访问日期均为 2026-11-02）")
srcs = [
    ("[PR] Fiverr Q3'26 新闻稿（GlobeNewswire，2026-10-29）", "https://www.globenewswire.com/news-release/2026/10/29/3390901/0/en/fiverr-announces-third-quarter-2026-results.html"),
    ("[SL] Fiverr Q3'26 股东信", "https://investors.fiverr.com/static-files/085ab4bb-4a23-42c8-b78c-3e0ecb3800e5"),
    ("Fiverr Q3'26 电话会讲稿（IR）", "https://investors.fiverr.com/static-files/34a35f89-1ef1-479f-b2b8-fa954b097a49"),
    ("[TR] 电话会实录（Motley Fool）", "https://www.fool.com/earnings/call-transcripts/2026/10/30/fiverr-fvrr-q3-2026-earnings-call-transcript/"),
    ("[TR] 电话会实录（TradingKey）", "https://www.tradingkey.com/news/transcripts/262258900-"),
    ("Fiverr FY25 新闻稿（2026-02-18）", "https://www.globenewswire.com/news-release/2026/02/18/3239912/0/en/fiverr-announces-fourth-quarter-and-full-year-2025-results.html"),
    ("[ZK] Zacks/Yahoo Finance 一致预期对比", "https://finance.yahoo.com/markets/stocks/articles/fiverr-fvrr-q3-earnings-taking-143001872.html"),
    ("Fiverr MCP 官方页面", "https://www.fiverr.com/mcp"),
    ("[LLM] Fiverr llms.txt", "https://www.fiverr.com/llms.txt"),
    ("Upwork MCP 官方页面", "https://www.upwork.com/ai/mcp"),
    ("Upwork 帮助中心：How to use Upwork with AI agents through MCP", "https://support.upwork.com/hc/en-us/articles/55446516654611-How-to-use-Upwork-with-AI-agents-through-MCP"),
    ("[UPQ] Upwork 26Q2 新闻稿（SEC 8-K，2026-08-10）", "https://www.sec.gov/Archives/edgar/data/1627475/000162747526000046/upwork2q26-pressrelease.htm"),
    ("[UPN] Upwork Now 新闻稿（2026-11-02）", "https://www.globenewswire.com/news-release/2026/11/02/3393672/0/en/upwork-introduces-upwork-now-to-help-clients-hire-experts-in-minutes.html"),
    ("Investing.com：Upwork 财报前瞻（2026-11-02）", "https://www.investing.com/news/earnings/upwork-faces-earnings-test-as-ai-reshapes-freelance-work-93CH-4992115"),
    ("SIA：人才平台全球毛支出（2026-08-13）", "https://www.staffingindustry.com/news/global-daily-news/talent-platform-global-gross-spend-falls-2"),
    ("SIA：全球零工经济 $3.7T", "https://www.staffingindustry.com/news/global-daily-news/global-gig-economy-reaches-37-trillion"),
    ("Freelancer Ltd ASX 1H26 公告（2026-07-28）", "https://announcements.asx.com.au/asxpdf/20260728/pdf/0723ml7wxlkc9l.pdf"),
    ("Reuters：Surge AI 融资（2025-07-01）", "https://www.reuters.com/business/scale-ais-bigger-rival-surge-ai-seeks-up-1-billion-capital-raise-sources-say-2025-07-01/"),
    ("Toptal 官网", "https://www.toptal.com/"),
    ("Contra 0 佣金页面", "https://contra.com/commission-free"),
    ("Contra MCP 页面", "https://contra.com/features/mcp"),
    ("[RAH] RentAHuman 文档", "https://rentahuman.ai/docs"),
    ("[RAH] npm rentahuman-mcp", "https://www.npmjs.com/package/rentahuman-mcp"),
    ("TaskRabbit Claude Connector", "https://claude.com/connectors/taskrabbit"),
    ("TaskRabbit 博客：TaskRabbit is now available in Claude", "https://www.taskrabbit.com/blog/taskrabbit-is-now-available-in-claude/"),
    ("Amazon MTurk 帮助页（关闭公告）", "https://www.mturk.com/help"),
    ("[SR] SynapticRelay：Which freelance marketplaces can your AI agent use?（2026-09-26，已由官方出处替代）", "https://synapticrelay.com/en/guides/ai-agent-freelance-marketplaces"),
    ("[DAM] Damodaran 隐含 ERP", "https://pages.stern.nyu.edu/~adamodar/New%5FHome%5FPage/home.htm"),
]
for label, url in srcs:
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(1)
    set_font(p.add_run(label + "："), size=8.5); add_hyperlink(p, url, size=8.5)
for t in ["[YF] yfinance（Python，2026-11-02 拉取；估值数据为美东 15:15）：财报日期、EPS 意外、一致预期、股价、^TNX、beta、同业倍数。",
          "Upwork 官方 agent plugin SKILL.md（github.com/upwork/upwork-agent-plugin）：manage_offers create_draft 返回 finalize_url（GoogleAI 复核引用）。",
          "内部材料：earnings_report.md、report_final.md、fvrr_valuation.md、model_out.json、googleai_review_full_r1.md（/workspace/fvrr/）。"]:
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(1); set_font(p.add_run(t), size=8.5)

# footer page numbers
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run(); set_font(r, size=8)
for tag, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
    if tag:
        e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), tag)
    else:
        e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt
    r._r.append(e)

doc.save(os.environ.get('OUT','/workspace/fvrr/FVRR_final_report.docx'))
print("ok")
