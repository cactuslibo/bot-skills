# 指标实现（纯 pandas/numpy，默认参数）。每个函数返回已平稳化的序列，命名后缀说明变换。
import numpy as np, pandas as pd
def sma(x,n): return x.rolling(n).mean()
def ema(x,n): return x.ewm(span=n,adjust=False).mean()
def rma(x,n): return x.ewm(alpha=1/n,adjust=False).mean()
def wma(x,n):
    w=np.arange(1,n+1); return x.rolling(n).apply(lambda a:(a*w).sum()/w.sum(),raw=True)
def tr(h,l,c): pc=c.shift(); return pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1)
def linreg(x,n):
    t=np.arange(n); tm=t.mean(); tv=((t-tm)**2).sum()
    slope=x.rolling(n).apply(lambda a:((t-tm)*(a-a.mean())).sum()/tv,raw=True)
    inter=sma(x,n)-slope*tm
    return slope,inter+slope*(n-1),inter+slope*n
def rollcorr_t(x,n):
    t=pd.Series(np.arange(len(x)),index=x.index,dtype=float); return x.rolling(n).corr(t)
def kama(c,n=10,f=2,s=30):
    er=(c-c.shift(n)).abs()/(c.diff().abs().rolling(n).sum())
    sc=(er*(2/(f+1)-2/(s+1))+2/(s+1))**2
    out=np.full(len(c),np.nan); cv=c.values; scv=sc.values
    for i in range(len(c)):
        if np.isnan(scv[i]): continue
        out[i]=cv[i] if np.isnan(out[i-1]) else out[i-1]+scv[i]*(cv[i]-out[i-1])
    return pd.Series(out,c.index),er
def supersmoother(x,n=10):
    a=np.exp(-1.414*np.pi/n); b=2*a*np.cos(1.414*np.pi/n); c2=b; c3=-a*a; c1=1-c2-c3
    v=x.values; o=np.copy(v).astype(float)
    for i in range(2,len(v)):
        if np.isnan(v[i]) or np.isnan(v[i-1]): continue
        o[i]=c1*(v[i]+v[i-1])/2+c2*o[i-1]+c3*o[i-2]
    return pd.Series(o,x.index)
def psar(h,l,af0=.02,step=.02,mx=.2):
    H,L=h.values,l.values; n=len(H); s=np.full(n,np.nan); up=True; af=af0; ep=H[0]; sar=L[0]
    for i in range(1,n):
        sar=sar+af*(ep-sar)
        if up:
            sar=min(sar,L[i-1],L[i-2] if i>1 else L[i-1])
            if L[i]<sar: up=False; sar=ep; ep=L[i]; af=af0
            elif H[i]>ep: ep=H[i]; af=min(af+step,mx)
        else:
            sar=max(sar,H[i-1],H[i-2] if i>1 else H[i-1])
            if H[i]>sar: up=True; sar=ep; ep=H[i]; af=af0
            elif L[i]<ep: ep=L[i]; af=min(af+step,mx)
        s[i]=sar
    return pd.Series(s,h.index)
def mcginley(c,n=10):
    v=c.values; o=np.full(len(v),np.nan); o[0]=v[0]
    for i in range(1,len(v)): o[i]=o[i-1]+(v[i]-o[i-1])/(n*(v[i]/o[i-1])**4)
    return pd.Series(o,c.index)
def frama(c,h,l,n=16):
    hh1=h.rolling(n//2).max(); ll1=l.rolling(n//2).min()
    n1=(hh1-ll1)/(n/2); n2=(hh1.shift(n//2)-ll1.shift(n//2))/(n/2); n3=(h.rolling(n).max()-l.rolling(n).min())/n
    D=(np.log(n1+n2)-np.log(n3))/np.log(2); a=np.exp(-4.6*(D-1)).clip(.01,1).values
    v=c.values; o=np.full(len(v),np.nan)
    for i in range(len(v)):
        if np.isnan(a[i]): continue
        o[i]=v[i] if np.isnan(o[i-1]) else a[i]*v[i]+(1-a[i])*o[i-1]
    return pd.Series(o,c.index)
def alma(c,n=9,off=.85,sig=6):
    m=off*(n-1); s=n/sig; w=np.exp(-((np.arange(n)-m)**2)/(2*s*s)); w/=w.sum()
    return c.rolling(n).apply(lambda a:(a*w).sum(),raw=True)
def hurst(x,n=100):
    def h(a):
        lags=[2,4,8,16,32]; tau=[np.std(a[l:]-a[:-l]) for l in lags]
        return np.polyfit(np.log(lags),np.log(tau),1)[0]
    return np.log(x).rolling(n).apply(h,raw=True)
def entropy(r,n=20,b=10):
    # 固定分箱：收益先除以前一日为止的 252 日滚动标准差（无前视），再落入固定边界 [-3σ,3σ] 等宽 10 箱（两端截断）
    z=(r/r.rolling(252).std().shift(1)).clip(-2.999,2.999); edges=np.linspace(-3,3,b+1)
    def e(a):
        p,_=np.histogram(a,bins=edges); p=p[p>0]/p.sum(); return -(p*np.log(p)).sum()
    return z.rolling(n).apply(e,raw=True)

def compute(df, mkt=None, vix=None, irx=None):
    o,h,l,c,v=[df[k] for k in ['Open','High','Low','Close','Volume']]
    v=v.replace(0,np.nan); r=np.log(c).diff(); tp=(h+l+c)/3; mp=(h+l)/2; R={}
    M,T,VOL,VP,MS,OT={},{},{},{},{},{}
    # ---------- 动量/震荡 ----------
    d=c.diff(); up=d.clip(lower=0); dn=(-d).clip(lower=0)
    M['RSI14']=100-100/(1+rma(up,14)/rma(dn,14))
    hh14=h.rolling(14).max(); ll14=l.rolling(14).min()
    k=100*(c-ll14)/(hh14-ll14); M['Stoch_K']=sma(k,3)  # slow %K(14,3)
    M['Stoch_D']=sma(M['Stoch_K'],3); M['KDJ_J']=3*M['Stoch_K']-2*M['Stoch_D']
    M['WilliamsR14']=-100*(hh14-c)/(hh14-ll14)
    mad=tp.rolling(20).apply(lambda a:np.abs(a-a.mean()).mean(),raw=True)
    M['CCI20']=(tp-sma(tp,20))/(0.015*mad)
    M['ROC10']=c/c.shift(10)-1; M['MTM10/C']=(c-c.shift(10))/c
    M['CMO14']=100*(up.rolling(14).sum()-dn.rolling(14).sum())/(up.rolling(14).sum()+dn.rolling(14).sum())
    M['AO/C']=(sma(mp,5)-sma(mp,34))/c
    M['BOP']=((c-o)/(h-l)).replace([np.inf,-np.inf],np.nan)
    M['PSY12']=(d>0).astype(float).rolling(12).mean()
    M['BIAS20']=c/sma(c,20)-1
    num=(c-o)+2*(c-o).shift(1)+2*(c-o).shift(2)+(c-o).shift(3); den=(h-l)+2*(h-l).shift(1)+2*(h-l).shift(2)+(h-l).shift(3)
    M['RVGI10']=num.rolling(10).sum()/den.rolling(10).sum()
    e3=ema(ema(ema(c,15),15),15); M['TRIX15']=e3.pct_change()
    M['DPO20/C']=(c-sma(c,20).shift(11))/c
    x=((mp-mp.rolling(10).min())/(mp.rolling(10).max()-mp.rolling(10).min())-.5)*2
    xv=x.values; val=np.full(len(xv),np.nan); f=np.full(len(xv),np.nan); pv=0; pf=0
    for i in range(len(xv)):
        if np.isnan(xv[i]): continue
        pv=np.clip(0.33*xv[i]+0.67*pv,-.999,.999); pf=0.5*np.log((1+pv)/(1-pv))+0.5*pf; f[i]=pf
    M['Fisher9']=pd.Series(f,c.index)
    w=np.arange(1,11); M['COG10']=-mp.rolling(10).apply(lambda a:(a[::-1]*w).sum()/a.sum(),raw=True)
    M['TSI25_13']=100*ema(ema(d,25),13)/ema(ema(d.abs(),25),13)
    hh=h.rolling(10).max(); ll=l.rolling(10).min(); rel=c-(hh+ll)/2
    M['SMI10']=100*ema(ema(rel,3),3)/(0.5*ema(ema(hh-ll,3),3))
    roc1=c.pct_change()*100; M['PMO']=ema(10*ema(roc1,35),20)  # 近似：EMA 替代定制平滑
    M['PPO12_26']=(ema(c,12)-ema(c,26))/ema(c,26); M['APO/C']=(ema(c,12)-ema(c,26))/c
    _,tsf,_=None,None,None
    sl,lr,ts=linreg(c,14); M['CFO14']=(c-ts.shift(1))/c
    dmax=(h-h.shift()).clip(lower=0); dmin=(l.shift()-l).clip(lower=0)
    M['DeMarker14']=sma(dmax,14)/(sma(dmax,14)+sma(dmin,14))
    M['Qstick8/C']=sma(c-o,8)/c
    M['AR26']=(h-o).rolling(26).sum()/(o-l).rolling(26).sum()
    M['BR26']=(h-c.shift()).clip(lower=0).rolling(26).sum()/(c.shift()-l).clip(lower=0).rolling(26).sum()
    mid=tp.shift(); M['CR26']=(h-mid).clip(lower=0).rolling(26).sum()/(mid-l).clip(lower=0).rolling(26).sum()
    # Swing Index (Wilder, limit move 用 ATR 替代——见报告)
    pc,po=c.shift(),o.shift(); A=(h-pc).abs(); B=(l-pc).abs(); C_=(h-l); D_=(pc-po).abs()
    Rr=np.where((A>=B)&(A>=C_),A-0.5*B+0.25*D_,np.where((B>=A)&(B>=C_),B-0.5*A+0.25*D_,C_+0.25*D_))
    Kk=np.maximum(A,B); Lm=3*sma(tr(h,l,c),14)
    M['SwingIndex']=50*((c-pc)+0.5*(c-o)+0.25*(pc-po))/pd.Series(Rr,c.index).replace(0,np.nan)*Kk/Lm
    M['IBS']=((c-l)/(h-l)).replace([np.inf,-np.inf],np.nan)
    atr14=rma(tr(h,l,c),14)
    # RWI：对 i=2..14 逐个计算后取最大值（原始定义出处未核实）
    t_rw=tr(h,l,c); hs_,ls2=[],[]
    for i in range(2,15):
        ai=rma(t_rw,i)*np.sqrt(i); hs_.append((h-l.shift(i))/ai); ls2.append((h.shift(i)-l)/ai)
    M['RWI_high14']=pd.concat(hs_,axis=1).max(axis=1); M['RWI_low14']=pd.concat(ls2,axis=1).max(axis=1)
    M['CTI12']=rollcorr_t(c,12)
    e13=ema(c,13); M['BullPower/C']=(h-e13)/c; M['BearPower/C']=(l-e13)/c
    sgn=np.sign(r); same=(sgn==sgn.shift()).astype(float); M['Momersion20']=same.rolling(20).mean()
    # ---------- 趋势/均线：价格水平型 → MA/C−1 ----------
    def lv(name,s): T[name]=s/c-1
    lv('SMA20',sma(c,20)); lv('EMA20',ema(c,20)); lv('WMA20',wma(c,20)); lv('RMA14',rma(c,14))
    e1=ema(c,20); e2=ema(e1,20); lv('DEMA20',2*e1-e2); lv('TEMA20',3*e1-3*e2+ema(e2,20))
    lv('TRIMA20',sma(sma(c,10),11)); km,er=kama(c); lv('KAMA10',km); T['EffRatio10']=er
    lv('HMA20',wma(2*wma(c,10)-wma(c,20),4)); lv('ALMA9',alma(c)); lv('VWMA20',(c*v).rolling(20).sum()/v.rolling(20).sum())
    def t3(x,n=5,a=.7):
        e=[x]; 
        for _ in range(6): e.append(ema(e[-1],n))
        c1=-a**3; c2=3*a*a+3*a**3; c3=-6*a*a-3*a-3*a**3; c4=1+3*a+a**3+3*a*a
        return c1*e[6]+c2*e[5]+c3*e[4]+c4*e[3]
    lv('T3_5',t3(c)); lv('ZLEMA20',ema(c+(c-c.shift(9)),20)); lv('FRAMA16',frama(c,h,l)); lv('McGinley10',mcginley(c))
    sl,lr,ts=linreg(c,14); lv('LSMA14',lr); T['LinRegSlope14/C']=sl/c; T['LinRegR2_14']=rollcorr_t(c,14)**2
    lv('SuperSmoother10',supersmoother(c))
    # Roofing/高通（Ehlers 2-pole highpass 48）
    a1=(np.cos(.707*2*np.pi/48)+np.sin(.707*2*np.pi/48)-1)/np.cos(.707*2*np.pi/48)
    cv=c.values; hp=np.zeros(len(cv))
    for i in range(2,len(cv)): hp[i]=(1-a1/2)**2*(cv[i]-2*cv[i-1]+cv[i-2])+2*(1-a1)*hp[i-1]-(1-a1)**2*hp[i-2]
    T['EhlersHighPass48/C']=pd.Series(hp,c.index)/c
    ss=supersmoother(c,20); slope=(ss.shift(20)-ss)/20
    T['Trendflex20/C']=(sum((ss-ss.shift(i)) for i in range(1,21))/20)/c
    T['MACD/C']=(ema(c,12)-ema(c,26))/c; T['MACDsig/C']=ema(T['MACD/C'],9); T['MACDhist/C']=T['MACD/C']-T['MACDsig/C']
    T['DMA10_50/C']=(sma(c,10)-sma(c,50))/c
    pdm=np.where((dmax>dmin)&(dmax>0),dmax,0); mdm=np.where((dmin>dmax)&(dmin>0),dmin,0)
    pdi=100*rma(pd.Series(pdm,c.index),14)/atr14; mdi=100*rma(pd.Series(mdm,c.index),14)/atr14
    dx=100*(pdi-mdi).abs()/(pdi+mdi); T['+DI14']=pdi; T['-DI14']=mdi; T['ADX14']=rma(dx,14)
    T['AroonUp25']=h.rolling(26).apply(lambda a:a.argmax(),raw=True)/25*100
    T['AroonDn25']=l.rolling(26).apply(lambda a:a.argmin(),raw=True)/25*100; T['AroonOsc25']=T['AroonUp25']-T['AroonDn25']
    lv('PSAR',psar(h,l))
    vmp=(h-l.shift()).abs().rolling(14).sum(); vmm=(l-h.shift()).abs().rolling(14).sum(); trs=tr(h,l,c).rolling(14).sum()
    T['Vortex+14']=vmp/trs; T['Vortex-14']=vmm/trs
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    lv('Ichi_Tenkan',ten); lv('Ichi_Kijun',kij); lv('Ichi_SpanA',((ten+kij)/2).shift(26)); lv('Ichi_SpanB',((h.rolling(52).max()+l.rolling(52).min())/2).shift(26))
    T['VHF28']=(c.rolling(28).max()-c.rolling(28).min())/c.diff().abs().rolling(28).sum()
    T['CHOP14']=100*np.log10(tr(h,l,c).rolling(14).sum()/(h.rolling(14).max()-l.rolling(14).min()))/np.log10(14)
    er9=ema(h-l,9); T['MassIndex25']=(er9/ema(er9,9)).rolling(25).sum()
    lv('DonchianUp20',h.rolling(20).max()); lv('DonchianLo20',l.rolling(20).min()); lv('DonchianMid20',(h.rolling(20).max()+l.rolling(20).min())/2)
    hs,ls_=sma(h,3).shift(),sma(l,3).shift(); st=np.where(c>hs,1,np.where(c<ls_,-1,np.nan)); st=pd.Series(st,c.index).ffill()
    lv('GannHiLo3',pd.Series(np.where(st>0,sma(l,3),sma(h,3)),c.index))
    # ---------- 波动率：取对数 ----------
    t_=tr(h,l,c); VOL['log_TR/C']=np.log(t_/c); VOL['log_NATR14']=np.log(atr14/c)
    sd=c.rolling(20).std(); VOL['BB_pctb']=(c-(sma(c,20)-2*sd))/(4*sd); VOL['log_BBW20']=np.log(4*sd/sma(c,20))
    VOL['log_KeltnerW20']=np.log(4*rma(t_,10)/ema(c,20))  # 2×ATR10
    VOL['log_StdDev20/C']=np.log(sd/c); VOL['log_HV20']=np.log(r.rolling(20).std()*np.sqrt(252))
    ehl=ema(h-l,10); VOL['ChaikinVol10']=ehl/ehl.shift(10)-1
    dd=100*(c/c.rolling(14).max()-1); VOL['log_Ulcer14']=np.log(np.sqrt((dd**2).rolling(14).mean())+1e-6)
    hl=np.log(h/l); co=np.log(c/o)
    VOL['log_Parkinson20']=0.5*np.log((hl**2).rolling(20).mean()/(4*np.log(2)))
    VOL['log_GarmanKlass20']=0.5*np.log((0.5*hl**2-(2*np.log(2)-1)*co**2).rolling(20).mean())
    rs=np.log(h/c)*np.log(h/o)+np.log(l/c)*np.log(l/o); VOL['log_RogersSatchell20']=0.5*np.log(rs.rolling(20).mean())
    VOL['GAPO5/C']=np.log((h.rolling(5).max()-l.rolling(5).min())/c)/np.log(5)  # 价格归一化版本：原式 ln(HH−LL)/ln(n) 中的区间先除以收盘价
    therm=pd.concat([(h-h.shift()).abs(),(l.shift()-l).abs()],axis=1).max(axis=1)
    VOL['log_ElderThermo/C']=np.log(therm/c+1e-6)
    VOL['log_ADR20/C']=np.log(sma(h-l,20)/c); VOL['log_MAD20/C']=np.log(c.rolling(20).apply(lambda a:np.abs(a-a.mean()).mean(),raw=True)/c)
    if vix is not None: VOL['log_VIX']=np.log(vix.reindex(c.index))
    # ---------- 成交量/量价：累积型做差分 ----------
    obv=(np.sign(d)*v).fillna(0).cumsum(); VP['OBVdev20']=(obv-sma(obv,20))/(sma(v,20)*np.sqrt(20))
    clv=((c-l)-(h-c))/(h-l); clv=clv.replace([np.inf,-np.inf],np.nan).fillna(0)
    ad=(clv*v).cumsum(); VP['ADdev20']=(ad-sma(ad,20))/(sma(v,20)*np.sqrt(20))
    VP['II%21']=(clv*v).rolling(21).sum()/v.rolling(21).sum()  # 与 CMF21 定义相同
    VP['CMF20']=(clv*v).rolling(20).sum()/v.rolling(20).sum()
    rmf=tp*v; pos=rmf.where(tp>tp.shift(),0); neg=rmf.where(tp<tp.shift(),0)
    VP['MFI14']=100-100/(1+pos.rolling(14).sum()/neg.rolling(14).sum())
    VP['VWAP20dev']=c/((tp*v).rolling(20).sum()/v.rolling(20).sum())-1  # 日线无法算日内 VWAP，用滚动 20 日 VWAP
    VP['Force13/(C·V20)']=ema(d*v,13)/(c*sma(v,20))
    emv=((h+l)/2-(h.shift()+l.shift())/2)/((v/1e8)/(h-l)); VP['EMV14/C']=sma(emv,14)/c
    pvt=(c.pct_change()*v).cumsum(); VP['PVTdev20']=(pvt-sma(pvt,20))/(sma(v,20)*np.sqrt(20))
    nv=np.where(v<v.shift(),c.pct_change(),0); pvv=np.where(v>v.shift(),c.pct_change(),0)
    nvi=pd.Series(np.cumprod(1+np.nan_to_num(nv)),c.index); pvi=pd.Series(np.cumprod(1+np.nan_to_num(pvv)),c.index)
    VP['dlogNVI']=np.log(nvi).diff(); VP['dlogPVI']=np.log(pvi).diff()
    trend=np.sign(tp.diff()); dm=h-l; vf=v*trend*100  # Klinger 简化版（常见实现）
    VP['Klinger/V20']=(ema(vf,34)-ema(vf,55))/sma(v,20)
    VP['PVO12_26']=(ema(v,12)-ema(v,26))/ema(v,26)
    VP['VolROC14']=np.log(v/v.shift(14))
    # 量价分布：日线下用 20 日按价格分箱的 POC 偏离
    trl=np.minimum(l,c.shift()); trh=np.maximum(h,c.shift())
    wad=np.where(c>c.shift(),c-trl,np.where(c<c.shift(),c-trh,0)); VP['dWAD/C']=pd.Series(wad,c.index)/c
    VP['log_BW_MFI']=np.log(((h-l)/v).replace(0,np.nan)/c)
    uv=v.where(d>0,0).rolling(26).sum(); dv=v.where(d<0,0).rolling(26).sum(); fv=v.where(d==0,0).rolling(26).sum()
    VP['VR26']=(uv+fv/2)/(dv+fv/2)
    VP['WVAD24/V']=(((c-o)/(h-l)).replace([np.inf,-np.inf],np.nan)*v).rolling(24).sum()/v.rolling(24).sum()
    VP['log_RVOL20']=np.log(v/sma(v,20))
    VP['TSV18/V']=(d*v).rolling(18).sum()/(c*v.rolling(18).sum())
    # ---------- 微观结构/流动性 ----------
    dc=c.diff(); cov=dc.rolling(21).cov(dc.shift()); MS['RollSpread21/C']=np.sqrt((-cov).clip(lower=0))*2/c
    MS['log_Amihud21']=np.log((r.abs()/(c*v)).rolling(21).mean()*1e9+1e-12)
    sv=np.sign(r)*np.sqrt(c*v); MS['KyleLambda60']=r.rolling(60).cov(sv)/sv.rolling(60).var()
    b=(np.log(h/l)**2)+(np.log(h.shift()/l.shift())**2); g=np.log(np.maximum(h,h.shift())/np.minimum(l,l.shift()))**2
    al=(np.sqrt(2*b)-np.sqrt(b))/(3-2*np.sqrt(2))-np.sqrt(g/(3-2*np.sqrt(2))); cs=2*(np.exp(al)-1)/(1+np.exp(al))
    MS['CorwinSchultz21']=cs.clip(lower=0).rolling(21).mean()
    # P-S：超额收益 = 简单收益 − 无风险日收益（^IRX 年化贴现率/100/252，前值填充）
    rf=(irx.reindex(c.index).ffill()/100/252) if irx is not None else 0
    ex=c.pct_change()-rf
    X1=c.pct_change().shift(); X2=(np.sign(ex)*c*v).shift()/1e9  # PS 原式：r^e_t ~ r_{t-1} + sign(r^e_{t-1})·DV_{t-1}（DV 以十亿美元计）
    # 滚动 60 日回归，取 γ
    Y=ex.values; A1=X1.values; A2=X2.values; gm=np.full(len(Y),np.nan)
    for i in range(60,len(Y)):
        yy=Y[i-59:i+1]; xx=np.column_stack([np.ones(60),A1[i-59:i+1],A2[i-59:i+1]]); m=~np.isnan(xx).any(1)&~np.isnan(yy)
        if m.sum()>30: gm[i]=np.linalg.lstsq(xx[m],yy[m],rcond=None)[0][2]
    MS['PastorStambaugh60']=pd.Series(gm,c.index)
    MS['log_DollarVol']=np.log(c*v)  # 换手率需流通股本，用美元成交额代理（见报告）
    lv2=lambda s:s/c-1; MS['TWAP20dev(OHLC4)']=c/sma((o+h+l+c)/4,20)-1
    # ---------- 其他 ----------
    OT['TypPrice/C']=tp/c-1; OT['MedPrice/C']=mp/c-1; OT['WClose/C']=(h+l+2*c)/4/c-1; OT['AvgPrice/C']=(o+h+l+c)/4/c-1
    pp=((h+l+c)/3).shift(); OT['PivotPP/C']=pp/c-1; OT['PivotR1/C']=(2*pp-l.shift())/c-1; OT['PivotS1/C']=(2*pp-h.shift())/c-1
    hh52=h.rolling(52).max(); ll52=l.rolling(52).min(); OT['FibPos52']=(c-ll52)/(hh52-ll52)
    OT['Zscore20']=(c-sma(c,20))/c.rolling(20).std()
    if mkt is not None:
        mr=np.log(mkt.reindex(c.index)).diff(); OT['Beta60']=r.rolling(60).cov(mr)/mr.rolling(60).var(); OT['Corr60']=r.rolling(60).corr(mr)
        OT['dlogPriceRel']=r-mr
    OT['Skew20']=r.rolling(20).skew(); OT['Kurt20']=r.rolling(20).kurt(); OT['PctRank20']=c.rolling(20).rank(pct=True)
    OT['MedianDev20']=c/c.rolling(20).median()-1; OT['Entropy20']=entropy(r); OT['Hurst100']=hurst(c)
    OT['MaxDD252']=c.rolling(252).apply(lambda a:np.min(a/np.maximum.accumulate(a)-1),raw=True); OT['LogRet1']=r
    hac=(o+h+l+c)/4; hao=np.full(len(c),np.nan); hao[0]=(o.iloc[0]+c.iloc[0])/2; hv=hac.values
    for i in range(1,len(c)): hao[i]=(hao[i-1]+hv[i-1])/2
    OT['HA_body/C']=(hac-pd.Series(hao,c.index))/c
    up4=(c>c.shift(4)).astype(int); dn4=(c<c.shift(4)).astype(int)
    def cnt(s):
        o_=np.zeros(len(s)); 
        for i in range(1,len(s)): o_[i]=o_[i-1]+1 if s[i] else 0
        return o_
    OT['TD_setup']=pd.Series(cnt(up4.values)-cnt(dn4.values),c.index).clip(-9,9)
    OT['DistHigh252']=c/h.rolling(252).max()-1; OT['DistLow252']=c/l.rolling(252).min()-1
    out={'动量震荡':M,'趋势均线':T,'波动率':VOL,'成交量量价':VP,'微观结构流动性':MS,'其他':OT}
    return {k:pd.DataFrame(vv).replace([np.inf,-np.inf],np.nan) for k,vv in out.items()}
