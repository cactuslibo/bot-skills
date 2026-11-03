"""Round-2 engine: weight-based, signal at close i -> weight change at open i+1; costs per side in bps of traded notional.
Uses full-history aux data from data/full (bars after 2026-10-29 dropped: 10-30 is an unfinished intraday bar)."""
import pandas as pd, numpy as np, sys
sys.path.insert(0,'/workspace/qqq_bottom/tv_bt'); from ind import *
F='/workspace/qqq_bottom/data/full/'
# approximate annual average effective fed funds rate (%), used only for leverage borrow cost / optional cash yield
EFFR={2000:6.24,2001:3.88,2002:1.67,2003:1.13,2004:1.35,2005:3.22,2006:4.97,2007:5.02,2008:1.92,2009:0.16,2010:0.18,2011:0.10,
2012:0.14,2013:0.11,2014:0.09,2015:0.13,2016:0.40,2017:1.00,2018:1.83,2019:2.16,2020:0.38,2021:0.08,2022:1.68,2023:5.02,2024:5.14,2025:4.20,2026:3.80,1999:4.97}
def load_full():
    q=pd.read_csv('/workspace/data/QQQ_daily.csv',parse_dates=['date']).set_index('date')
    for n,f in [('vix','VIX'),('vix3m','VIX3M'),('adv','ADVN_NQ'),('dec','DECL_NQ'),('ndfi','NDFI')]:
        s=pd.read_csv(F+f+'.csv',parse_dates=['time']).set_index('time')['close']; s=s[(s>0)&(s.index<='2026-10-29')]
        q[n]=s.reindex(q.index).ffill(limit=3)
    q['vix3m']=q.vix3m.where(q.index>=pd.Timestamp('2007-12-05'))
    q['adv']=q.adv.where(q.index>=pd.Timestamp('2004-01-01')); q['dec']=q.dec.where(q.index>=pd.Timestamp('2004-01-01'))
    q['rf']=[EFFR[y]/100 for y in q.index.year]
    return q
def returns(df,w_tgt,cost_bps=5,borrow=True,cash_yield=False):
    """w_tgt[i]: weight decided at close i, held from open i+1."""
    O,C=df.open.values,df.close.values; N=len(df); rf=df.rf.values/252; r=np.zeros(N); w=np.zeros(N)
    for i in range(1,N):
        a=w_tgt[i-1]; b=w_tgt[i-2] if i>=2 else 0.0   # b held overnight into open i, a after open i
        r[i]=b*(O[i]/C[i-1]-1)+a*(C[i]/O[i]-1)-abs(a-b)*cost_bps/1e4
        if borrow and a>1: r[i]-=(a-1)*(rf[i]+0.01/252)  # (EFFR+1%)/252 per day on borrowed slice
        if cash_yield and a<1: r[i]+=(1-a)*rf[i]
        w[i]=a
    return r,w
def sim(df,entry,exitf,cost_bps=5):
    """single-slot tactical. entry(i)->branch label or None; exitf(i,state)->bool. state={'ei','ef','br'}; ei=fill bar."""
    O=df.open.values; N=len(df); tgt=np.zeros(N); tr=[]; st=None; pend=None
    for i in range(N):
        if pend=='in': st={'ei':i,'ef':O[i],'br':br}; pend=None
        elif pend=='out': tr.append((st['ei'],i,st['ef'],O[i],st['br'])); st=None; pend=None
        if st is None:
            br=entry(i)
            if br is not None and i<N-1: pend='in'; tgt[i]=1
        else:
            if exitf(i,st): pend='out'; tgt[i]=0
            else: tgt[i]=1
    if st is not None: tr.append((st['ei'],N-1,st['ef'],df.close.values[-1],st['br']))
    r,w=returns(df,tgt,cost_bps)
    return dict(tr=tr,r=r,w=w,tgt=tgt,open=st is not None,pend=pend)
def stats(df,res,a,b,cost_bps=5):
    a,b=pd.Timestamp(a),pd.Timestamp(b); idx=df.index; m=(idx>=a)&(idx<=b)
    r=pd.Series(res['r'][m],idx[m]); eq=(1+r).cumprod(); yrs=m.sum()/252
    dd=eq/eq.cummax()-1; peak=eq.cummax()
    # longest drawdown duration (calendar days)
    under=dd<0; dur=0; mx=0; start=None
    for t,u in under.items():
        if u: start=start or t; mx=max(mx,(t-start).days)
        else: start=None
    pr=np.array([x/p*(1-cost_bps/1e4)**2-1 for s,e,p,x,_ in res['tr'] if a<=idx[s]<=b])
    win=pr[pr>0]; los=pr[pr<=0]
    sd=r.std()
    return dict(trades=len(pr),win=(pr>0).mean() if len(pr) else np.nan,
        CAGR=eq.iat[-1]**(1/yrs)-1 if yrs>0 else np.nan,sharpe=r.mean()/sd*np.sqrt(252) if sd>0 else np.nan,MDD=dd.min(),
        calmar=(eq.iat[-1]**(1/yrs)-1)/abs(dd.min()) if dd.min()<0 else np.nan,
        PF=win.sum()/-los.sum() if len(los) and los.sum()<0 else np.inf,WL=(win.mean()/-los.mean()) if len(win) and len(los) and los.mean()<0 else np.nan,
        exposure=(res['w'][m]>0).mean(),avgw=res['w'][m].mean(),dd_days=mx,tot=eq.iat[-1]-1,
        skew=r.skew(),kurt=r.kurt()+3,T=m.sum(),srd=r.mean()/sd if sd>0 else np.nan)
