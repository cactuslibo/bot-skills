import json,os,collections
rows=json.load(open('rows.json'))
gai=open('../gai/gai_section.md').read() if os.path.exists('../gai/gai_section.md') else "**GoogleAI 核验待做**：调用进行中/未返回，原因见下。"
npdf=sum(r['pdf']=='✓' for r in rows)
grades=collections.Counter(r['grade'] for r in rows)
bn={'1':'分支1 阶段时长','2':'分支2 成功率/转化概率','3':'分支3 研发成本与生产率','4':'分支4 AI 对时间/成本/成功率的影响','5':'分支5 价值链：外包、利润/价值分配、公共与风投资金'}
def tbl(rs):
    o=["| ID | 级别 | 作者 | 年 | 题名 | 期刊/来源 | DOI/链接 | Crossref | PDF |","|---|---|---|---|---|---|---|---|---|"]
    for r in rs: o.append(f"| {r['key']} | {r['grade']} | {r['authors']} | {r['year']} | {r['title']} | {r['venue']} | {r['doi']} | {r['cr']} | {r['pdf']} |")
    return "\n".join(o)
order={'A1':0,'A2':1,'A3':2,'B1':3,'B2':4,'B3':5,'C2':6}
bt="\n\n".join(f"### {bn[b]}（{sum(1 for r in rows if r['branch']==b)} 篇）\n\n"+tbl(sorted([r for r in rows if r['branch']==b],key=lambda r:(order[r['grade']],r['key']))) for b in '12345')
gm="| 用途\\可信度 | 1 | 2 | 3 | 合计 |\n|---|---|---|---|---|\n"
for u in 'ABC':
    gm+=f"| {u} | "+" | ".join(str(grades.get(u+l,0)) for l in '123')+f" | {sum(grades.get(u+l,0) for l in '123')} |\n"
gm+=f"| 合计 | "+" | ".join(str(sum(grades.get(u+l,0) for u in 'ABC')) for l in '123')+f" | {len(rows)} |"
bg="| 分支 | A | B | C | 合计 |\n|---|---|---|---|---|\n"+"\n".join(f"| {bn[b]} | {sum(1 for r in rows if r['branch']==b and r['grade'][0]=='A')} | {sum(1 for r in rows if r['branch']==b and r['grade'][0]=='B')} | {sum(1 for r in rows if r['branch']==b and r['grade'][0]=='C')} | {sum(1 for r in rows if r['branch']==b)} |" for b in '12345')
t=open('lit_template.md').read()
t=t.replace('{{GRADE_MATRIX}}',gm).replace('{{BRANCH_GRADE}}',bg).replace('{{TABLES}}',bt).replace('{{GAI}}',gai).replace('{{NPDF}}',str(npdf)).replace('{{NROWS}}',str(len(rows))).replace('{{NSCI}}',str(sum(1 for r in rows if r['pdf']=='✗' and r['grade'][0] in 'AB'))).replace('{{ABC}}','A %d / B %d / C %d'%tuple(sum(1 for r in rows if r['grade'][0]==u) for u in 'ABC'))
open('../lit.md','w').write(t)
print('ok',len(t))
