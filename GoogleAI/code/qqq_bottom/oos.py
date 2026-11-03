"""Backtest 12 QQQ bottom-detection models. Signals on close, fill next open (except Smash Day: stop entry/exit intraday)."""
import pandas as pd, numpy as np
D='/workspace/qqq_bottom/data/'
q=pd.read_csv('/workspace/tv_QQQ_1D_full.csv',parse_dates=['time']).set_index('time')
q.columns=[c.lower() for c in q.columns]
def ext(f): return pd.read_csv(D+f,parse_dates=['time']).set_index('time')['close']
df=q.copy()
for n,f in [('vix','VIX.csv'),('vix3m','VIX3M.csv'),('adv','ADVN_NQ.csv'),('dec','DECL_NQ.csv'),('ndfi','NDFI.csv')]:
    df[n]=ext(f).reindex(df.index).ffill()
O,H,L,C,V=df.open,df.high,df.low,df.close,df.volume
def sma(s,n): return s.rolling(n).mean()
def std(s,n): return s.rolling(n).std(ddof=0)
def rsi(s,n):  # Wilder RSI
    d=s.diff(); up=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return 100-100/(1+up/dn)
def atr(n):
    tr=pd.concat([H-L,(H-C.shift()).abs(),(L-C.shift()).abs()],axis=1).max(axis=1); return tr.ewm(alpha=1/n,adjust=False).mean()
idx=df.index; N=len(df)

def run(entry, exitf, stop_entry=None, stop_exit=None):
    """entry: bool Series (close signal). exitf(i, ei, state)->bool on close i. Returns trades and daily returns."""
    ret=np.zeros(N); inpos=np.zeros(N,bool); trades=[]; pos=False; pend_in=pend_out=False
    for i in range(1,N):
        if pend_out and pos:   # exit at open
            ret[i]=O.iat[i]/C.iat[i-1]-1; trades.append((ei,i,ep,O.iat[i])); pos=False; pend_out=False; inpos[i]=True
            continue
        if not pos:
            px=None
            if pend_in: px=O.iat[i]
            elif stop_entry is not None and not np.isnan(stop_entry[i]) and H.iat[i]>stop_entry[i]: px=max(O.iat[i],stop_entry[i])
            pend_in=False
            if px is not None:
                pos=True; ei=i; ep=px; ret[i]=C.iat[i]/px-1; inpos[i]=True
                if exitf(i,ei): pend_out=True
                continue
            if entry.iat[i] and i<N-1: pend_in=True
            continue
        inpos[i]=True
        if stop_exit is not None:
            s=stop_exit(i)
            if L.iat[i]<s:
                xp=min(O.iat[i],s); ret[i]=xp/C.iat[i-1]-1; trades.append((ei,i,ep,xp)); pos=False; continue
        ret[i]=C.iat[i]/C.iat[i-1]-1
        if exitf(i,ei): pend_out=True
    if pos: trades.append((ei,N-1,ep,C.iat[-1]))  # mark open trade at last close
    return trades, ret, inpos

M={}
# 1 RSI2
r2=rsi(C,2); s5=sma(C,5); s200=sma(C,200)
M[1]=dict(entry=(C>s200)&(r2<10), exitf=lambda i,e: C.iat[i]>s5.iat[i], start=s200.first_valid_index())
# 2 VIX stretch
s10=sma(C,10); vs=df.vix/sma(df.vix,10)
M[2]=dict(entry=(vs>=1.05)&(C<s10), exitf=lambda i,e: C.iat[i]>s10.iat[i] or i-e+1>=5, start=s10.first_valid_index())
# 3 Williams VIX Fix
hc=C.rolling(22).max(); wv=(hc-L)/hc*100; wm=sma(wv,20); wu=wm+2*std(wv,20)
M[3]=dict(entry=(wv>wu)|(wv>10), exitf=lambda i,e: wv.iat[i]<wm.iat[i] and wv.iat[i-1]>=wm.iat[i-1], start=wu.first_valid_index())
# 4 FTD: day0 = bar whose Low is the lowest Low of prior 25 bars (incl.); reset if undercut
ftd=np.zeros(N,bool); low_i=None; low_v=np.inf
ll25=L.rolling(25).min()
for i in range(25,N):
    if L.iat[i]<=ll25.iat[i]: low_i=i; low_v=L.iat[i]
    if low_i is not None and i>low_i:
        d=i-low_i
        if 4<=d<=10 and C.iat[i]/C.iat[i-1]-1>0.015 and V.iat[i]>V.iat[i-1]: ftd[i]=True; low_i=None
        elif d>10: low_i=None
ftd=pd.Series(ftd,idx); ftdlow={}
def ex4(i,e):
    # FTD bar = signal bar = e-1
    return C.iat[i]<L.iat[e-1]
M[4]=dict(entry=ftd, exitf=ex4, start=idx[25])
# 5 VIX/VIX3M
tr=df.vix/df.vix3m; r14=rsi(C,14)
M[5]=dict(entry=(tr.shift(1).rolling(5).max()>1.0)&(tr<0.95)&(tr.shift(1)>=0.95), exitf=lambda i,e: r14.iat[i]>70 or tr.iat[i]>1.0, start=tr.first_valid_index())
# 6 Zweig
ar=(df.adv/(df.adv+df.dec)).ewm(span=10,adjust=False).mean()
M[6]=dict(entry=(ar>0.61)&(ar.shift(1)<=0.61)&(ar.rolling(11).min()<0.40), exitf=lambda i,e: ar.iat[i]<0.5 and ar.iat[i-1]>=0.5, start=idx[30])
# 7 IBS
ibs=(C-L)/(H-L); s20=sma(C,20); bb2=s20-2*std(C,20)
M[7]=dict(entry=(ibs<0.05)&(C<bb2), exitf=lambda i,e: C.iat[i]>s5.iat[i] or C.iat[i]>s20.iat[i], start=s20.first_valid_index())
# 8 % above 50dma: arm when <15, signal when crosses >20 after arming
nd=df.ndfi; arm=False; sig=np.zeros(N,bool)
for i in range(1,N):
    if nd.iat[i]<15: arm=True
    if arm and nd.iat[i]>20 and nd.iat[i-1]<=20: sig[i]=True; arm=False
ll20p=L.rolling(20).min().shift(1)
M[8]=dict(entry=pd.Series(sig,idx), exitf=lambda i,e: nd.iat[i]>80 or C.iat[i]<ll20p.iat[i], start=idx[20])
# 9 Smash day: setup day close = 20d lowest close and IBS<=0.25; next day buy stop at setup high; trailing stop = lowest low of prior 3 bars
setup=(C<=C.rolling(20).min())&(ibs<=0.25)
se=np.where(setup.shift(1).fillna(False),H.shift(1),np.nan)
ll3=L.rolling(3).min().shift(1)
M[9]=dict(entry=pd.Series(False,idx), exitf=lambda i,e: False, stop_entry=se, stop_exit=lambda i: ll3.iat[i], start=idx[20])
# 10 3-day low
M[10]=dict(entry=(L<L.shift(1))&(L.shift(1)<L.shift(2))&(C>s200)&(r2<5), exitf=lambda i,e: C.iat[i]>H.iat[i-1], start=s200.first_valid_index())
# 11 ATR expansion
a14=atr(14); bb25=s20-2.5*std(C,20)
M[11]=dict(entry=(a14>=a14.rolling(20).max())&(C<bb25)&(C>C.shift(1)), exitf=lambda i,e: C.iat[i]>s20.iat[i] and C.iat[i-1]<=s20.iat[i-1], start=s20.first_valid_index())
# 12 VIX RSI2
vr=rsi(df.vix,2)
M[12]=dict(entry=(vr.shift(1).rolling(5).max()>90)&(vr<70)&(vr.shift(1)>=70), exitf=lambda i,e: vr.iat[i]<20 or i-e+1>=5, start=idx[5])

def st2(ret,a,b):
    r=pd.Series(ret,idx).loc[a:b]; eq=(1+r).cumprod()
    return (eq/eq.cummax()-1).min(), r.mean()/r.std()*np.sqrt(252) if r.std()>0 else np.nan, eq.iat[-1]-1
out=[]
for k in range(1,13):
    m=M[k]; tr_,ret,inp=run(m['entry'].fillna(False),m['exitf'],m.get('stop_entry'),m.get('stop_exit'))
    row={'model':k}
    for lab,a,b in [('IS','2016-01-01','2021-12-31'),('OOS','2022-01-01','2026-12-31')]:
        pr=np.array([x/p-1 for e,_,p,x in tr_ if a<=str(idx[e].date())<=b and idx[e]>=m['start']])
        dd,sh,tot=st2(ret,max(pd.Timestamp(a),m['start']),b)
        row.update({f'{lab}_trades':len(pr),f'{lab}_win':round((pr>0).mean(),2) if len(pr) else None,f'{lab}_sharpe':round(sh,2),f'{lab}_mdd':round(dd,3),f'{lab}_tot':round(tot,3)})
    out.append(row)
bh=(C/C.shift(1)-1).fillna(0).values
for lab,a,b in [('IS','2016','2021'),('OOS','2022','2026')]: print('BH',lab,[round(x,3) for x in st2(bh,a,b)])
o=pd.DataFrame(out); o.to_csv('oos_split.csv',index=False); print(o.to_string())
