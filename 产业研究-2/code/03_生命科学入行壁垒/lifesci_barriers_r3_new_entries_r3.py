import json
exec(open('grades_r3.py').read()); info=json.load(open('info_r3.json')); cr=json.load(open('crossref_r3.json'))
import os
DOI_FIX={"Coo08":"10.1215/s12280-008-9040-y","Kar07":"10.1111/j.1467-6451.2012.00473.x"}
NOTE={
"Kar07":"Undermind 收录为工作论文“Exclusionary Pricing and Rebates When Scale Matters”；Crossref 检到同作者正式版 J. Ind. Econ. 60(1), 2012，题名“Exclusionary Pricing When Scale Matters”",
"Whi89":"DOI 为 NBER WP 2995；正式版刊于 American Economic Review（Undermind 记 pp. 837-859），Crossref 无该期刊 DOI",
"Car98":"Undermind 记 1998 工作论文；DOI 解析到 RAND J. Econ. 2002 正式版",
"Far86":"AER 1986，Crossref 无 DOI（JSTOR 期刊）","Agh87":"AER 1987，Crossref 无 DOI（JSTOR 期刊）",
"Coo08":"Undermind 给的 10.1007 前缀 DOI 经 Crossref 重定向为 10.1215/s12280-008-9040-y（EASTS 现属 Taylor & Francis）",
"Car10":"Crossref 年份 2009（在线）","Pea16":"Crossref 年份 2015（在线）","Lut10":"Crossref 年份 2009（在线）","Far03":"Crossref 年份 2000（工作论文登记年份异常，以期刊 2003 为准待核）",
"Bou07":"Crossref 检到同作者 SSRN 10.2139/ssrn.1290634（题名为 Reducing 而非 Modifying），未采纳为正式 DOI",
"Cha01":"Crossref 记录无题名，仅作者一致",
"Tha10b":"DataCite DOI（Rutgers 博士论文），已用 DataCite API 核实",
"Jor19":"法文期刊，Crossref 题名为法文“Actualités du séquençage d’ADN”",
"Dix80":"Crossref：Economic Journal 1980；本地 PDF 为 Warwick 工作论文版（扫描件，已目视核对首页）",
}
DIR={"1":"工具","2":"测序","3":"锁定/IO理论","4":"CRO"}
rows=[]; n=88
for k,(d,u,c,txt,st) in G.items():
    i=info[k]; doi=DOI_FIX.get(k) or i['doi']
    link=f"https://doi.org/{doi}" if doi else (i['link'] or '')
    pdf="有" if os.path.exists(f"dl/{k}.pdf") else "无"
    rows.append(dict(id=f"B{n}",key=k,title=i['title'],authors=i['authors'],year=i['year'],venue=i['venue'],doi=doi,link=link,dir=DIR[d],use=u,cred=c,grade=f"{u}{c}",claim=txt,stage=st,pdf=pdf,note=NOTE.get(k,""),xref=cr[k].get('mode') and (cr[k].get('sim',0)>=0.9 or k in ('Jor19','Cha01','Kar07','Coo08'))))
    n+=1
json.dump(rows,open('new_rows.json','w'),ensure_ascii=False,indent=1)
with open('table_for_gai.txt','w') as f:
    for r in rows: f.write(f"{r['id']} | {r['title']} | {r['authors']} | {r['year']} | {r['venue']} | {r['doi'] or '无DOI'} | {r['grade']} | {r['claim']}\n")
print(len(rows),rows[-1]['id'])
