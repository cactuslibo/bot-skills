"""Gemini round-1 candidates C1-C5, exactly as specified in debate_round1_gemini.md; indicators per account Pine scripts."""
from eng2 import *
df=load_full(); O,H,L,C,V=df.open,df.high,df.low,df.close,df.volume
o,h,l,c=O.values,H.values,L.values,C.values
r2=rsi(C,2).values; s200=sma(C,200).values; s150=sma(C,150).values
SMA={n:sma(C,n).values for n in (3,4,5,6,8,10,12,15)}
ll5=L.rolling(5).min().values
ts_real=(df.vix/df.vix3m)
def wvf_up(mult):  # Pine CM_Williams_Vix_Fix: wvf, upperBand (population stdev), rangeHigh
    w,mid,up,rh,g=wvf(C,L,22,20,mult,50,.85); return w.values,up.values,rh.values
ibs=((C-L)/(H-L)).values
def tr_(): return pd.concat([H-L,(H-C.shift()).abs(),(L-C.shift()).abs()],axis=1).max(axis=1)
atr5=rma(tr_(),5); atrx=(atr5/sma(atr5,20)).values
tm=tmf(C,H,L,V,21).values; mo=mcclellan(df.adv,df.dec).values; nd=df.ndfi.values
# --- proxies for periods without VIX3M (Gemini's own proxies)
vix=df.vix
def C1(rsi_t=15,wmult=2.0,stop=0.06,bt=1.05,proxy=True,lime=False,cost=5,bull_maxd=5,bear_sma=10,bear_rsi=65):
    w,up,rh=wvf_up(wmult); tsr=ts_real.values; px=(vix/sma(vix,20)).values
    def entry(i):
        if i<200 or np.isnan(s200[i]): return None
        if c[i]>s200[i]:
            if r2[i]<rsi_t and c[i]>ll5[i]: return 'bull'
        else:
            wv=(w[i]>=up[i]) or (lime and w[i]>=rh[i])
            if np.isnan(tsr[i]):
                if not proxy: return None
                vt=px[i]>=1.25*bt/1.05
            else: vt=tsr[i]>=bt
            if wv and vt and c[i]>o[i]: return 'bear'
        return None
    def ex(i,s):
        if s['br']=='bull': return r2[i]>70 or c[i]>SMA[5][i] or i-s['ei']+1>=bull_maxd
        return c[i]>SMA[bear_sma][i] or r2[i]>bear_rsi or c[i]<s['ef']*(1-stop)
    return sim(df,entry,ex,cost)
def C2(rsi_t=15,tmf_t=-0.05,mo_t=-40,nd_t=25,maxd=6,stop=0.04,cost=5):
    def entry(i):
        if np.isnan(s200[i]): return None
        br=(mo[i]<mo_t) or (nd[i]<nd_t)   # NaN comparisons are False -> no signal before 2004
        return 'x' if (c[i]>s200[i] and r2[i]<rsi_t and tm[i]<tmf_t and br) else None
    def ex(i,s): return r2[i]>70 or c[i]>SMA[5][i] or i-s['ei']+1>=maxd or c[i]<s['ef']*(1-stop)
    return sim(df,entry,ex,cost)
def C3(bt=1.05,rsi_t=25,exs=10,maxd=8,stop=0.05,proxy=True,ibs_t=0.3,cont=0.92,cost=5):
    tsr=ts_real.values; px=(vix/sma(vix,60)).values
    real=~np.isnan(tsr); ratio=np.where(real,tsr,px); thr=np.where(real,bt,1.25*bt/1.05); ct=np.where(real,cont,cont)
    rmax3=pd.Series(ratio).rolling(3).max().values; rthr3=pd.Series(thr).rolling(3).min().values
    def entry(i):
        if i<3 or np.isnan(ratio[i]) or (not real[i] and not proxy): return None
        return 'x' if (rmax3[i]>thr[i] and ratio[i]<ratio[i-1] and r2[i]<rsi_t and ibs[i]>ibs_t) else None
    def ex(i,s): return ratio[i]<ct[i] or c[i]>SMA[exs][i] or i-s['ei']+1>=maxd or c[i]<s['ef']*(1-stop)
    return sim(df,entry,ex,cost)
def C4(blen=21,ibs_t=0.15,exs=5,atr_t=1.15,trend=150,maxd=4,cost=5):
    b=boo(C,blen).values; st=sma(C,trend).values
    def entry(i): return 'x' if (c[i]>st[i] and b[i]<0 and ibs[i]<ibs_t and atrx[i]>atr_t) else None
    def ex(i,s): return c[i]>SMA[exs][i] or b[i]>50 or i-s['ei']+1>=maxd
    return sim(df,entry,ex,cost)
def C5(rsi_t=15,wmult=2.0,maxd=5,stop=0.04,sat=0.5,cost=5,base_on=True,trigger=None,exit_rsi=70):
    """base: 1.0 if C>SMA200 (decided at close, applied next open) else 0; satellite +sat on trigger."""
    w,up,rh=wvf_up(wmult); N=len(df); tgt=np.zeros(N); tr=[]; st=None; pend=None
    trig=trigger if trigger is not None else (lambda i: r2[i]<rsi_t and w[i]>=up[i])
    for i in range(N):
        if pend=='in': st={'ei':i,'ef':o[i]}; pend=None
        elif pend=='out': tr.append((st['ei'],i,st['ef'],o[i],'sat')); st=None; pend=None
        base=1.0 if (base_on and not np.isnan(s200[i]) and c[i]>s200[i]) else (1.0 if base_on=='always' else 0.0)
        if st is None:
            if i>=200 and trig(i) and i<N-1: pend='in'; tgt[i]=base+sat
            else: tgt[i]=base
        else:
            if r2[i]>exit_rsi or i-st['ei']+1>=maxd or c[i]<st['ef']*(1-stop): pend='out'; tgt[i]=base
            else: tgt[i]=base+sat
    r,ww=returns(df,tgt,cost)
    return dict(tr=tr,r=r,w=ww,tgt=tgt,open=st is not None,pend=pend)
def bh(cost=0):
    t=np.ones(len(df)); r,w=returns(df,t,0); return dict(tr=[(0,len(df)-1,o[0],c[-1],'bh')],r=r,w=w,tgt=t,open=True,pend=None)
