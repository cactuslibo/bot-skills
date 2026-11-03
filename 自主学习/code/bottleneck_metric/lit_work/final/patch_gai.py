import json
m=json.load(open('master.json'))
P={
"Mon13":dict(title="Competitive Intensity and Its Two-Sided Effect on the Boundaries of Firm Performance（工作论文原题 Quantifying the negative and positive effects of competitive intensity on firm performance）",year=2018,venue="Management Science 64(6):2716–2733",doi="10.1287/mnsc.2017.2737",xadd="GoogleAI 指出正式版，Crossref 已确认（题名、作者、卷页一致）"),
"Cha15b":dict(xadd="GoogleAI 指出可能的正式版：J. Management Accounting Research 33(3):9–27，10.2308/jmar-17-070，题名改为“Suppliers' Product Market Competition, Customer Concentration, and Cost Structure”。Crossref 确认该 DOI 存在、作者相同，但题名不同，未逐字核对是否同一研究"),
"She18c":dict(xadd="GoogleAI 称只有 HKUST 工作论文、无 DOI；Crossref 检到同作者 Management Science 2026“Dynamic Collusion, Vertical Competition, and Systematic Risk”（10.1287/mnsc.2024.04715），可能是正式版，题名不同，未核实"),
"Sch84":dict(xadd="GoogleAI 称正式卷期为 AER 75(3), 1985；它给的 DOI 10.2307/1814804 在 Crossref 返回 404，不采纳；年份未独立核实"),
"Mue86b":dict(venue="Cambridge University Press（专著）",xadd="GoogleAI 指出为专著，Crossref 确认 10.1017/cbo9780511664731"),
"Hal18c":dict(venue="NBER Working Paper 24574",xadd="Crossref 确认"),
"Loe18b":dict(venue="NBER Working Paper 24768",xadd="Crossref 确认"),
}
for k,p in P.items():
    v=m[k]; x=p.pop('xadd')
    v.update(p); v['xnote']=(v.get('xnote')+'；' if v.get('xnote') else '')+x
json.dump(m,open('master.json','w'),ensure_ascii=False,indent=1)
print('patched',len(P))
