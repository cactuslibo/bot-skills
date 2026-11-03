import json,os
C=json.load(open("cands.json"));I=json.load(open("included.json"));F=json.load(open("formal_doi.json"))
F.update({"Gof13":"10.1016/j.jfineco.2021.05.054","Irv13":"10.2308/accr-51246"})
pdfdir="/workspace/bottleneck_metric/lit_pdfs"
def pdf(k):
    for f in sorted(os.listdir(pdfdir)):
        if f.startswith(k+".") or f.startswith(k+"_"): return "有（"+f+"）" if "supplement" not in f else "仅补充材料（"+f+"）"
    return "无（列入 scihub_needed.md）"
def doi(k):
    d=F.get(k) or C[k]["doi"]
    return f"https://doi.org/{d}" if d else (C[k]["link"] or "无DOI")
BR={"a":"(a)议价能力/利润率/加成率","b":"(b)价值链利润分配","c":"(c)网络中心性/上游度","d":"(d)上游定价权/冲击传播","e":"(e)超额利润持续性"}
OV={"Car16":("Supply Chain Disruptions: Evidence from the Great East Japan Earthquake","2021（QJE 136(2):1255–1321；Crossref 在线 2020）"),"Irv13":("Customer-Base Concentration, Profitability, and the Relationship Life Cycle","2016（TAR 91(3):883–906）"),"Rav20b":("Testing the Production Approach to Markup Estimation","2023（REStud 90(5):2592–2611）"),"Pre17":("The smile curve at the firm level: Where value is added along supply chains","2018（Econ. Letters 164:38–42）"),"Run20":("Measuring the input rank in global supply networks","2023（World Economy 46(10):3081–3115）"),"Ell20":("Supply Network Formation and Fragility","2022（AER 112(8):2701–2747）"),"Bon20":("Some unpleasant markup arithmetic: Production function elasticities and their estimation from production data","2021（JME 121）"),"Dra08":("A Larger Slice or a Larger Pie? An Empirical Investigation of Bargaining Power in the Distribution Channel","2010（Mark. Sci. 29(1):57–74）"),"Ace11":("The Network Origins of Aggregate Fluctuations","2012（Econometrica 80(5):1977–2016）"),"Alv00":("Markups and Cost Pass-through Along the Supply Chain","2025（NBER WP 34110）"),"Agr23":("Inventory Productivity and Stock Returns in Manufacturing Networks","2024（MSOM）"),"Gof20":("Production Networks and Stock Returns: The Role of Vertical Creative Destruction","2020（RFS）"),"War96":("Industry Differences in the Persistence of Firm-Specific Returns","1996（AER 86(5):1253–1265，JSTOR 2117773，无 Crossref DOI）"),"Ben01":("'Oscillate Wildly': asymmetries and persistence in company-level profitability","2001（Bank of England 工作论文）")}
KEY=["Shi12","Gos09","Pat12b","Cow88","Gal83","Dhy22","Gof13","Bar16","Loe20","Dic12"]
core=open("core_sections.md").read()
rest=["| ID | 题名 | 第一作者等 | 年份 | DOI/链接 | 分支 | 对应指标 | 核心结论（据摘要，除注明外） | 分级 | 本地PDF |","|---|---|---|---|---|---|---|---|---|---|"]
for k,(br,u,c,ind,note) in I.items():
    if k in KEY: continue
    d=C[k]; au=d["authors"].split(",")[0]+(" 等" if "," in d["authors"] else "")
    yr=OV.get(k,(d["title"],d["year"]));rest.append(f"| {k} | {yr[0]} | {au} | {yr[1]} | {doi(k)} | {BR[br]} | {ind} | {note} | {u}{c} | {pdf(k)} |")
gai=open("gai_section.md").read() if os.path.exists("gai_section.md") else "（GoogleAI 核验进行中，见下文状态）"
out=core.replace("{{REST}}","\n".join(rest)).replace("{{GAI}}",gai)
for k in KEY: out=out.replace("{{PDF:"+k+"}}",pdf(k)).replace("{{DOI:"+k+"}}",doi(k))
open("/workspace/bottleneck_metric/lit_from_wenxian.md","w").write(out)
print("ok",len(out))
