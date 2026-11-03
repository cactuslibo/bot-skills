"""同口径重算第 6–7 轮选中项 DSR（训练段收益 + 当轮全部候选在同一训练段的 SR 方差；N=10804）。只用训练段，不计入验证集查看。"""
import json, importlib, numpy as np, pandas as pd
from r5 import dsr, EFFR
for modname in ['r6','r7']:
    mod=importlib.import_module(modname); m=mod.M('QQQ'); C=mod.cands(); rf=np.array([EFFR.get(d.year,0)/100/252 for d in m.days])
    res=json.load(open(f'{modname}_results.json'))
    for f,v in res['audit_fix']['chosen'].items():
        p=v['params']; p={'panic':tuple(p['panic'])} if 'panic' in p else p
        lo,hi=mod.TRAIN[f]; mt=(m.days>=pd.Timestamp(lo))&(m.days<pd.Timestamp(hi))
        srs=[((lambda x:x.mean()/x.std())((m.returns(*mod.build(m,ff,pp),True)-rf)[mt])) for ff,pp in C]
        d=dsr((m.returns(*mod.build(m,f,p),True)-rf)[mt],10804,np.var(srs))
        v['dsr_train_v2']=dict(dsr=d[0],sr_ann=d[1],sr0_ann=d[2]); print(modname,f,'DSR %.3f (SR %.2f, SR0 %.2f)'%d)
    json.dump(res,open(f'{modname}_results.json','w'),indent=1,default=str)
