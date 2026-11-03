"""Round 2 hourly: H1/H2/H3 hybrids on daily P2 signal; P2 baseline on the same hourly engine. 2.5bp/side, Sharpe x sqrt(1764)."""
import itertools, pickle, json
from h1 import *
from statistics import NormalDist; ND=NormalDist()
q=load(); o,h,l,c=q.open.values,q.high.values,q.low.values,q.close.values; bar=q.bar.values; last=q.last.values; first=q.first.values; N=len(q)
dates=q.date.values
dclose=q.close.groupby(q.date).last(); dclose=dclose[dclose.index<=pd.Timestamp('2026-10-29')]
F='/workspace/qqq_bottom/data/full/'
dv=pd.read_csv(F+'VIX.csv',parse_dates=['time']).set_index('time')['close']; dm=pd.read_csv(F+'VIX3M.csv',parse_dates=['time']).set_index('time')['close']
dratio=(dv/dm).reindex(dclose.index); dr2=rsi(dclose,2); ds5=sma(dclose,5)
p2sig=((dr2<15)&(dratio<1)); exitsig=(dclose>ds5)
dl=list(dclose.index); dpos={d:k for k,d in enumerate(dl)}
# per-bar: is last bar of a day with P2 signal / exit signal (evaluated at that day's close)
sig_at=np.array([last[i] and bool(p2sig.get(pd.Timestamp(dates[i]),False)) for i in range(N)])
ex_at=np.array([last[i] and bool(exitsig.get(pd.Timestamp(dates[i]),False)) for i in range(N)])
hr2=rsi(q.close,2).values
# provisional daily SMA5 during the day: (last 4 daily closes + current close)/5
prev4=pd.Series(dclose.rolling(4).sum().shift(0).values,index=dclose.index)  # sum of closes up to day k
dk=np.array([dpos.get(pd.Timestamp(d),-1) for d in dates])
def prov_s5(i):
    k=dk[i]; ref=k-1 if k>=0 else len(dl)-1   # previous completed day index (today = 10-30 not in dclose)
    if k<0: ref=len(dl)-1
    return (prev4.iloc[ref]+c[i])/5 if ref>=3 else np.nan
def sim(cost=2.5,entry_mode='p2',X=None,fb=6,cons_bp=None,unfilled='fallback',trig=None,fbh=7,Y=None,hmin=None):
    """Bar-level simulator with custom fills. Returns dict like h1.Sim.run."""
    cst=cost/1e4; r=np.zeros(N); gap=np.zeros(N); intr=np.zeros(N); w=np.zeros(N); tr=[]
    pos=0.0; ef=None; ei=None; arm=False; armday=None; limit=None; pend_out=False; pend_in=False; held=0
    for i in range(1,N):
        hld=pos; g=o[i]/c[i-1]-1
        fill_px=None
        if pend_out and pos>0:
            r[i]=hld*g - cst; gap[i]=hld*g; tr.append((ei,i,ef,o[i])); pos=0.0; pend_out=False
            b=c[i]/o[i]-1; r[i]+=0  # flat for rest of bar
            hld=0.0; # continue to entry logic below on same bar is not allowed (one action per bar open)
            if arm and first[i]: pass
            w[i]=0; 
            # allow armed entries to proceed on this bar only via limit logic below
        else:
            gap[i]=hld*g; r[i]=hld*g
        # ---- entry logic (armed after P2 signal at previous close)
        if pos==0 and arm:
            if entry_mode=='p2':
                if first[i]: fill_px=o[i]
            elif entry_mode=='h1':
                if first[i]: limit=o[i]*(1-X); 
                if bar[i]<fb and limit is not None:
                    thr=limit if cons_bp is None else limit*(1-cons_bp/1e4)
                    if o[i]<=limit and not first[i]: fill_px=o[i]
                    elif l[i]<=thr: fill_px=min(o[i],limit) if cons_bp is None else (o[i] if o[i]<=limit else limit)
                elif bar[i]==fb:
                    if unfilled=='fallback': fill_px=o[i]
                    else: arm=False
            elif entry_mode=='h2':
                if pend_in: fill_px=o[i]; pend_in=False
                elif bar[i]==fbh and not first[i]: fill_px=o[i]
            if fill_px is not None:
                pos=1.0; ef=fill_px; ei=i; arm=False; held=0
                r[i]+= (c[i]/fill_px-1) - cst; intr[i]=c[i]/fill_px-1; w[i]=1
        elif pos>0:
            r[i]+=c[i]/o[i]-1; intr[i]=c[i]/o[i]-1; w[i]=1
        if pos>0: held+=1
        # ---- signals at close i
        if entry_mode=='h2' and arm and pos==0 and bar[i]<fbh-1+1 and not pend_in and dates[i]!=armday:
            t=(c[i]>o[i]) if trig=='A' else (c[i]>h[i-1])
            if t and bar[i]<=fbh-2: pend_in=True
            elif t and bar[i]==fbh-1: pend_in=True
        if pos>0 and not pend_out:
            if ex_at[i]: pend_out=True
            elif Y is not None and held>=hmin and hr2[i]>Y and c[i]>prov_s5(i): pend_out=True
        if sig_at[i] and pos==0 and not arm: arm=True; armday=dates[i]; limit=None; pend_in=False
        if arm and last[i] and dates[i]!=armday: arm=False   # signal only valid for D1
    if pos>0: tr.append((ei,N-1,ef,c[-1]))
    return dict(r=r,gap=gap,intr=intr,w=w,tr=tr,open=pos>0,pend=None,held=None,arm=arm)
