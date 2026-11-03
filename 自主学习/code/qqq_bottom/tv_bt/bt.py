"""TV-indicator bottom-buying backtests on QQQ daily. Conventions = v1: signal on close, fill next open,
exit signal on close -> fill next open, long-only, 100% in/out, no costs; Sharpe on daily returns (zeros when flat)*sqrt(252).
IS=2016-01-22..2021-12-31 (parameter choice), OOS=2022-01-01..2026-10-29."""
import pandas as pd, numpy as np, json, sys
sys.path.insert(0,'/workspace/qqq_bottom/tv_bt'); from ind import *
D='/workspace/qqq_bottom/data/'
def load(start):
    q=pd.read_csv('/workspace/data/QQQ_daily.csv',parse_dates=['date']).set_index('date')  # has 2026-10-29; identical to tv file 2016+
    q=q.loc[start:] if start else q
    for n,f in [('vix','VIX'),('vix3m','VIX3M'),('adv','ADVN_NQ'),('dec','DECL_NQ'),('ndfi','NDFI')]:
        s=pd.read_csv(D+f+'.csv',parse_dates=['time']).set_index('time')['close']; q[n]=s.reindex(q.index).ffill()
    return q
def run(df,entry,exitf,maxd=None):
    O,C=df.open.values,df.close.values; N=len(df); e=entry.fillna(False).values; x=exitf.fillna(False).values
    ret=np.zeros(N); inp=np.zeros(N,bool); tr=[]; pos=False; pin=pout=False
    for i in range(1,N):
        if pos and pout:
            ret[i]=O[i]/C[i-1]-1; inp[i]=True; tr.append((ei,i,ep,O[i])); pos=pout=False
            if e[i] and i<N-1: pin=True
            continue
        if not pos:
            if pin:
                pos=True; ei=i; ep=O[i]; ret[i]=C[i]/ep-1; inp[i]=True; pin=False
                if x[i] or (maxd and 1>=maxd): pout=True
            elif e[i] and i<N-1: pin=True
            continue
        inp[i]=True; ret[i]=C[i]/C[i-1]-1
        if x[i] or (maxd and i-ei+1>=maxd): pout=True
    openpos=pos
    if pos: tr.append((ei,N-1,ep,C[-1]))
    return tr,ret,inp,openpos,pin
def stats(df,tr,ret,inp,a,b):
    a,b=pd.Timestamp(a),pd.Timestamp(b); idx=df.index; m=(idx>=a)&(idx<=b); r=pd.Series(ret[m]); eq=(1+r).cumprod(); yrs=m.sum()/252
    pr=np.array([x/p-1 for s,_,p,x in tr if a<=idx[s]<=b])
    return dict(trades=len(pr),win=(pr>0).mean() if len(pr) else np.nan,CAGR=eq.iat[-1]**(1/yrs)-1,
                sharpe=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else np.nan,MDD=(eq/eq.cummax()-1).min(),exposure=inp[m].mean())
P={'IS':('2016-01-22','2021-12-31'),'OOS':('2022-01-01','2026-12-31'),'FULL':('2016-01-22','2026-12-31')}
