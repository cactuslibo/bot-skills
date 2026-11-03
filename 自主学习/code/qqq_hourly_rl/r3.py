"""Round 3: 资金对等 + 相对P2超额奖励 + ATR出场 + decomp消融 + 嵌套(扩展窗)walk-forward"""
import json, sys, numpy as np, pandas as pd, optuna
from multiprocessing import Pool
from r3eng import *
optuna.logging.set_verbosity(optuna.logging.WARNING)
idx=h.index; YR=idx.year.values
def day_rets(r):
    s=pd.Series(r).groupby(dayid).apply(lambda x:np.prod(1+x.values)-1); return s.values
DYR=np.array([d.year for d in days])
def year_stats(r,eps,w,y):
    dr=DR_cache(r)[DYR==y]; eq=np.cumprod(1+dr); sd=dr.std()
    cum=np.cumprod(1+r); pnl=[cum[b]/cum[a-1]-1 for a,b in eps if YR[a]==y and a>0]
    m=YR==y
    return dict(win=float(np.mean([x>0 for x in pnl])) if pnl else 0.0,n=len(pnl),tot=float(eq[-1]-1),cagr=float(eq[-1]**(252/len(dr))-1),
        mdd=float((eq/np.maximum.accumulate(eq)-1).min()),sharpe=float(dr.mean()/sd*np.sqrt(252)) if sd>0 else 0.0,avgw=float(w[m].mean()),expo=float((w[m]>0).mean()))
def DR_cache(r):
    lg=np.log1p(r); s=np.zeros(len(days)); np.add.at(s,dayid,lg); return np.expm1(s)
P2=dict(entry='open',exit='base',tpk=9,stk=9,hd=999,delay=0,rn=2,rth=0,dip=0.0,win=7,force=1,frac=0.0,gap=9,decomp='none')
_p2=sim(P2); P2Y={y:year_stats(*_p2,y) for y in range(2016,2027)}
def rel_reward(s,b): return (s['sharpe']-b['sharpe'])+(s['win']-b['win'])+0.5*(s['cagr']-b['cagr'])
def objective_years(p,years):
    out=sim(p); rs=[];n=0;nb=0;aw=0;ab=0
    for y in years:
        s=year_stats(*out,y); b=P2Y[y]; rs.append(rel_reward(s,b)); n+=s['n']; nb+=b['n']; aw+=s['avgw']; ab+=b['avgw']
    o=float(np.mean(rs)-0.5*np.std(rs))
    if n<0.7*nb or aw<0.8*ab: o=-9.0
    return o
def suggest(t,decomp):
    p=dict(entry=t.suggest_categorical('entry',['open','dip','split']),exit=t.suggest_categorical('exit',['base','moc','delay']),
      tpk=t.suggest_float('tpk',0.5,8.0) if t.suggest_categorical('use_tp',[0,1]) else 9,
      stk=t.suggest_float('stk',1.0,10.0) if t.suggest_categorical('use_st',[0,1]) else 9,
      hd=t.suggest_categorical('hd',[2,3,4,5,999]),delay=t.suggest_int('delay',1,6),rn=t.suggest_categorical('rn',[2,3,5,8,14]),
      rth=t.suggest_int('rth',5,35),dip=t.suggest_float('dip',0.002,0.03),win=t.suggest_int('win',3,14),force=1,
      frac=t.suggest_float('frac',0.25,0.9),gap=t.suggest_float('gap',0.002,0.02) if t.suggest_categorical('use_gap',[0,1]) else 9,
      decomp=t.suggest_categorical('decomp',['none','intra_dn','over_up']) if decomp=='free' else decomp)
    return p
FL=['tpk','stk','dip','frac','gap']
def optimize(args):
    decomp,ytest,ntr=args; years=list(range(2016,ytest))
    recs=[]
    def obj(t):
        p=suggest(t,decomp); o=objective_years(p,years); recs.append((o,p)); return o
    st=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=ytest,n_startup_trials=40)); st.optimize(obj,n_trials=ntr)
    # 稳健重排: top10, 每个浮点参数 ±15% 和整数 ±1 的随机扰动 6 次取均值
    rng=np.random.default_rng(0); top=sorted(recs,key=lambda x:-x[0])[:10]; scored=[]
    for o,p in top:
        if o<=-9: continue
        nb=[]
        for _ in range(6):
            q=dict(p)
            for k in FL:
                if q[k]<9: q[k]=q[k]*rng.uniform(0.85,1.15)
            for k,lo,hi in [('rth',5,35),('win',3,14),('delay',1,6)]: q[k]=int(np.clip(q[k]+rng.integers(-1,2),lo,hi))
            nb.append(objective_years(q,years))
        scored.append((0.5*o+0.5*np.mean(nb),o,float(np.mean(nb)),p))
    scored.sort(key=lambda x:-x[0]); best=scored[0] if scored else (None,None,None,P2)
    return dict(decomp=decomp,ytest=ytest,train_years=years,score=best[0],obj=best[1],nb_mean=best[2],params=best[3],
                trials=[dict(o=o,p=p) for o,p in recs])
if __name__=='__main__':
    phase=sys.argv[1]; NT=int(sys.argv[2])
    if phase=='pre':
        jobs=[(d,y,NT) for d in ['free','none','intra_dn'] for y in (2019,2020,2021)]
    else:
        d=sys.argv[3]; jobs=[(d,y,NT) for y in (2022,2023,2024,2025,2026)]
    with Pool(6) as pool: res=pool.map(optimize,jobs)
    json.dump(res,open(f'r3_{phase}.json','w'),default=float)
    # 嵌套评估: 每个测试年用该年之前训练出的参数
    for d in sorted(set(r['decomp'] for r in res)):
        rr=[r for r in res if r['decomp']==d]
        for r in rr:
            out=sim(r['params']); s=year_stats(*out,r['ytest']); b=P2Y[r['ytest']]
            print(d,r['ytest'],'R_rel=%.3f'%rel_reward(s,b),'cand',{k:round(v,3) for k,v in s.items()},'P2',{k:round(v,3) for k,v in b.items()})
