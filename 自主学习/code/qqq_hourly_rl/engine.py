import numpy as np, pandas as pd
EFFR={2014:0.09,2015:0.13,2016:0.40,2017:1.00,2018:1.83,2019:2.16,2020:0.38,2021:0.08,2022:1.68,2023:5.02,2024:5.14,2025:4.20,2026:3.80}
import os
F=os.environ.get('QVIXD','/workspace/qqq_bottom/data/full').rstrip('/')+'/'   # 日线 VIX/VIX3M 目录（可用 QVIXD 覆盖）
def vix_ratio():
    v=pd.read_csv(F+'VIX.csv',parse_dates=['time']).set_index('time').close
    v3=pd.read_csv(F+'VIX3M.csv',parse_dates=['time']).set_index('time').close
    r=(v/v3).dropna(); cut=os.environ.get('QCUT')
    return r[r.index<pd.Timestamp(cut)] if cut else r
def rsi(c,n):
    d=c.diff(); up=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return 100-100/(1+up/dn)
def load_daily():
    q=pd.read_csv(os.environ.get('QDATA','/workspace/data')+'/QQQ_daily.csv',parse_dates=['date']).set_index('date')
    q=q[q.index>='2014-06-01']; q['ratio']=vix_ratio().reindex(q.index).ffill(limit=3); return q
def load_hourly():
    h=pd.read_csv(os.environ.get('QDATA','/workspace/data')+'/QQQ_1h.csv'); h['time']=pd.to_datetime(h.time.str[:19]); h=h.set_index('time')
    h['day']=h.index.normalize()
    r=vix_ratio(); dates=sorted(h.day.unique())
    # 前一交易日收盘的 VIX/VIX3M（盘中不可得当天收盘值 -> 用前一日，防前视）
    prev=r.reindex(pd.DatetimeIndex(dates)).ffill(limit=3).shift(1)
    h['ratio_prev']=h.day.map(prev)
    return h
def run(O,C,idx,entry,exit_fn,cost=5,bpy=252):
    """entry[i] bool at close i -> buy open i+1; exit_fn(i,ei,ef)->bool at close i -> sell open i+1."""
    N=len(C); pos=np.zeros(N); trades=[]; inpos=False; pend=None
    for i in range(N):
        if pend=='in': inpos=True; ei=i; ef=O[i]; pend=None
        elif pend=='out': inpos=False; trades.append((idx[ei],idx[i],ef,O[i],i-ei)); pend=None
        pos[i]=inpos
        if i==N-1: break
        if inpos and exit_fn(i,ei,ef): pend='out'
        elif not inpos and entry[i]: pend='in'
    if inpos: trades.append((idx[ei],idx[N-1],ef,C[N-1],N-1-ei))
    return pos,trades
def returns(O,C,idx,pos,cost=5,bpy=252):
    # 收益：持仓 bar 内 open->close + 前一 bar close->open(隔夜/跨bar)，进出在 open 成交
    N=len(C); r=np.zeros(N); rf=np.array([EFFR[t.year]/100 for t in idx])/bpy
    for i in range(1,N):
        a,b=pos[i],pos[i-1]
        r[i]=b*a*(O[i]/C[i-1]-1)+a*(C[i]/O[i]-1)-abs(a-b)*cost/1e4+(1-a)*rf[i]
    return r
def metrics(r,idx,trades,pos,bpy,lo,hi):
    m=(idx>=pd.Timestamp(lo))&(idx<pd.Timestamp(hi)); rr=r[m]
    eq=np.cumprod(1+rr); yrs=m.sum()/bpy
    tr=[t for t in trades if t[0]>=pd.Timestamp(lo) and t[0]<pd.Timestamp(hi)]
    pnl=[(t[3]/t[2])*(1-5e-4)/(1+5e-4)-1 for t in tr]
    sd=rr.std()
    return dict(win=np.mean([p>0 for p in pnl]) if pnl else np.nan, n=len(tr), tot=eq[-1]-1,
        cagr=eq[-1]**(1/yrs)-1, mdd=(eq/np.maximum.accumulate(eq)-1).min(),
        sharpe=rr.mean()/sd*np.sqrt(bpy) if sd>0 else 0, expo=pos[m].mean(), avgpnl=np.mean(pnl) if pnl else np.nan)
