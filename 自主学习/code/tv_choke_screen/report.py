import pandas as pd,numpy as np,markdown
R=pd.read_csv('results.csv'); R=R[R.ticker!='WSO.B']  # WSO.B 与 WSO 同一 CIK
f=lambda v,p=1: '—' if pd.isna(v) else f"{v*100:.{p}f}%"
def row(r):
  return f"| {r.ticker} | {r['name']} | {int(r.sic2)} ({int(r.peer_n)}家) | {f(r.gm_trough)}（{int(r.trough_year)}） | P{r.gm_trough_pct*100:.0f} | {int(r.yr_lo)}–{int(r.yr_hi)} | {r.up_dgm_mean*100:+.2f} / {r.up_dom_mean*100:+.2f} | {f(r.cl_rev)}（{'' if pd.isna(r.cl_year) else int(r.cl_year)}） | {'—' if pd.isna(r.book_to_bill) else f'{r.book_to_bill:.2f}（RPO {r.rpo_yoy*100:+.0f}%，{int(r.rpo_year)}）'} | {r.cap_terms if isinstance(r.cap_terms,str) else '否'} |"
H="| 代码 | 公司 | SIC2(同业数) | 低谷GM（年） | 同业分位 | GM年份 | 上行年ΔGM/ΔOM 均值(pp) | 合同负债/收入（年） | 订单出货比≈(收入+ΔRPO)/收入 | 自家10-K产能/长约用语 |\n|"+"---|"*10
A=R[R.s3=='通过'].sort_values('gm_trough_pct',ascending=False); W=R[R.s3=='数据不足'].sort_values('gm_trough_pct',ascending=False); N=R[R.s3=='未通过']
n=len(R); s1=R.s1.value_counts()
cov_gm=(R.s1.isin(['通过','未通过'])).sum()
md=f"""# 卡脖子三段式指标组合：TradingView 美股池筛选报告
生成日期：2026-11-01（美东）。数据：SEC EDGAR companyfacts XBRL + EDGAR 全文检索（均为 **A 级 SEC 原始披露**；本报告未使用 B/C 级来源）。

> **重要局限（先读）**：该组合在独立标签上的 AUC 仅约 0.70（宽标签 95% CI [0.44, 0.93]，含 0.5，不显著）；各段阈值均未经有效回测。下面的名单**只是候选，不是结论**。周期顶部年份会出现利润率假象（上行期毛利/营业利润率扩张可能只是景气顶部）。

## 1. 股票池与覆盖
- CSV 按记录解析共 876 条（`wc -l` 为 929 行，差异来自带引号的多行字段）：`source=screener_mcap>10B` 的普通股 **812 只**纳入；`sector_theme_etf` 的 **64 只 ETF 跳过**。文件中**没有 A 股**记录（若原本应包含 A 股，同样跳过，SEC 无其数据）。
- 812 只全部在 SEC 找到 CIK（WSO/WSO.B 等同一公司多类股按一家处理，去重后 {n} 只）。
- 第一段可计算（≥8 年 GAAP 毛利率且含 2009/2019/2023 任一下行年，同业≥5 家）：**{cov_gm} 只（{cov_gm/n*100:.0f}%）**。
- 不适用（金融/保险/REIT 等 SIC 60–67，或 XBRL 无 GrossProfit/营业成本）：{s1.get('不适用(无毛利率/金融地产)',0)}；毛利率不足 8 年：{s1.get('不足8年',0)}；SIC 两位码同业不足 5 家：{s1.get('同业不足5家',0)}。
- 第一段通过 {s1.get('通过',0)}，未通过 {s1.get('未通过',0)}；第二段通过 {(R.s2=='通过').sum()}；第三段：全过 **{len(A)}**，数据不足（观察名单）**{len(W)}**，数据齐但未过 {len(N)}。
- 第三段数据覆盖（第二段通过的 {(R.s2=='通过').sum()} 家）：合同负债/预收 {(R[R.s2=='通过'].sig_cl!='缺数据').sum()} 家有数；RPO 连续两年 {(R[R.s2=='通过'].sig_bb!='缺数据').sum()} 家有数。

## 2. 方法（按 final.md / REPORT_Taz.md 的三段结构，按本次任务指令设定参数）
1. **下行期护城**：年度 GAAP 毛利率 = GrossProfit/收入（缺 GrossProfit 时用 收入−营业成本）。年度口径取 10-K/20-F 中 350–380 天的期间值，重述取最新申报。要求 ≥8 年且含下行年（2009、2019、2023；XBRL 从约 2009 年起，2001 年无法覆盖）。取窗口最低毛利率，在**同 SIC 两位码**内的可计算公司中算分位，≥P50 通过（注：final.md 原设计为 SIC4→SIC3，这里按任务指令用 SIC2）。
2. **上行期攫取**：收入同比上升年份中，毛利率同比变化均值 > 0，且营业利润率同比变化均值 > 毛利率变化均值。
3. **领先信号（任意两条）**：(a) 最新年 合同负债/客户预付（ContractWithCustomerLiability(Current)、CustomerAdvances*、DeferredRevenueCurrent）÷ 收入 ≥ 10%；(b) RevenueRemainingPerformanceObligation 同比增长且 订单出货比代理值 (收入+ΔRPO)/收入 ≥ 1.05；(c) 公司自身 2024-01 以来的 10-K 出现 “sold out / take-or-pay / long-term supply agreement / capacity reservation / fully booked”；(d) 客户 10-K 披露 sole/single source。阈值 10%/1.05 为本次预设，未回测。
   - **(d) 计为“缺数据”**：EDGAR 全文检索只能判断“sole source”与公司名出现在同一份 10-K，不能确认是客户把它列为单一来源（例如 Salesforce 命中 102 家、S&P Global 94 家，明显是噪声）。原始命中数保留在 results.csv 的 ss_n_filers/ss_filers 列，仅供人工复核，不计分。
   - (c) 只是关键词命中，未经人工阅读上下文。

## 3. 三段全过名单（{len(A)} 只，按低谷毛利率同业分位排序）
{H}
""" + "\n".join(row(r) for _,r in A.iterrows()) + f"""

**解读提醒**：全过名单以软件/SaaS（SIC 73）和网络/存储设备为主，原因是其合同负债（递延收入）和 RPO 天然偏高——final.md 已指出合同负债/收入可能是**行业结构混淆**，不代表“产能被抢”。较接近实体卡脖子含义的是 AVGO（RPO +62%，订单出货比 1.20）、RTX（订单出货比 1.56，但其毛利率 XBRL 只到 2017 年）、CW、NTAP、P(Everpure)。

## 4. 观察名单：前两段通过、第三段数据不足（{len(W)} 只）
多数是因为没有披露 RPO（无法算订单出货比）。其中已命中一条信号的值得优先人工补数据：
{H}
""" + "\n".join(row(r) for _,r in W.iterrows()) + f"""

## 5. 前两段通过、第三段数据齐但未过（{len(N)} 只）
{', '.join(f"{r.ticker}（合同负债/收入 {f(r.cl_rev)}，订单出货比 {r.book_to_bill:.2f}）" for _,r in N.iterrows())}。
值得注意：NVDA、LRCX 第三段未过——NVDA 合同负债/收入仅 0.6%、订单出货比 1.00；LRCX 2026 财年 RPO −9%。KLAC、AMAT、ASML、TSM 未进入前两段名单，见 results.csv 中各自 s1/s2 字段。

## 6. 局限
- 组合 AUC≈0.70 且不显著；阈值（P50、10%、1.05）均未经有效验证。结果只是候选。
- 周期顶部会出现利润率假象：上行年 ΔGM/ΔOM 为正，可能只是景气高点；低谷年也可能含重组费用和存货减值（GAAP 口径，未做调整）。
- SIC 两位码过粗（如 35 同时包含电脑、机械、半导体设备），同业分位会被行业结构左右；部分组只有 5–9 家。
- XBRL 标签缺失或中断（如 RTX、INTU、SNA、HAL 的毛利率只到 2017 年）会让窗口偏旧；IFRS 外国发行人按报告币种计算比率。
- 第三段 (d) 无法可靠自动获取；(c) 只是关键词命中。没有使用任何非 SEC 来源，因此不存在 B/C 级数据。

## 7. 文件
results.csv（全部 811 家公司的逐段字段与原始数值）、panel_tv.csv（年度面板）、fts_cache.json（全文检索原始命中）、脚本 fetch.py / stage12.py / stage3.py / final.py / report.py。
"""
open('report.md','w').write(md)
css="body{font-family:'Noto Sans CJK SC','WenQuanYi Micro Hei',sans-serif;font-size:10px;margin:18px}table{border-collapse:collapse;font-size:8.5px}td,th{border:1px solid #999;padding:2px 4px}blockquote{background:#fff3cd;padding:6px;margin:0}"
open('report.html','w').write(f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>"+markdown.markdown(md,extensions=['tables'])+"</body></html>")
