"""第 8 轮起的统一流程（执行 WIN_CRITERIA 原标准 + 附加规则 A1–A5）：
训练选参（avgw 对等、新分支训练触发≥5）-> 各族最佳进入验证集（只看一次，记录 OOS_LOG.md）-> SPA 覆盖当轮全部候选 -> DSR（全部轮次试验数）-> 跨 ETF。
用法: python3 winrun2.py r8 R8 <之前累计试验数>"""
import json, sys, importlib, datetime, numpy as np, pandas as pd
mod=importlib.import_module(sys.argv[1]); RN=sys.argv[2]; NPREV=int(sys.argv[3])
from r5 import full_report, rc_spa, dsr, EFFR
from config import VAL   # 验证集终点 2026-10-28（含），见 config.py
m=mod.M('QQQ'); C=mod.cands(); base=mod.build(m,'P2',None); NT=NPREV+len(C)
rf=np.array([EFFR.get(d.year,0)/100/252 for d in m.days])
def dsr_train(fam,p,lo,hi):
    """DSR 统一用训练段：被检验的收益 = 选中项在其训练段的日超额收益；SR 方差 = 当轮全部候选在同一训练段的日 SR 方差（不再用验证集的方差）。"""
    mt=(m.days>=pd.Timestamp(lo))&(m.days<pd.Timestamp(hi)); srs=[]
    for ff,pp in C:
        x=(m.returns(*mod.build(m,ff,pp),True)-rf)[mt]; srs.append(x.mean()/x.std())
    x=(m.returns(*mod.build(m,fam,p),True)-rf)[mt]
    return dsr(x,NT,np.var(srs))
def R(s,b): return (s['exSharpe']-b['exSharpe'])+(s['win']-b['win'])+0.5*(s['cagr']-b['cagr'])
rows=[]
for fam,p in C:
    lo,hi=mod.TRAIN[fam]; b=full_report(m,*base,lo,hi); w=mod.build(m,fam,p); s=full_report(m,*w,lo,hi); tr=mod.triggers(m,fam,lo,hi)
    ok=s['avgw']>=0.8*b['avgw'] and tr>=5
    rows.append(dict(fam=fam,p=p,train=s,p2train=b,trig=tr,R=R(s,b) if ok else -9,eligible=ok))
best={}
for r in rows:
    if not r['eligible']: continue                       # 不合格候选不参与入选（不再默认选第一个）
    if r['fam'] not in best or r['R']>best[r['fam']]['R']: best[r['fam']]=r
for f in sorted(set(r['fam'] for r in rows)-set(best)): print(f'WARNING: 族 {f} 没有合格候选（avgw 对等且训练触发≥5），不进入验证集')
if not best: raise SystemExit('ERROR: 全部候选都不合格（avgw 对等且训练触发≥5），本轮不进入验证集')
for f,r in best.items(): print('TRAIN',f,mod.TRAIN[f],r['p'],'trig',r['trig'],'R=%.3f'%r['R'],{k:round(v,3) for k,v in r['train'].items()},'| P2',{k:round(v,3) for k,v in r['p2train'].items()})
n_el=sum(r['eligible'] for r in rows); print('eligible',n_el,'/',len(rows))
# ---- 验证集：只看一次 ----
k=sum(1 for l in open('OOS_LOG.md') if l.startswith('| ') and l[2].isdigit())+1
with open('OOS_LOG.md','a') as fh: fh.write(f"| {k} | {RN} | {datetime.datetime.now():%Y-%m-%d %H:%M} | 全部 {len(C)} 个候选（SPA 用）；报告 {', '.join(best)} 的训练段最佳 + P2 | winrun2.py {sys.argv[1]} |\n")
mv=(m.days>=pd.Timestamp(VAL[0]))&(m.days<pd.Timestamp(VAL[1])); bdr=m.returns(*base,True)
bv=full_report(m,*base,*VAL); D=[]; RR=[]
for fam,p in C:
    dr=m.returns(*mod.build(m,fam,p),True); D.append(dr[mv]-bdr[mv]); RR.append(dr[mv]-rf[mv])
D=np.array(D).T; _,p_spa=rc_spa(D)
print('SPA over all %d candidates: p=%.3f'%(len(C),p_spa))
res={}
for f,r in best.items():
    w=mod.build(m,f,r['p']); s=full_report(m,*w,*VAL); trv=mod.triggers(m,f,*VAL)
    i=[j for j,(ff,pp) in enumerate(C) if ff==f and pp==r['p']][0]; _,p1=rc_spa(D[:,[i]])
    lo,hi=mod.TRAIN[f]; ds=dsr_train(f,r['p'],lo,hi)
    crit=dict(capital=s['avgw']>=0.8*bv['avgw'],win=s['win']>bv['win'],cagr=s['cagr']>bv['cagr'],exS=s['exSharpe']>=bv['exSharpe'],mdd=s['mdd']>=bv['mdd']-0.02,
              spa=(p_spa<0.10 and D[:,i].mean()>0),trig5=r['trig']>=5)
    res[f]=dict(params=r['p'],train_trig=r['trig'],val_trig=trv,val=s,p_single=p1,p_spa_all=p_spa,dsr_train=ds,crit=crit,WIN=all(crit.values()))
    print('VAL',f,{a:round(v,4) for a,v in s.items()},'trig_val',trv,'p1=%.3f'%p1,'DSR=%.3f'%ds[0],crit,'WIN' if all(crit.values()) else 'no')
print('VAL P2',{a:round(v,4) for a,v in bv.items()})
ETF=['XLK','XLY','XLF','XLI','XLV','XLP','XLE','XLB','XLU']; xe={}
for tk in ETF:
    e=mod.M(tk); eb=full_report(e,*mod.build(e,'P2',None),*VAL); xe[tk]={}
    for f in best:
        s=full_report(e,*mod.build(e,f,best[f]['p']),*VAL); xe[tk][f]=dict(dExS=s['exSharpe']-eb['exSharpe'],dWin=s['win']-eb['win'],dCagr=s['cagr']-eb['cagr'],dMdd=s['mdd']-eb['mdd'])
for f in best:
    v=[xe[t][f] for t in ETF]; print('XETF',f,'dExS>0 %d/9, dWin>0 %d/9, dCAGR>0 %d/9, mean dExS %.3f, mean dCAGR %.4f, mean dMDD %.4f'%(sum(x['dExS']>0 for x in v),sum(x['dWin']>0 for x in v),sum(x['dCagr']>0 for x in v),np.mean([x['dExS'] for x in v]),np.mean([x['dCagr'] for x in v]),np.mean([x['dMdd'] for x in v])))
json.dump(dict(NT=NT,rows=rows,best={f:dict(p=r['p'],R=r['R'],trig=r['trig'],train=r['train'],p2train=r['p2train']) for f,r in best.items()},val_p2=bv,spa_all=p_spa,res=res,xetf=xe),open(f'{sys.argv[1]}_results.json','w'),indent=1,default=str)
