"""P1/P2 verification: stops, overlays, 2020/2022 trades, 2008 with real VIX3M, DSR/haircut on round-1 trials."""
from cands import *
from statistics import NormalDist; N_=NormalDist()
atr14=rma(tr_(),14).values; tsr=ts_real.values; r2s=r2
def P(which,stop=None,maxd=None,atrk=None,cost=0):
    def entry(i):
        if np.isnan(s200[i]) or np.isnan(r2s[i]): return None
        if which==1: return 'x' if (c[i]>s200[i] and r2s[i]<15) else None
        return 'x' if (not np.isnan(tsr[i]) and r2s[i]<15 and tsr[i]<1) else None
    def ex(i,s):
        base=(r2s[i]>70) if which==1 else (c[i]>SMA[5][i])
        if stop and c[i]<s['ef']*(1-stop): return True
        if maxd and i-s['ei']+1>=maxd: return True
        if atrk and c[i]<s['ef']-atrk*atr14[s['ei']-1]: return True
        return base
    return sim(df,entry,ex,cost)
PER={'2016+':('2016-01-22','2026-10-29'),'IS16-21':('2016-01-22','2021-12-31'),'OOS22-26':('2022-01-01','2026-10-29'),'2000-26':('2000-01-03','2026-10-29'),
     '2008-15':('2008-01-02','2015-12-31'),'2008-26':('2008-01-02','2026-10-29'),'2000-02':('2000-01-03','2002-12-31'),'2008':('2008-01-01','2008-12-31'),'2020':('2020-01-01','2020-12-31'),'2022':('2022-01-01','2022-12-31')}
def row(name,R,cost):
    d={'model':name}
    for p,(a,b) in PER.items():
        s=stats(df,R,a,b,cost); d[p]=f"{s['trades']}/{s['sharpe']:.2f}/{s['MDD']*100:.1f}%/{s['CAGR']*100:.1f}%"
    return d
rows=[]
for w in (1,2):
    for lab,kw in [('无止损',{}),('收盘止损-5%',dict(stop=0.05)),('收盘止损-8%',dict(stop=0.08)),('时间止损10日',dict(maxd=10)),('ATR止损2.5×ATR14',dict(atrk=2.5))]:
        for cost in (0,5): rows.append(row(f'P{w} {lab} {cost}bp',P(w,cost=cost,**kw),cost))
T=pd.DataFrame(rows); T.to_csv('p12_stops.csv',index=False); pd.set_option('display.width',400); pd.set_option('display.max_columns',20); print(T.to_string())
# overlays
B=bh()
def ov(tgt_t,mode):
    base=np.ones(len(df)) if mode=='always' else np.where(c>s200,1.0,0.0); base[np.isnan(s200)]=1 if mode=='always' else 0
    t=base+0.5*tgt_t; r,w=returns(df,t,5); return dict(tr=[],r=r,w=w,tgt=t,open=False,pend=None)
orow=[]
for w in (1,2):
    R=P(w,cost=5)
    for mode in ('always','sma200'):
        O_=ov(R['tgt'],mode); d={'model':f'P{w} 叠加 base={mode}'}
        for p in ['2016+','OOS22-26','2000-26','2008-26','2000-02','2008','2022']:
            s=stats(df,O_,*PER[p],5); d[p]=f"{s['sharpe']:.2f}/{s['MDD']*100:.1f}%/{s['CAGR']*100:.1f}%"
        orow.append(d)
for mode in ('always','sma200'):
    O_=ov(np.zeros(len(df)),mode); d={'model':f'无卫星 base={mode}'}
    for p in ['2016+','OOS22-26','2000-26','2008-26','2000-02','2008','2022']:
        s=stats(df,O_,*PER[p],5); d[p]=f"{s['sharpe']:.2f}/{s['MDD']*100:.1f}%/{s['CAGR']*100:.1f}%"
    orow.append(d)
OV=pd.DataFrame(orow); OV.to_csv('p12_overlay.csv',index=False); print(OV.to_string())
# trades 2020 / 2022
for w in (1,2):
    R=P(w)
    for y in ('2020','2022'):
        print(f'P{w} {y}:',[(str(df.index[s].date()),str(df.index[e].date()),f'{x/p-1:+.2%}') for s,e,p,x,_ in R['tr'] if str(df.index[s].year)==y])
for y,(a,b) in [('2020',('2020-01-01','2020-12-31')),('2022',('2022-01-01','2022-12-31'))]:
    seg=df.loc[a:b]; print(y,'min close',seg.close.idxmin().date(),round(seg.close.min(),2),'min low',seg.low.idxmin().date(),round(seg.low.min(),2),
      'C>SMA200 on low day', bool((df.close>sma(df.close,200)).loc[seg.close.idxmin()]), 'VIX/VIX3M', round(ts_real.loc[seg.close.idxmin()],3))
# when below SMA200 in 2020/2022
cs=pd.Series(c>s200,df.index)
for y in ('2020','2022'): print(y,'days below SMA200',int((~cs.loc[y]).sum()),'of',len(cs.loc[y]))
# MAE
for w in (1,2):
    R=P(w); mae=[]
    for s,e,p,x,_ in R['tr']: mae.append(l[s:e+1].min()/p-1)
    mae=np.array(mae); rets=np.array([x/p-1 for s,e,p,x,_ in R['tr']]); hold=np.array([e-s for s,e,_,_,_ in R['tr']])
    print(f'P{w} 2000-26 MAE worst {mae.min():.1%}, p5 {np.percentile(mae,5):.1%}, worst trade {rets.min():.1%}, max hold {hold.max()} bars, n trades {len(rets)}')
    k=np.argmin(rets); s,e,p,x,_=R['tr'][k]; print('   worst trade',df.index[s].date(),df.index[e].date())
# CAGR verification
for w in (1,2):
    R=P(w); s=stats(df,R,*PER['2016+'],0); m=(df.index>='2016-01-22')
    rr=R['r'][m]; inm=R['w'][m]>0; ann_in=(np.prod(1+rr[inm]))**(252/inm.sum())-1
    Rc=returns(df,R['tgt'],0,cash_yield=True)[0][m]; cy=np.prod(1+Rc)**(252/m.sum())-1
    print(f'P{w} 2016+ CAGR {s["CAGR"]:.2%} tot {s["tot"]:.1%} exposure {s["exposure"]:.1%} annualised-while-invested {ann_in:.1%} CAGR with cash@EFFR {cy:.2%}')
s=stats(df,B,*PER['2016+'],0); print('BH 2016+ CAGR',round(s['CAGR'],4),'sharpe',round(s['sharpe'],2),'MDD',round(s['MDD'],3))
# DSR / haircut on round-1 172 trials (2016-01-22..)
R1=np.load('round1_rets.npy'); sr=R1.mean(1)/R1.std(1); V=np.nanvar(sr)
C_=np.corrcoef(R1[R1.std(1)>0]); ev=np.linalg.eigvalsh(np.nan_to_num(C_)); Neff=ev.sum()**2/(ev**2).sum()
def dsr(st,N):
    g=0.5772156649; sr0=np.sqrt(V)*((1-g)*N_.inv_cdf(1-1/N)+g*N_.inv_cdf(1-1/(N*np.e)))
    z=(st['srd']-sr0)*np.sqrt(st['T']-1)/np.sqrt(1-st['skew']*st['srd']+(st['kurt']-1)/4*st['srd']**2); return N_.cdf(z),sr0*np.sqrt(252)
def haircut(st,N):  # Harvey-Liu Bonferroni
    t=st['srd']*np.sqrt(st['T']); p=2*(1-N_.cdf(t)); pa=min(1,p*N); 
    ta=N_.inv_cdf(1-pa/2) if pa<1 else 0; return p,pa,ta/np.sqrt(st['T'])*np.sqrt(252)
print('round1 trials',len(sr),'std of trial SR (ann)',round(np.sqrt(V)*np.sqrt(252),3),'N_eff(eigen)',round(Neff,1))
for w in (1,2):
    st=stats(df,P(w),*PER['2016+'],0)
    for N in (172,int(round(Neff)),15):
        d=dsr(st,N); h=haircut(st,N); print(f'P{w} SR {st["sharpe"]:.2f} N={N}: DSR prob {d[0]:.3f} (SR0 {d[1]:.2f}); Bonferroni p {h[0]:.4f}->{h[1]:.3f}, haircut SR {h[2]:.2f}')
    st=stats(df,P(w),'2000-01-03','2026-10-29',0) if w==1 else stats(df,P(w),'2008-01-02','2026-10-29',0)
    h=haircut(st,172); d=dsr(st,172); print(f'   longer sample SR {st["sharpe"]:.2f}: DSR {d[0]:.3f}, haircut SR(N=172) {h[2]:.2f}')
