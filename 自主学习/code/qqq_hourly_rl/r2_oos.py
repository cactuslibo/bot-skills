import json
from r2 import *
c=json.load(open('r2_robust.json'))[0]['params']; res={}
for name,p in [('P2',P2),('H2',c)]:
    r,eps,w=sim(p)
    for seg,(lo,hi) in {'pre_oos':('2015-01-01','2022-01-01'),'oos':('2022-01-01','2026-10-30'),'full':('2015-01-01','2026-10-30')}.items():
        s,_=stats(r,eps,w,lo,hi); hold=np.mean([(e[1]-e[0])/7 for e in eps if e[0]>=np.searchsorted(idx,pd.Timestamp(lo)) and e[0]<np.searchsorted(idx,pd.Timestamp(hi))])
        s['avg_hold_days']=float(hold); res[f'{name}_{seg}']=s; print(name,seg,{k:round(v,4) for k,v in s.items()})
json.dump(dict(H2=c,res=res),open('r2_oos.json','w'),indent=1)
