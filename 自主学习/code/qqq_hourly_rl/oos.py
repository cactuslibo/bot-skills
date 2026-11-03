import json
from search import *
sel=json.load(open('selected.json')); out=[]
for k,s in enumerate(sel):
    p=s['params']; p={a:(int(v) if a in('rn','rth','ddn','sma','hold','dth') else v) for a,v in p.items()}
    r,tr,pos=build(p); m=metrics(r,idx,tr,pos,BPY,*TE); full=metrics(r,idx,tr,pos,BPY,'2015-01-01','2026-10-30')
    hrs=np.mean([t[4] for t in tr]); print(k,'OOS',{a:round(float(v),4) for a,v in m.items()},'avg_hold_bars',round(hrs,1)); print('  full',{a:round(float(v),4) for a,v in full.items()})
    out.append(dict(rank=k,params=s['params'],oos={a:float(v) for a,v in m.items()},full={a:float(v) for a,v in full.items()}))
json.dump(out,open('oos_results.json','w'),indent=1)
