import json
from r3 import *
res=json.load(open('r3_oos.json'))
def agg(plist):
    dr=[];pnl=[];w=[]
    for y,p in plist:
        r,eps,ww=sim(p); d=DR_cache(r); dr.append(d[DYR==y]); w.append(ww[YR==y]); cum=np.cumprod(1+r)
        pnl+= [cum[b]/cum[a-1]-1 for a,b in eps if YR[a]==y]
    dr=np.concatenate(dr); w=np.concatenate(w); eq=np.cumprod(1+dr)
    return dict(win=np.mean([x>0 for x in pnl]),n=len(pnl),tot=eq[-1]-1,cagr=eq[-1]**(252/len(dr))-1,mdd=(eq/np.maximum.accumulate(eq)-1).min(),
       sharpe=dr.mean()/dr.std()*np.sqrt(252),expo=(w>0).mean(),avgw=w.mean())
H=agg([(r['ytest'],r['params']) for r in res]); B=agg([(y,P2) for y in range(2022,2027)])
out={'H3':{k:float(v) for k,v in H.items()},'P2':{k:float(v) for k,v in B.items()}}
print(json.dumps(out,indent=1)); json.dump(out,open('r3_oos_agg.json','w'),indent=1)
