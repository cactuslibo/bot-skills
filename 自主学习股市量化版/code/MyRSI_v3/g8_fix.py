# 仅重算 G8（LOYO 分批+波动率口径 vs 按年匹配敞口BH 的 Sharpe/MDD）。只用训练年，不涉及2024/2026。
import json,numpy as np,v3; P=v3.P; from run_v3 import tst,size_pick,TRN
assert P.yr.max()==2025
O=json.load(open('main_results.json')); dm=np.isin(v3.DY,TRN); out={}
for tag,repick in (('orig_picks',False),('repicked',True)):
    w=np.ones(P.n); picks={}
    for y,v in O['loyo'].items():
        y=int(y); yrs=[t for t in TRN if t!=y]; sg=P.signals(v['p'],[y])
        f,vt=(size_pick(P.signals(v['p'],yrs),yrs)[1:] if repick else v['size'][1:]); picks[y]=(f,vt)
        hm=P.yr==y; w[hm]=v3.position(sg,f,vt)[hm]
    d,ex=v3.daily(w); t,_=tst(d,ex,dm); out[tag]=dict(picks=picks,trade=t,G8=bool(t['sh_s']>=t['sh_b'] and t['mdd_s']<=t['mdd_b']))
out['size_grid_trials']=8*20
json.dump(out,open('g8_fix.json','w'),indent=1,default=float); print(json.dumps(out,indent=1,default=float))
