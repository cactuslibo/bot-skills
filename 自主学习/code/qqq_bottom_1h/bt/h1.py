"""Hourly engine for QQQ RTH bars (7/day; bar label = start time). Signal at bar close -> fill next bar open.
Optional MOC exit at bar close (time-based exits only). Returns per bar split into gap (O_i/C_{i-1}) and intrabar (C_i/O_i)."""
import pandas as pd, numpy as np, sys
sys.path.insert(0,'/workspace/qqq_bottom/tv_bt'); from ind import sma, ema, rma, stdev, rsi, boo, mcclellan
D='/workspace/qqq_bottom_1h/data/'
def rd(f): x=pd.read_csv(D+f,parse_dates=['time']).set_index('time'); return x
def load():
    q=rd('QQQ_RTH.csv'); q=q[~q.index.duplicated()]
    q['date']=q.index.normalize(); q['hm']=q.index.strftime('%H:%M')
    q['bar']=q.hm.map({'09:30':1,'10:30':2,'11:30':3,'12:30':4,'13:30':5,'14:30':6,'15:30':7})
    q['first']=q.date!=q.date.shift(); q['last']=q.date!=q.date.shift(-1)
    q.loc[q.index[-1],'last']=False   # today's session still open (last bar 14:30)
    v=rd('VIX.csv')['close']; v=v[v.index.strftime('%H:%M').isin(q.hm.unique())]  # align VIX to RTH bar labels
    q['vix']=v.reindex(q.index); q['vix']=q.groupby('date')['vix'].ffill()
    q.loc[q.index<pd.Timestamp('2020-01-02'),'vix']=np.nan
    m=rd('VIX3M.csv')['close']; q['vix3m']=m.reindex(q.index); q['vix3m']=q.groupby('date')['vix3m'].ffill()
    for n in ['ADVN_NQ','DECL_NQ','TICK_NQ']: q[n]=rd(n+'.csv')['close'].reindex(q.index)
    # daily VIX/VIX3M from daily files (full history), lagged one day (known before today's session)
    F='/workspace/qqq_bottom/data/full/'
    dv=pd.read_csv(F+'VIX.csv',parse_dates=['time']).set_index('time')['close']; dm=pd.read_csv(F+'VIX3M.csv',parse_dates=['time']).set_index('time')['close']
    dr=(dv/dm).dropna(); dr=dr[dr.index<=pd.Timestamp('2026-10-29')]
    days=pd.Index(q.date.unique()); q['dratio_prev']=q.date.map(dr.reindex(days).ffill().shift(1))
    q['dratio_today']=q.date.map(dr.reindex(days))   # only known at day close
    return q
class Sim:
    def __init__(s,q,cost_bps=2.5): s.q=q; s.cost=cost_bps/1e4
    def run(s,entry,exitf,moc=None,size=None):
        """entry(i)->bool at close i. exitf(i,st)->bool at close i (fill next open). moc(i,st)->bool exit at close i itself."""
        q=s.q; O=q.open.values; C=q.close.values; N=len(q); gap=np.zeros(N); intr=np.zeros(N); r=np.zeros(N); w=np.zeros(N); held=np.zeros(N,bool)
        pos=0.0; pend=None; st=None; tr=[]
        for i in range(N):
            h=pos  # held through gap into open i
            g=O[i]/C[i-1]-1 if i>0 else 0.0
            if pend=='in': pos=1.0; st={'ei':i,'ef':O[i],'sig':i-1}; pend=None
            elif pend=='out': tr.append((st['ei'],i,st['ef'],O[i])); pos=0.0; st=None; pend=None
            b=C[i]/O[i]-1
            gap[i]=h*g; intr[i]=pos*b; r[i]=h*g+pos*b-abs(pos-h)*s.cost; w[i]=pos; held[i]=(pos>0 or h>0)
            if pos>0:
                if moc is not None and moc(i,st): tr.append((st['ei'],i,st['ef'],C[i],'moc')); r[i]-=s.cost; pos=0.0; st=None; continue
                if exitf(i,st): pend='out'
            else:
                if i<N-1 and entry(i): pend='in'
            # pending entry at last bar of data
        openpos=st is not None
        if openpos: tr.append((st['ei'],N-1,st['ef'],C[-1]))
        return dict(r=r,gap=gap,intr=intr,w=w,tr=tr,open=openpos,pend=pend,held=held)
BPY=252*7  # nominal bars per year used for annualisation (actual avg ~1747 due to half days)
def stats(q,R,a,b,cost_bps=2.5):
    m=(q.index>=pd.Timestamp(a))&(q.index<=pd.Timestamp(b)+pd.Timedelta(hours=23)); r=pd.Series(R['r'][m],q.index[m])
    if m.sum()==0: return {}
    yrs=(q.index[m][-1]-q.index[m][0]).days/365.25; eq=(1+r).cumprod(); dd=(eq/eq.cummax()-1).min()
    bpy=m.sum()/yrs
    dr=(1+r).groupby(q.date[m]).prod()-1
    idx=q.index; c=cost_bps/1e4
    pr=np.array([t[3]/t[2]*(1-c)/(1+c)-1 for t in R['tr'] if a<=str(idx[t[0]].date())<=b]) if R['tr'] else np.array([])
    gross=np.array([t[3]/t[2]-1 for t in R['tr'] if a<=str(idx[t[0]].date())<=b]) if R['tr'] else np.array([])
    g=R['gap'][m]; it=R['intr'][m]
    on=(g**2).sum()/((g**2).sum()+(it**2).sum()) if ((g**2).sum()+(it**2).sum())>0 else np.nan
    sd=r.std()
    return dict(trades=len(pr),win=(pr>0).mean() if len(pr) else np.nan,avg_net_bp=pr.mean()*1e4 if len(pr) else np.nan,avg_gross_bp=gross.mean()*1e4 if len(gross) else np.nan,
        PF=pr[pr>0].sum()/-pr[pr<0].sum() if (pr<0).any() else np.inf,CAGR=eq.iat[-1]**(1/yrs)-1,
        sharpe=r.mean()/sd*np.sqrt(BPY) if sd>0 else np.nan, sharpe_obs=r.mean()/sd*np.sqrt(bpy) if sd>0 else np.nan,
        sharpe_daily=dr.mean()/dr.std()*np.sqrt(252) if dr.std()>0 else np.nan,MDD=dd,exposure=R['w'][m].mean(),
        overnight_share=on,T=m.sum(),srd=r.mean()/sd if sd>0 else np.nan,skew=r.skew(),kurt=r.kurt()+3,tot=eq.iat[-1]-1)
