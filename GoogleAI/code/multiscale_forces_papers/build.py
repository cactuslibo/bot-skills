import json,os
exec(open('ann.py').read())
m=json.load(open('meta.json')); R=json.load(open('rounds.json')); R['R0']+=['Lev21','Lev14']
rk={k:r for r,ks in R.items() for k in ks}
isAB=lambda k:A[k][2][0] in 'AB'
cum=0; sat=[]
for r in ['R0','R1','R2','R3']:
    n=sum(isAB(k) for k in R[r]); rate=None if cum==0 else n/cum
    sat.append((r,len(R[r]),n,cum,rate)); cum+=n
rows=[];miss=[]
for i,(k,v) in enumerate(m.items(),1):
    pdf=os.path.exists(f'pdfs/{k}.pdf')
    if not pdf: miss.append(v)
    cr=v['crossref'] if v['crossref']=='OK' else ('未核实' if v['crossref']=='NO_DOI' else '⚠'+v['crossref'].split(':')[0])
    rows.append(f"| {i} | {k} | {v['title'].replace('|','/')} | {v['authors']} | {v['year']}{'' if not v.get('cr_year') or str(v['cr_year'])==v['year'] else ' (CR:'+str(v['cr_year'])+')'} | {v['venue']} | {v['doi'] or '—'} | {A[k][0]} | {A[k][1]} | {A[k][2]} | {A[k][3]} | {'yes' if pdf else 'no'} | {cr} | {rk.get(k,'R0')} |")
g={};[g.__setitem__(A[k][2],g.get(A[k][2],0)+1) for k in m]
npdf=len(m)-len(miss)
sat_tbl="\n".join(f"| {r} | {t} | {n} | {c} | {'—' if x is None else f'{x*100:.1f}%'} | {'—' if x is None else ('<5%' if x<0.05 else '≥5%')} |" for r,t,n,c,x in sat)
L=open('list_template.md').read().format(N=len(m),NPDF=npdf,NMISS=len(miss),GRADES=", ".join(f"{k}:{v}" for k,v in sorted(g.items())),SAT=sat_tbl,ROWS="\n".join(rows))
open('list.md','w').write(L)
open('scihub_needed.md','w').write("# 未获取合法全文的文献（供 Taz 决定是否交 SciHub bot；GoogleAI 提示有版权风险）\n\n共 %d 篇。\n\n| Key | 标题 | DOI |\n|---|---|---|\n"%len(miss)+"\n".join(f"| {v['key']} | {v['title']} | {v['doi'] or '无DOI'} |" for v in miss)+"\n")
json.dump(dict(sat=sat,npdf=npdf,nmiss=len(miss),grades=g,n=len(m)),open('summary.json','w'),ensure_ascii=False)
print(sat,npdf,len(miss),g)
