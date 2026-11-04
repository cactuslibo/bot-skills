import pandas as pd, base64, json, os
O = "/workspace/wyckoff/full_bt"
T = pd.read_csv(f"{O}/核心结果_全组合.csv"); B = pd.read_csv(f"{O}/分组结果_H20.csv")
D = pd.read_csv(f"{O}/当前清单_已完成筑底.csv"); P = pd.read_csv(f"{O}/当前清单_预备_等待Test.csv")
pb = open(f"{O}/pbo_dsr.txt").read().strip()
def pct(x): return f"{x*100:.2f}%"
def fmt(df):
    d = df.copy()
    for c in ("win", "mean", "med", "ex", "ex_med"): 
        if c in d: d[c] = d[c].map(pct)
    for c in ("t_ex", "t_ex_month", "pf"):
        if c in d: d[c] = d[c].map(lambda x: f"{x:.2f}")
    return d.rename(columns=dict(kind="类型", var="变体", arm="入场臂", H="持有期", exit="出场", n="交易数", win="胜率", mean="平均收益", med="中位收益",
                                 ex="平均超额(vs SPY)", ex_med="中位超额", t_ex="超额t值(逐笔)", t_ex_month="超额t值(按月聚类)", pf="盈亏比", dim="维度", key="分组"))
s = T[T.kind == "信号"]; best = s.sort_values("t_ex_month", ascending=False).iloc[0]
base = s[(s["var"] == "V1_base") & (s.arm == "E2") & (s.H == 20) & (s.exit.str.startswith("止损"))].iloc[0]
core = T[T.H == 20]
yr = B[(B["var"] == "V1_base") & (B.arm == "E2") & (B.exit == "无止损") & (B.dim == "year")]
cap = B[(B.dim == "capb") & (B.exit == "无止损")]
sec = B[(B["var"] == "V1_base") & (B.arm == "E2") & (B.exit == "无止损") & (B.dim == "sector")].sort_values("ex", ascending=False)
npos_sig = (s.ex > 0).sum()
head = (f"结论：没有超额收益。40 个信号组合（2 变体 × 2 入场臂 × 5 持有期 × 2 出场）中，相对 SPY 的平均超额收益为正的有 {npos_sig} 个；"
        f"表现最好的组合（{best['var']} {best.arm}，持有 {best.H} 日，{best.exit}）胜率 {pct(best.win)}，平均超额 {pct(best.ex)}，逐笔 t={best.t_ex:.2f}，按月聚类 t={best.t_ex_month:.2f}，统计上与 0 无差别；"
        f"规范基准组合（V1_base E2，20 日，止损@Spring低点）胜率仅 {pct(base.win)}，平均超额 {pct(base.ex)}（t={base.t_ex:.2f}）。"
        f"不设止损时胜率约 50–58%，与同股票随机日期入场几乎一样；止损放在 Spring 低点会把胜率压到 17–44% 且超额更差。")
lim = ["股票池是当前市值 >10 亿美元的存活股票，不含退市股，存在幸存者偏差和“按今天市值选股”的前视，绝对收益偏高；不过与同池随机日期对照比较时这一偏差大部分抵消。",
       "全部数据（2005-01-01 至 2026-11-03）都参与了回测，没有保留样本外；但本次没有调任何参数（沿用 v0 默认值和 V3 预设），结论又是否定的，过拟合风险不是主要问题。",
       f"PBO/DSR（40 个试验的月度超额序列，CSCV S=16）：{pb}。PBO 低只说明各组合排名相对稳定（基本都是 ≈0 或负），DSR≈0 表示最优组合的夏普在多重检验下不显著。",
       "逐笔 t 值忽略了交易之间的时间重叠和横截面相关，偏乐观；按入场月聚类的 t 值更可信。",
       "成本按每边 10bp，未计冲击成本；止损按盘中触及 min(开盘, 止损价) 成交，之后持现金至持有期结束，超额仍按同一窗口的 SPY 计算。",
       "数据处理：缺口 >10 个日历日处切断分段，每段单独跑信号；每段开头 60 日成交额中位数不足 $100 万的部分剔除（处理 SPAC 壳/前身公司，如 ARIS、CHRN、DCOM、ALVO）；段长 <150 根舍弃。信号日需收盘价 ≥$3 且 20 日平均成交额 ≥$100 万。同一标的同一变体×入场臂 28 个交易日去重。",
       "随机对照：每只股票、每个变体×入场臂，从该股可交易日中随机抽取与信号相同的笔数，重复 5 次，只做无止损。",
       "当前清单基于 V1_base 和各股票最后一个数据日（多数为 2026-11-03，部分截止到 10-30）；“已完成筑底”只表示结构成立，回测显示它没有统计上的优势，不构成买入建议。"]
cols = ["代码", "名称", "行业", "市值_亿美元", "Spring日期", "Spring低点_止损", "Test日期", "最新收盘", "距止损pct", "同时满足V3放量下破"]
md = [f"# 威科夫筑底法全样本回测总结（市值>10亿美股）\n\n生成日期：2026-11-03（美东时间）\n\n## 结论\n{head}\n",
      "## 核心表（持有 20 日，含随机对照）\n" + fmt(core).to_markdown(index=False),
      "\n## 全部 40 个信号组合（按“按月聚类 t 值”排序）\n" + fmt(s.sort_values("t_ex_month", ascending=False)).to_markdown(index=False),
      "\n## 按年份（V1_base E2，20 日，无止损）\n" + fmt(yr).to_markdown(index=False),
      "\n## 按市值档（20 日，无止损）\n" + fmt(cap).to_markdown(index=False),
      "\n## 按行业（V1_base E2，20 日，无止损）\n" + fmt(sec).to_markdown(index=False),
      f"\n## 当前已完成筑底（{len(D)} 只）\n" + D[cols].to_markdown(index=False),
      f"\n## 预备名单：已出现 Spring、等待 Test（{len(P)} 只）\n" + P[cols].to_markdown(index=False),
      "\n## 局限\n" + "\n".join("- " + x for x in lim),
      "\n## 文件\n- run_full.py（信号+交易）、analyze.py（统计）、current_list.py（清单）、make_report.py\n- 核心结果_全组合.csv、分组结果_H20.csv、pbo_dsr.txt、当前清单_*.csv、raw_results.pkl\n"]
open(f"{O}/结论.md", "w").write("\n".join(md))
st = 'style="border-collapse:collapse;font-size:12px" border="1" cellpadding="4"'
def h(df): return df.to_html(index=False, border=1).replace('border="1" class="dataframe"', st)
html = f"""<div style="font-family:Arial,'Microsoft YaHei',sans-serif;font-size:14px">
<p><b>{head}</b></p>
<h3>核心表（持有 20 日；超额 = 扣成本后收益 − SPY 同窗口收益）</h3>{h(fmt(core))}
<h3>其他持有期中表现最好的 5 个信号组合</h3>{h(fmt(s.sort_values('t_ex_month', ascending=False).head(5)))}
<h3>分组发现</h3><ul>
<li>按年份（V1_base E2，20 日，无止损）：22 年中超额为正的有 {(yr.ex>0).sum()} 年，正负交替，没有稳定的年份规律。</li>
<li>按市值档：{'；'.join(f"{r['var']} {r.arm} {r.key} 超额 {pct(r.ex)}（t={r.t_ex:.2f}）" for _, r in cap[cap['var']=='V1_base'].iterrows())}。各档都接近 0。</li>
<li>按行业（V1_base E2）：超额最高的是 {sec.iloc[0].key}（{pct(sec.iloc[0].ex)}，t={sec.iloc[0].t_ex:.2f}，n={sec.iloc[0].n}），最低的是 {sec.iloc[-1].key}（{pct(sec.iloc[-1].ex)}）；没有哪个行业在多重检验后显著。</li>
<li>V3（下破根放量 &gt;1.5×均量）没有比 V1 更好，反而略差。</li></ul>
<h3>当前已完成筑底：{len(D)} 只（最近 20 个交易日内出现缩量 Test，且之后未跌破 Spring 低点）</h3>{h(D[cols])}
<p>另有 {len(P)} 只处于“已出现 Spring、等待 Test”的预备状态，完整名单见附件 CSV。</p>
<h3>局限</h3><ul>{''.join('<li>'+x+'</li>' for x in lim)}</ul>
<p>文件路径：/workspace/wyckoff/full_bt/（结论.md、清单 CSV、代码）</p></div>"""
open(f"{O}/email.html", "w").write(html)
txt = head + "\n\n完整表格见 HTML 版本和附件。"
att = [dict(filename=f, mimeType="text/csv", content=base64.b64encode(open(f"{O}/{f}", "rb").read()).decode())
       for f in ("当前清单_已完成筑底.csv", "当前清单_预备_等待Test.csv", "核心结果_全组合.csv")]
json.dump(dict(to=os.environ.get("WYCKOFF_MAIL_TO", ""), subject="威科夫筑底法全样本回测总结（市值>10亿美股）", body=txt, htmlBody=html, attachments=att),
          open(f"{O}/email_args.json", "w"), ensure_ascii=False)
print(head); print(len(html))
