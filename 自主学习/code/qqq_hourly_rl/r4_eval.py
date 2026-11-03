import json,sys
from r4 import *
def stitched(res):
    rows=[];dr=[];tp=[];ws=[];h4d=[];per=[]
    for r in res:
        y=r['ytest']; p=r['chosen']['params'] if r['chosen'] else None
        out=sim(p) if p else p2_out(); s=year_stats(out,[y]); b=year_stats(p2_out(),[y])
        per.append((y,p is not None,s,b,rel(s,b)))
        rr,eps,w=out; dr.append(DR(rr)[DYR==y]); ws.append(w[YR==y])
        for x in tr_pnl(rr,eps):
            if YR[x[0]]==y:
                tp.append(x)
                if x[2]=='h4': h4d.append(x[3]-cash_ret(x[0],x[1]+1))
    dr=np.concatenate(dr); eq=np.cumprod(1+dr); w=np.concatenate(ws)
    S=dict(win=np.mean([x[3]>0 for x in tp]),n=len(tp),n_h4=len(h4d),tot=eq[-1]-1,cagr=eq[-1]**(252/len(dr))-1,mdd=(eq/np.maximum.accumulate(eq)-1).min(),sharpe=dr.mean()/dr.std()*np.sqrt(252),expo=w.mean())
    return S,per,np.array(h4d),dr
res=json.load(open(sys.argv[1])); S,per,h4d,dr=stitched(res); ys=[r['ytest'] for r in res]
B=year_stats(p2_out(),ys); bdr=DR(p2_out()[0])[np.isin(DYR,ys)]
for y,has,s,b,R in per: print(y,'H4' if has else 'P2only','R_rel=%.3f'%R,'combo',{k:round(v,3) for k,v in s.items()},'P2',{k:round(v,3) for k,v in b.items()})
print('COMBO',{k:round(float(v),4) for k,v in S.items()}); print('P2   ',{k:round(float(v),4) for k,v in B.items()})
rng=np.random.default_rng(1)
if len(h4d): bs=rng.choice(h4d,(5000,len(h4d))).mean(1); print('H4 trade paired diff: n',len(h4d),'mean',round(h4d.mean(),4),'win',round((h4d>0).mean(),3),'p(mean<=0)',(bs<=0).mean(),'CI90',np.percentile(bs,[5,95]).round(4))
# 日度配对 block bootstrap（组合−P2）
d=dr-bdr; L=10; nb=len(d)//L; bs=[]
for _ in range(5000):
    st=rng.integers(0,len(d)-L,nb); bs.append(np.concatenate([d[s:s+L] for s in st]).mean())
bs=np.array(bs); print('daily diff mean*252',round(d.mean()*252,4),'p(<=0)',(bs<=0).mean())
json.dump(dict(combo={k:float(v) for k,v in S.items()},p2={k:float(v) for k,v in B.items()},per=[(y,h,s,b,R) for y,h,s,b,R in per],h4_diffs=h4d.tolist()),open(sys.argv[1].replace('.json','_eval.json'),'w'),default=float,indent=1)
