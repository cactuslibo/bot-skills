import json,os,re
rows=json.load(open('new_rows.json'))
old=open('../lit_v2.md').read()
from collections import Counter
cA=Counter(r['use'] for r in rows); cg=Counter(r['grade'] for r in rows)
B=lambda k:[r['id'] for r in rows if r['key']==k][0]
def ids(*ks): return ", ".join(B(k) for k in ks)
# ---------- header ----------
old=old.replace("# 生命科学工具 / 测序 / CRO 行业进入壁垒文献综述（第 2 版，2026-11-01 美东时间）","# 生命科学工具 / 测序 / CRO 行业进入壁垒文献综述（第 3 版，2026-11-01 美东时间）")
ver=f"""**第 3 版说明（2026-11-01 约 23:10 美东）**：在第 2 版 87 篇（B01–B87，备份为 `lit_v2.md`）基础上，补做了 Wohlin 双向滚雪球 2 轮、IO 理论 berrypicking（限制性定价 / 进入阻止 / 搭售捆绑 / 售后市场）和 CRO 定向补检（HHI、FSP），新增 **55 篇（B88–B142）**，合计 **142 篇**。新增分级：A {cA['A']}、B {cA['B']}、C {cA['C']}。仍**未饱和**，因总篇数预算（≤150）按兜底条款停止。工作文件在 `r3/`。B30 的 DOI 保持第 2 版更正值，未改动。下面第 2 版说明中“滚雪球未执行”的部分已由本版补做。

"""
old=old.replace("**版本说明**：第 1 版",ver+"**版本说明（第 2 版）**：第 1 版",1)
old=old.replace("这是证据缺口（相关 IO 理论分支本轮未检索，见“疑似空白/未检索分支”）。**","这是证据缺口。第 3 版补检了 IO 理论分支：限制性定价、进入阻止、搭售/捆绑和售后市场理论都有成熟文献，但**都是一般理论或其他行业的实证**，仍没有一篇把它们用到这三个行业上（经 Undermind + OpenAlex 3 组同义词复核，定为疑似空白，见第 3 版“疑似空白”）。**")
new_sum=f"""### 5. 第 3 版新增证据（B88–B142）怎样改变判断
- **理论上，“在位者靠低价阻止进入”并不是自然结论**：有转换成本时，受进入威胁的在位者可能比无威胁时定价更低，也可能更高 [{ids('Kle87b')}]；限制性定价要成立，需要信息不对称下的信号机制 [{ids('Mil82')}]；更常见、更可信的阻止进入手段是事前产能投资 [{ids('Dix80')}]、长期排他合同 [{ids('Agh87')}]、抬高对手成本 [{ids('Sal87')}]、序贯进入阻止 [{ids('Ber84')}]。所以论点里“龙头靠低利润阻止进入”在理论上只是多种可能之一，**而且在这三个行业中从未被实证检验**。
- **捆绑、搭售与售后市场是工具/测序行业更贴切的机制**：捆绑是有效的进入壁垒，无需每个产品都低价 [{ids('Nal04','Cho06','Gre20d')}]；搭售可保持并扩展垄断 [{ids('Whi89','Car98','Car12b')}]；售后市场势力的反垄断分析 [{ids('Car10','Far03')}]；“必备品”供应商的排斥 [{ids('Ide24')}]。这与第 2 版的“耗材专有 + 装机基础”结论一致，并补上了理论基础。
- **装机基础优势有设备采购的实证**：联邦计算机采购中机构更倾向在位供应商 [{ids('Gre93')}]，网络设备买方同样如此 [{ids('For01')}]，微机市场有装机基础效应 [{ids('Kos99')}]；医疗器械买方层面存在跨品类的使用和合同溢出 [{ids('Gre20c')}]。这些都是**相邻行业**的证据，不是直接对工具/测序的检验。
- **规模经济**：基因组学与高通量筛选让药企在实验中获得规模经济 [{ids('Nig00')}]，支持“工具技术带来规模型壁垒”。
- **测序**：Illumina 收购 PacBio 的评论 [{ids('Jor19')}]，与 B16 等结论一致。
- **CRO**：合规成本（数据监查）推高试验成本 [{ids('Pro11b')}]；CRO 空间分布研究 [{ids('Ban17')}]；NEJM、英国调查与价值链研究描述了 CRO 接管研发职能和外包增长 [{ids('Shu07','How08','Haa09')}]。**CRO 行业 HHI/利润率/进入率的计量研究和 FSP 专门实证，经补检仍找不到，定为疑似空白。**
- **总判断不变**：文献不支持“技术门槛低、龙头靠低利润率阻止进入”；补检后可以更明确地说，这一机制在理论上并不必然成立，在三个行业中也没有实证。

"""
old=old.replace("\n\n## 方向 (1) 生命科学工具行业进入壁垒",new_sum+"\n## 方向 (1) 生命科学工具行业进入壁垒",1)
# ---------- new table ----------
def tbl(rs):
    s="| ID | 题目 | 作者 | 年份 | 期刊/来源 | 链接 | 子方向 | 核心结论 | 级 | 来源轮次 | 本地 PDF | 备注 |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    for r in rs: s+=f"| {r['id']} | {r['title']} | {r['authors']} | {r['year']} | {r['venue']} | {r['link']} | {r['dir']} | {r['claim']} | {r['grade']} | {r['stage']} | {r['pdf']} | {r['note']} |\n"
    return s
sec="## 方向 (5) 第 3 版新增：滚雪球 R1–R2 与定向补检（B88–B142）\n\n来源轮次：R1/R2＝Wohlin 滚雪球轮次；G1/G2＝CRO 定向补检（HHI、FSP），不计入饱和率。Hae17（Haeussler & Rake 2017）是 B79 的另一版本，已合并，未新编号。\n\n"+tbl(rows)+"\n"
old=old.replace("## 步骤 0–8 执行记录","## 第 1–2 版方法记录（保留原文）\n\n## 步骤 0–8 执行记录",1)
old=old.replace("## 步骤 0–8 执行记录",sec+"## 步骤 0–8 执行记录",1) if False else old
old=old.replace("## 第 1–2 版方法记录（保留原文）",sec+"## 第 1–2 版方法记录（保留原文）",1)
gai=open('gai_section_r3.md').read() if os.path.exists('gai_section_r3.md') else "GoogleAI 核验待做：GoogleAI 任务已于 2026-11-01 23:02 美东提交（r3/run_gai_r3.py，日志 r3/gai_r3.log），写本版时尚未返回。"
pdfn=len([f for f in os.listdir('../pdfs') if f.endswith('.pdf')])
newpdf=[r['id'] for r in rows if r['pdf']=='有']
v3=open('v3_method.md').read().replace('{{GAI}}',gai).replace('{{PDFN}}',str(pdfn)).replace('{{NEWPDF}}','、'.join(newpdf))
old=old.replace("## 补记（2026-11-01 21:50 美东）",v3+"\n## 补记（2026-11-01 21:50 美东）")
open('../lit.md','w').write(old)
print('written',len(old),pdfn,len(newpdf))
