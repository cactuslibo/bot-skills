import json,sys
P={'10.1016':'Elsevier','10.1111':'Wiley','10.1002':'Wiley','10.1257':'AEA','10.2307':'JSTOR','10.1287':'INFORMS','10.1093':'Oxford UP','10.1086':'U Chicago Press','10.1162':'MIT Press','10.1017':'Cambridge UP','10.1007':'Springer','10.1023':'Springer','10.2308':'AAA','10.2139':'SSRN','10.1509':'AMA/SAGE','10.1177':'SAGE','10.1080':'Taylor & Francis','10.1108':'Emerald','10.1089':'Mary Ann Liebert','10.1373':'Oxford UP (Clin Chem)','10.5210':'First Monday','10.1038':'Nature','10.1056':'NEJM','10.1001':'JAMA','10.3386':'NBER'}
R=json.load(open(sys.argv[1])); o=['# proxy_todo (legal OA retrieval failed, 2026-11-01)\n','| ID | DOI | Publisher | Free links found (bot-blocked/unverified) |','|---|---|---|---|']
from collections import defaultdict; G=defaultdict(list)
for r in R:
    if r['st']!='MISS': continue
    d=r.get('doi',''); p=P.get(d.split('/')[0].lower() if d else '', 'Other' if d else 'No DOI')
    if d.lower().startswith('10.1257'):p='AEA'
    G[p].append(r['id']); o.append(f"| {r['id']} | {d or '—'} | {p} | {' ; '.join(u for u in r.get('cands',[]) if 'doi.org' not in u)[:400]} |")
open(sys.argv[2],'w').write('\n'.join(o)+'\n')
for p,v in sorted(G.items()): print(f'{p}({len(v)}): {" ".join(v)}')
