import json,numpy as np,pandas as pd
import r2
from r2 import *
c=json.load(open('r2_robust.json'))[0]['params']
def run(p,lo='2022-01-01',hi='2026-10-30',cash=True,gapfix=False):
    if not cash: r2.rfbar=np.zeros(N)
    else: r2.rfbar=np.array([EFFR[t.year]/100 for t in h.index])/(252*7)
    if gapfix: p=dict(p,gap=9)
    r,eps,w=r2.sim(p); s,dr=stats(r,eps,w,lo,hi)
    m=(idx>=pd.Timestamp(lo))&(idx<pd.Timestamp(hi))
    rf=pd.Series(np.array([EFFR[t.year]/100 for t in idx])[m]/252,index=dayid[m]).groupby(level=0).first().values
    ex=dr-rf if cash else dr
    s['sh_excess']=float(ex.mean()/ex.std()*np.sqrt(252)); s['per_cap_ann']=float(np.mean(dr- (rf*(1) if cash else 0))*252/max(s['avgw'],1e-9)) 
    return {k:round(v,4) for k,v in s.items()}
for nm,p in [('P2',P2),('H2',c),('H2_rth20(DSR所测)',json.load(open('r2_selected.json'))['best'])]:
    print(nm,'含现金',run(p)); print(nm,'无现金',run(p,cash=False))
print('H2 去掉gap', run(c,gapfix=True)); print('H2 force=1',run(dict(c,force=1)));print('H2 frac=1',run(dict(c,entry='split',frac=1.0)))
