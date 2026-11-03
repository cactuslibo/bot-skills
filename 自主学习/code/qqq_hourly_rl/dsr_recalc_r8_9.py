"""只用训练段重算第 8–9 轮选中项的 DSR（统一口径，不读取验证集 -> 不计入验证集查看次数）。结果写回 r8_results.json / r9_results.json 的 res.*.dsr_train_v2。"""
import json, importlib, numpy as np, pandas as pd
from r5 import dsr, EFFR
for modname,NT in [('r8',10909),('r9',10945)]:
    mod=importlib.import_module(modname); m=mod.M('QQQ'); C=mod.cands(); rf=np.array([EFFR.get(d.year,0)/100/252 for d in m.days])
    res=json.load(open(f'{modname}_results.json'))
    for f,v in res['res'].items():
        lo,hi=mod.TRAIN[f]; mt=(m.days>=pd.Timestamp(lo))&(m.days<pd.Timestamp(hi))
        srs=[]
        for ff,pp in C:
            x=(m.returns(*mod.build(m,ff,pp),True)-rf)[mt]; srs.append(x.mean()/x.std())
        x=(m.returns(*mod.build(m,f,v['params']),True)-rf)[mt]; d=dsr(x,NT,np.var(srs))
        v['dsr_train_v2']=dict(dsr=d[0],sr_ann=d[1],sr0_ann=d[2],note='SR 方差取当轮全部候选在同一训练段的方差')
        print(modname,f,'旧 DSR %.3f -> 新 DSR %.3f (SR %.2f, SR0 %.2f)'%(v['dsr_train'][0] if isinstance(v['dsr_train'],list) else float(str(v['dsr_train']).strip('()[]').split(',')[0]),d[0],d[1],d[2]))
    json.dump(res,open(f'{modname}_results.json','w'),indent=1,default=str)
