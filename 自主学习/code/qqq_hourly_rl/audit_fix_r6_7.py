"""审计整改复算（第 6–7 轮）：半日 PX 修正后重算；资金占用统一 avgw；SPA 覆盖每轮全部 67 个候选（验证集日收益差）；
DSR 试验数 N=10670+134=10804；训练段触发次数（≥5 门槛，附加执行规则）。入选参数保持各轮原选中项不变（不重新选参）。"""
import json, datetime, numpy as np, pandas as pd, importlib
from r5 import full_report, rc_spa, dsr, EFFR
from config import VAL; NT=10670+134   # 验证集终点 2026-10-28（含），见 config.py
out={}
with open('OOS_LOG.md','a') as fh: fh.write(f"| 8 | R6/R7 审计整改复算 | {datetime.datetime.now():%Y-%m-%d %H:%M} | R6、R7 全部 134 个候选（SPA 用），原选中项不变 | audit_fix_r6_7.py |\n")
for modname in ['r6','r7']:
    mod=importlib.import_module(modname); m=mod.M('QQQ'); C=mod.cands(); base=mod.build(m,'P2',None)
    res=json.load(open(f'{modname}_results.json'))
    mv=(m.days>=pd.Timestamp(VAL[0]))&(m.days<pd.Timestamp(VAL[1])); rf=np.array([EFFR.get(d.year,0)/100/252 for d in m.days])
    bdr=m.returns(*base,True); D=[]; keys=[]; R=[]
    for fam,p in C:
        w=mod.build(m,fam,p); dr=m.returns(*w,True); D.append(dr[mv]-bdr[mv]); keys.append((fam,json.dumps(p,sort_keys=True))); R.append(dr[mv]-rf[mv])
    D=np.array(D).T; R=np.array(R).T; _,p_spa_all=rc_spa(D); srv=(R.mean(0)/R.std(0)).var()
    b=full_report(m,*base,*VAL); fix={'P2_val':b,'spa_all67':p_spa_all,'NT':NT,'chosen':{}}
    for f,v in res['best'].items():
        p=v['p']
        if modname=='r6' and f=='F2_rt+panic': p={'panic':tuple(p['panic'])}
        w=mod.build(m,f,p); s=full_report(m,*w,*VAL); trainlo,trainhi=mod.TRAIN[f]
        trig=None
        if modname=='r7' and f!='G3_exec':
            mod.build(m,f,p); trig=sum(1 for e,x,md in m._ivals if md=='moc' and pd.Timestamp(trainlo)<=m.days[min(e,len(m.days)-1)]<pd.Timestamp(trainhi))
        dr=m.returns(*w,True); x=(dr-rf)[(m.days>=pd.Timestamp(trainlo))&(m.days<pd.Timestamp(trainhi))]
        ds=dsr(x,NT,srv)
        k=keys.index((f,json.dumps(p if not isinstance(p.get('panic'),tuple) else {'panic':list(p['panic'])},sort_keys=True))) if (f,json.dumps(p,sort_keys=True)) in keys or True else None
        crit=dict(capital=s['avgw']>=0.8*b['avgw'],win=s['win']>b['win'],cagr=s['cagr']>b['cagr'],exS=s['exSharpe']>=b['exSharpe'],mdd=s['mdd']>=b['mdd']-0.02,spa=p_spa_all<0.10,trig5=(trig is None or trig>=5))
        fix['chosen'][f]=dict(params=v['p'],val=s,train_triggers=trig,dsr_train=ds,crit=crit,WIN=all(crit.values()))
        print(modname,f,v['p'],{a:round(x,4) for a,x in s.items()},'trig',trig,'DSR %.3f'%ds[0],crit)
    print(modname,'P2 val',{a:round(x,4) for a,x in b.items()},'SPA(67)=%.3f'%p_spa_all)
    res['audit_fix']=fix
    for f in res['res']: res['res'][f]['oos']['avgw']=fix['chosen'][f]['val']['avgw']
    res['oos_p2']['avgw']=b['avgw']
    json.dump(res,open(f'{modname}_results.json','w'),indent=1,default=str)
