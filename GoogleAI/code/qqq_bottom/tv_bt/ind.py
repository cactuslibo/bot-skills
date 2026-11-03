"""Faithful Python ports of TradingView Pine indicators (daily). Pine stdev = population (ddof=0); rma = Wilder."""
import pandas as pd, numpy as np
def sma(s,n): return s.rolling(n).mean()
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def rma(s,n): return s.ewm(alpha=1/n,adjust=False).mean()
def stdev(s,n): return s.rolling(n).std(ddof=0)
def rsi(s,n):
    d=s.diff(); up=rma(d.clip(lower=0),n); dn=rma(-d.clip(upper=0),n)
    r=100-100/(1+up/dn); r[dn==0]=100; r[(up==0)&(dn!=0)]=0; return r
def stoch(s,n): lo=s.rolling(n).min(); hi=s.rolling(n).max(); return 100*(s-lo)/(hi-lo)
def mfi(src,vol,n):  # Pine ta.mfi
    ch=src.diff(); pos=(vol*src).where(ch>0,0).rolling(n).sum(); neg=(vol*src).where(ch<0,0).rolling(n).sum()
    return 100-100/(1+pos/neg)
# CM_Williams_Vix_Fix_Finds_Market_Bottoms.pine
def wvf(C,L,pd_=22,bbl=20,mult=2.0,lb=50,ph=.85):
    hc=C.rolling(pd_).max(); w=(hc-L)/hc*100; mid=sma(w,bbl); up=mid+mult*stdev(w,bbl); rh=w.rolling(lb).max()*ph
    return w,mid,up,rh,(w>=up)|(w>=rh)
# MyRSI.pine / CCT_Bollinger_Band_Oscillator (same formula, len 21)
def boo(C,n=21): sd=stdev(C,n); return 100*(C+2*sd-sma(C,n))/(4*sd)
# CM_RSI-2_Strategy_Lower_Indicator.pine
def cm_rsi2_buy(C): r=rsi(C,2); return (C>sma(C,200))&(C<sma(C,5))&(r<10)
# McClellan_Oscillator_LazyBear.pine (ratio adjusted, rm=1000)
def mcclellan(a,d,rm=1000): rana=rm*(a-d)/(a+d); return ema(rana,19)-ema(rana,39)
# CM_Twiggs_Money_Flow.pine (WiMA = rma seeded at first value*1/len, approx)
def tmf(C,H,L,V,n=21):
    th=np.maximum(C.shift(),H); tl=np.minimum(C.shift(),L); tc=(th-tl).replace(0,9999999)
    adv=V*((C-tl)-(th-C))/tc
    def wima(x):
        out=np.zeros(len(x)); p=0.0
        for i,v in enumerate(np.nan_to_num(x.values)): p=(v+p*(n-1))/n; out[i]=p
        return pd.Series(out,x.index)
    wv=wima(V); return wima(adv)/wv
# My_MFI_RSI_STOCH_RSI.pine (long side)
def mfi_rsi_stoch(H,L,C,V,thr=20):
    src=(H+L+C)/3; m=mfi(src,V,14); r=rsi(src,14); r1=rsi(C,14); k=sma(stoch(r1,14),3); d=sma(k,3)
    return (m<thr)&(r<thr)&(k<thr)&(d<thr), k
# WaveTrend_with_Crosses_LazyBear.pine
def wavetrend(H,L,C,n1=10,n2=21):
    ap=(H+L+C)/3; esa=ema(ap,n1); d=ema((ap-esa).abs(),n1); ci=(ap-esa)/(0.015*d); w1=ema(ci,n2); return w1,sma(w1,4)
# Transient_Zones_v1_1.pine: PTZ low = low <= lowest(low,10); confirmed TZ low appears h_right(10) bars later
def tz_low(L,hl=10,hr=10):
    ptz=L<=L.rolling(hl).min(); tz=L.shift(hr+1)<=L.rolling(hl+hr+1).min(); return ptz,tz
