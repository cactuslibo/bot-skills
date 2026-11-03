import re,os,json
from new_entries import E
v1=open("lit_v1.md").read()
scihub={"B04","B14","B18","B20","B24","B26","B30","B32","B33","B36","B37","B38","B39","B41","B43","B45"}
def pdfmark(i):
    if not os.path.exists(f"pdfs/{i}.pdf"): return "无"
    return "有（SciHub）" if i in scihub else "有"
# old tables: take sections 1-3 from v1 and add PDF column
sec=v1.split("## 方向 (1)")[1].split("## 方向 (4)")[0]
out=[]
for l in ("## 方向 (1)"+sec).splitlines():
    m=re.match(r"\| (B\d\d) \|",l)
    if m: l=l+f" {pdfmark(m.group(1))} |"
    elif l.startswith("| ID |"): l=l+" 本地 PDF |"
    elif l.startswith("|---|"): l=l+"---|"
    out.append(l)
old_tables="\n".join(out)
# B18 note
old_tables=old_tables.replace("摘要不可得；短读长市场挤入多家新技术 | B2 |","摘要不可得；短读长市场挤入多家新技术（SciHub 所得 PDF 首页标题为“Navigating an increasingly crowded sequencing landscape”，应为同一篇的版面标题，待核） | B2 |")
cro=["## 方向 (4) CRO 行业集中度、并购、新进入者与利润率（第 2 轮新增，B46–B87）","",
"来源：Undermind 深度检索 4、5（见 PRISMA-S）。核心结论据摘要；标“全文 p.x”的为本次读过 PDF 的页码（PDF 页序）。","",
"| ID | 题目 | 作者 | 年份 | DOI / 链接 | 子主题 | 核心结论 | 级 | 本地 PDF | 备注 |","|---|---|---|---|---|---|---|---|---|---|"]
extra={"B58":"；全文 p.1：“the CRO industry was born to cut costs, so its profit margin is low”，并引述“专业环节分不到足够的产品价值，所以利润率往往很小”",
"B46":"；全文 p.19：规模经济意味着未来可能有更多并购，很小的公司效率高说明存在利基优势",
"B53":"；全文 p.12（PDF 页序）：CRO 基础设施使 IP 型初创企业（药企侧）“进入壁垒低”——说的是 CRO 降低了**新药企**的进入门槛，不是 CRO 自身门槛低",
"B50":"；全文 p.14：客户更换 CRO 时承担“不小的转换成本”（知识未编码，靠监查员口耳相传）",
"B67":"；全文 p.2（摘要）"}
for e in E:
    i,k,t,a,y,d,sub,c,g,n=e
    link=d if d.startswith("无") else f"https://doi.org/{d.split('（')[0]}"+("（疑似错误归属）" if "疑似" in d else "")
    cro.append(f"| {i} | {t} | {a} | {y} | {link} | {sub} | {c}{extra.get(i,'')} | {g} | {pdfmark(i)} | {n} |")
open("_old_tables.md","w").write(old_tables); open("_cro_table.md","w").write("\n".join(cro))
print(old_tables.count("| 有"), "\n".join(cro).count("| 有 |"))
