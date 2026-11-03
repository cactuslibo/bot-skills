"""Gemini M1-M10 + own T1-T5 on hourly QQQ. See tv_round1.md for interpretation of ambiguous rules."""
import itertools, json, pickle
from h1 import *
from statistics import NormalDist; ND=NormalDist()
q=load(); O,H,L,C,V=q.open,q.high,q.low,q.close,q.volume
o,h,l,c,v=O.values,H.values,L.values,C.values,V.values; bar=q.bar.values; last=q.last.values; first=q.first.values; N=len(q)
r2=rsi(C,2).values; r14=rsi(C,14).values; ibs=((C-L)/(H-L)).fillna(0.5).values
SMA=lambda n: sma(C,n).values
prevclose=C.groupby(q.date).transform('last').shift(1)   # placeholder (fixed below)
dclose=C.groupby(q.date).last(); dopen=O.groupby(q.date).first()
pdc=q.date.map(dclose.shift(1)).values      # previous session close
gap1=q.date.map(dopen/dclose.shift(1)-1).values
dsma5=q.date.map(sma(dclose,5)).values; dcl=q.date.map(dclose).values  # only used on last bar of day
def mk(f): return f
M={}
# M1
def M1(gap=-0.005,rt=10,sm=20,hold=5):
    s=SMA(sm)
    return dict(entry=lambda i: bar[i]==1 and gap1[i]<gap and r2[i]<rt, exitf=lambda i,st: c[i]>s[i] or i-st['ei']+1>=hold)
# M2 session VWAP (hlc3*vol cumulative per session); Stdev(VWAP,20) := rolling 20-bar population stdev of (Close-VWAP)
tp=(H+L+C)/3; cum=lambda x: x.groupby(q.date).cumsum()
vwap=(cum(tp*V)/cum(V)).values
def M2(th=-2.0,vl=20,sdl=20,sdmode='dev'):
    dev=pd.Series(c-vwap,q.index); sd=stdev(dev,sdl).values if sdmode=='dev' else stdev(C,sdl).values
    z=(c-vwap)/sd; vs=sma(V,vl).values
    return dict(entry=lambda i: bar[i]<7 and not last[i] and z[i]<th and v[i]>vs[i], exitf=lambda i,st: c[i]>=vwap[i], moc=lambda i,st: last[i])
# M3
def M3(dt=1.0,rt=5,it=0.1):
    s5=SMA(5)
    return dict(entry=lambda i: q.dratio_prev.values[i]<dt and r2[i]<rt and ibs[i]<it,
                exitf=lambda i,st: c[i]>s5[i] or (last[i] and c[i]>dsma5[i]))
# M4 hourly VIX/VIX3M: spike >sp within previous 14 bars, then today's bar crosses below rv
ratio=(q.vix/q.vix3m).values
def M4(sp=1.02,rv=0.99,win=14,hold=7):
    mx=pd.Series(ratio).shift(1).rolling(win).max().values
    return dict(entry=lambda i: i>0 and mx[i]>sp and ratio[i]<rv and ratio[i-1]>=rv, exitf=lambda i,st: i-st['ei']+1>=hold)
# M5: signal at close of bar 3 (12:30) and/or bar 4 (13:30); exit MOC at bar-7 close
def M5(rt=15,bars=(3,4)):
    return dict(entry=lambda i: bar[i] in bars and r2[i]<rt and not last[i], exitf=lambda i,st: False, moc=lambda i,st: last[i])
# M6 WVF hourly (Pine: highest close 22, population stdev); Gemini: upper band only
def M6(bbl=20,mult=2.0,hold=3,lime=False):
    hc=C.rolling(22).max(); w=((hc-L)/hc*100); up=(sma(w,bbl)+mult*stdev(w,bbl)).values; rh=(w.rolling(50).max()*.85).values; w=w.values
    return dict(entry=lambda i: (w[i]>=up[i] or (lime and w[i]>=rh[i])) and c[i]>o[i], exitf=lambda i,st: r2[i]>70 or i-st['ei']+1>=hold)
# M7 NR: range < min(range of previous k bars) (current bar excluded)
rng=(H-L); trr=pd.concat([H-L,(H-C.shift()).abs(),(L-C.shift()).abs()],axis=1).max(axis=1); atr14=rma(trr,14).values
def M7(k=7,it=0.15,hold=4,atrm=1.0):
    mn=rng.shift(1).rolling(k).min().values; s2=SMA(200); rg=rng.values
    return dict(entry=lambda i: rg[i]<mn[i] and ibs[i]<it and c[i]>s2[i],
                exitf=lambda i,st: c[i]>h[st['sig']]+atrm*atr14[st['sig']] or i-st['ei']+1>=hold)
def M8(t14=35,t2=10):
    s2=SMA(200); s10=SMA(10)
    return dict(entry=lambda i: c[i]>s2[i] and r14[i]<t14 and r2[i]<t2, exitf=lambda i,st: c[i]>s10[i] or r2[i]>60)
# M9 bar6 (14:30-15:30) close: low < lowest(low of previous k bars), green; optional lower-wick >= x of range; exit = fill at next day's bar-2 open
def M9(k=5,wick=None):
    mn=L.shift(1).rolling(k).min().values; lw=((np.minimum(o,c)-l)/(h-l+1e-12))
    return dict(entry=lambda i: bar[i]==6 and l[i]<mn[i] and c[i]>o[i] and (wick is None or lw[i]>=wick),
                exitf=lambda i,st: bar[i]==1 and i>st['ei'])
def M10(k=10,rp=14,hold=10):
    rr=rsi(C,rp); ll=L.shift(1).rolling(k).min().values; rl=rr.shift(1).rolling(k).min().values; rr=rr.values
    return dict(entry=lambda i: l[i]<ll[i] and rr[i]>rl[i], exitf=lambda i,st: r2[i]>75 or i-st['ei']+1>=hold)
# ---- own proposals from account Pine scripts
dpc=q.date.map(dclose.shift(1)).values
d_r2=q.date.map(rsi(dclose,2).shift(1)).values      # yesterday's daily RSI2 (known pre-session)
dS200=q.date.map(sma(dclose,200).shift(1)).values
def T1(rt=10,dt=1.0):   # CM_RSI-2 lime on 1h + daily VIX term-structure filter; exit C>SMA5 (CM rule)
    s200=SMA(200); s5=SMA(5)
    return dict(entry=lambda i: c[i]>s200[i] and c[i]<s5[i] and r2[i]<rt and q.dratio_prev.values[i]<dt, exitf=lambda i,st: c[i]>s5[i])
def T2(mult=2.0,lime=True,dt=1.0):  # CM_Williams_Vix_Fix (Pine lime incl. rangeHigh) + daily ratio<1, exit RSI2>70
    hc=C.rolling(22).max(); w=((hc-L)/hc*100); up=(sma(w,20)+mult*stdev(w,20)).values; rh=(w.rolling(50).max()*.85).values; w=w.values
    return dict(entry=lambda i: (w[i]>=up[i] or (lime and w[i]>=rh[i])) and q.dratio_prev.values[i]<dt, exitf=lambda i,st: r2[i]>70)
def T3(n=21,th=0,ex=50):   # MyRSI / CCT_BOO on 1h: boo<th with daily close>SMA200; exit boo>ex
    b=boo(C,n).values
    return dict(entry=lambda i: b[i]<th and dpc[i]>dS200[i], exitf=lambda i,st: b[i]>ex)
mo=mcclellan(q.ADVN_NQ,q.DECL_NQ).values
def T4(mt=-150,rt=10):    # McClellan_Oscillator_LazyBear on hourly Nasdaq breadth (RANA) + RSI2; exit C>SMA5
    s5=SMA(5)
    return dict(entry=lambda i: mo[i]<mt and r2[i]<rt, exitf=lambda i,st: c[i]>s5[i])
def T5(rt=15,dt=1.0):     # daily P2 executed on hourly bars: signal at close of bar 6 (15:30) using bar-6 close as provisional daily close; buy bar-7 open; exit when bar-6 close > provisional SMA5 -> sell bar-7 open
    # provisional daily series: past 4 daily closes + current bar-6 close
    dc=dclose.values; dmap={d:k for k,d in enumerate(dclose.index)}; di=np.array([dmap[d] for d in q.date])
    def prov(i):
        k=di[i]; hist=dc[max(0,k-30):k]; s=np.append(hist,c[i]); return s
    cache={}
    def feats(i):
        if i in cache: return cache[i]
        s=pd.Series(prov(i)); rr=rsi(s,2).iat[-1]; m5=s.iloc[-5:].mean(); cache[i]=(rr,m5); return cache[i]
    tr_=q.vix.values/q.vix3m.values
    rlive=np.where(np.isnan(tr_),q.dratio_prev.values,tr_)   # use live hourly ratio when available (2020+), else yesterday's daily ratio
    return dict(entry=lambda i: bar[i]==6 and feats(i)[0]<rt and rlive[i]<dt, exitf=lambda i,st: bar[i]==6 and c[i]>feats(i)[1])
BASE={'M1':{}, 'M2':{}, 'M3':{}, 'M4':{}, 'M5':{}, 'M6':{}, 'M7':{}, 'M8':{}, 'M9':{}, 'M10':{}}
GRID={'M1':dict(gap=[-0.003,-0.005,-0.007],rt=[5,10,15]),'M2':dict(th=[-1.8,-2.0,-2.2],vl=[10,20,30]),'M3':dict(dt=[0.95,1.0],rt=[2,5,10]),
      'M4':dict(sp=[1.01,1.03],rv=[0.98,1.0]),'M5':dict(rt=[10,15,20],bars=[(3,),(4,)]),'M6':dict(mult=[1.8,2.0,2.2],bbl=[10,20]),
      'M7':dict(k=[7,10,14],it=[0.1,0.2]),'M8':dict(t14=[30,35,40],t2=[5,10]),'M9':dict(k=[5,10],wick=[0.5,0.7]),'M10':dict(k=[10,20],rp=[10,14])}
FN={'M1':M1,'M2':M2,'M3':M3,'M4':M4,'M5':M5,'M6':M6,'M7':M7,'M8':M8,'M9':M9,'M10':M10}
OWN={'T1':(T1,dict(rt=[5,10],dt=[0.95,1.0])),'T2':(T2,dict(mult=[1.8,2.0,2.2],lime=[True,False])),'T3':(T3,dict(th=[0,-10],ex=[50,80])),
     'T4':(T4,dict(mt=[-100,-150,-200],rt=[10,20])),'T5':(T5,dict(rt=[10,15,20]))}
