"""通用：训练段选参 -> 各族最佳进入 OOS（只看一次）-> 胜出标准检查 + OOS 上的 SPA + 跨 ETF。用法: python3 winrun.py r6 ROUND"""
import json, sys, importlib, datetime, numpy as np, pandas as pd
mod=importlib.import_module(sys.argv[1]); RN=sys.argv[2]
from r5 import full_report, rc_spa, EFFR
from config import VAL as OOS; TRAIN=mod.TRAIN   # 验证集终点 2026-10-28（含），见 config.py
m=mod.M('QQQ'); C=mod.cands(); base=mod.build(m,'P2',None)
rf=np.array([EFFR.get(d.year,0)/100/252 for d in m.days])
def R(s,b): return (s['exSharpe']-b['exSharpe'])+(s['win']-b['win'])+0.5*(s['cagr']-b['cagr'])
rows=[]
for fam,p in C:
    lo,hi=TRAIN[fam]; b=full_report(m,*base,lo,hi); s=full_report(m,*mod.build(m,fam,p),lo,hi)
    ok=s['avgw']>=0.8*b['avgw']
    rows.append(dict(fam=fam,p=p,train=s,p2train=b,R=R(s,b) if ok else -9))
best={}
for r in rows:
    if r['fam'] not in best or r['R']>best[r['fam']]['R']: best[r['fam']]=r
for f,r in best.items(): print('TRAIN',f,TRAIN[f],r['p'],'R=%.3f'%r['R'],{k:round(v,3) for k,v in r['train'].items()},'P2',{k:round(v,3) for k,v in r['p2train'].items()})
# ---- OOS 只看一次 ----
with open('OOS_LOG.md','a') as fh: fh.write(f"| {sum(1 for l in open('OOS_LOG.md') if l.startswith('| ') and l[2].isdigit())+1} | {RN} | {datetime.datetime.now():%Y-%m-%d %H:%M} | {', '.join(best)} 的训练段最佳 + P2 | winrun.py {sys.argv[1]} |\n")
mo=(m.days>=pd.Timestamp(OOS[0]))&(m.days<pd.Timestamp(OOS[1]))
bo=full_report(m,*base,*OOS); bdr=m.returns(*base,True)[mo]; D=[]; out={}
for f,r in best.items():
    w=mod.build(m,f,r['p']); s=full_report(m,*w,*OOS); D.append(m.returns(*w,True)[mo]-bdr); out[f]=s
D=np.array(D).T; _,p_spa=rc_spa(D)
res={}
for k,(f,s) in enumerate(out.items()):
    _,p_ind=rc_spa(D[:,[k]])
    crit=dict(capital=s['avgw']>=0.8*bo['avgw'],win=s['win']>bo['win'],cagr=s['cagr']>bo['cagr'],exS=s['exSharpe']>=bo['exSharpe'],mdd=s['mdd']>=bo['mdd']-0.02,spa=p_spa<0.10 and D[:,k].mean()>0)
    res[f]=dict(params=best[f]['p'],oos=s,p_single=p_ind,p_spa_set=p_spa,crit=crit,WIN=all(crit.values()))
    print('OOS',f,{a:round(v,4) for a,v in s.items()},'p_single=%.3f p_SPA=%.3f'%(p_ind,p_spa),crit,'WIN' if all(crit.values()) else 'no')
print('OOS P2',{a:round(v,4) for a,v in bo.items()})
# ---- 跨 ETF（冻结参数） ----
ETF=['XLK','XLY','XLF','XLI','XLV','XLP','XLE','XLB','XLU']; xe={}
for tk in ETF:
    e=mod.M(tk); eb=full_report(e,*mod.build(e,'P2',None),*OOS); xe[tk]={}
    for f in best:
        s=full_report(e,*mod.build(e,f,best[f]['p']),*OOS); xe[tk][f]=dict(dExS=s['exSharpe']-eb['exSharpe'],dWin=s['win']-eb['win'],dCagr=s['cagr']-eb['cagr'])
for f in best:
    v=[xe[t][f] for t in ETF]; print('XETF OOS',f,'dExS>0 %d/9, dWin>0 %d/9, dCAGR>0 %d/9, mean dExS %.3f, mean dCAGR %.4f'%(sum(x['dExS']>0 for x in v),sum(x['dWin']>0 for x in v),sum(x['dCagr']>0 for x in v),np.mean([x['dExS'] for x in v]),np.mean([x['dCagr'] for x in v])))
json.dump(dict(rows=rows,best={f:dict(p=r['p'],R=r['R'],train=r['train'],p2train=r['p2train']) for f,r in best.items()},oos_p2=bo,res=res,xetf=xe),open(f'{sys.argv[1]}_results.json','w'),indent=1,default=str)
