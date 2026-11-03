import json,numpy as np
from r2 import *
recs=[json.loads(l) for l in open('r2_log.jsonl')]
seen=set(); top=[]
for r in sorted(recs,key=lambda x:-x['obj']):
    k=json.dumps(r['params'],sort_keys=True)
    if k in seen: continue
    seen.add(k); top.append(r)
    if len(top)==30: break
out=[]
for r in top:
    b=r['params']; objs=[]
    for k,v in GRID.items():
        if isinstance(v[0],str): continue
        j=v.index(b[k])
        for jj in (j-1,j+1):
            if 0<=jj<len(v): q=dict(b); q[k]=v[jj]; objs.append(wf_objective(q)[0])
    out.append(dict(params=b,obj=r['obj'],nb_mean=float(np.mean(objs)),nb_min=float(np.min(objs)),score=float(0.5*r['obj']+0.5*np.mean(objs))))
out.sort(key=lambda x:-x['score'])
json.dump(out,open('r2_robust.json','w'),indent=1)
for o in out[:5]: print(round(o['obj'],3),round(o['nb_mean'],3),round(o['nb_min'],3),o['params'])
