# MyRSI on QQQ 1h. Indicator/fill logic reused from myrsi/batch/bt3.py (Pine EMA, ddof=0, signal at close -> fill next open)
import pandas as pd, numpy as np, itertools
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=pd.read_csv('/workspace/data/QQQ_1h.csv'); d['time']=pd.to_datetime(d.time,utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
d=d.set_index('time'); O,C=d.open.values,d.close.values; idx=d.index; N=len(d)
def ema(x,n): return x.ewm(span=n,adjust=False).mean()
IND={}
def ind(m):
    if m in IND: return IND[m]
    c=d.close; L=21*m; sd=c.rolling(L).std(ddof=0); boo=100*(c+2*sd-c.rolling(L).mean())/(4*sd)
    boo=boo[boo.notna()]  # Pine: EMA seeded at first valid boo
    r={'boo':boo.reindex(idx),'g':ema(boo,12*m).reindex(idx),'b':ema(boo,26*m).reindex(idx),'r':ema(boo,120*m).reindex(idx)}
    IND[m]=r; return r
def xup(a,b): return (a>b)&(a.shift()<=b.shift())
def xdn(a,b): return (a<b)&(a.shift()>=b.shift())
def signals(m,entry,exitr,filt,T):
    I=ind(m); s=d.close.rolling(T).mean(); up=d.close>s
    if entry in('gr','gb','br'): f,sl=I[entry[0]],I[entry[1]]; en=xup(f,sl); ex_x=xdn(f,sl)
    elif entry=='g40': en=xup(I['g'],pd.Series(-40.,idx)); ex_x=xdn(I['g'],I['b'])
    elif entry=='boo40': en=xup(I['boo'],pd.Series(-40.,idx)); ex_x=xdn(I['g'],I['b'])
    if filt: en=en&up
    ex={'sma':~up,'x':ex_x,'x|sma':ex_x|~up}[exitr]
    warm=max(T,120*m+21*m)
    return en.fillna(False).values,ex.fillna(False).values,warm
def run(en,ex,warm):
    pos=np.zeros(N); p=0
    for t in range(1,N):  # position held during bar t decided at close t-1
        if p==0 and en[t-1]: p=1
        elif p==1 and ex[t-1]: p=0
        pos[t]=p
    pos[:warm+1]=0; return pos
def equity(pos,cost=0.0,lo=None,hi=None):
    m=np.ones(N,bool)
    if lo: m&=idx>=pd.Timestamp(lo)
    if hi: m&=idx<pd.Timestamp(hi)
    ii=np.where(m)[0]; p=pos[ii].copy(); p[0]=0 if pos[ii[0]-1]==0 else p[0]  # start flat-consistent
    prevp=np.r_[pos[ii[0]-1] if ii[0]>0 else 0,p[:-1]]
    if lo: prevp[0]=0
    gap=O[ii]/C[ii-1]-1; gap[0]=0 if ii[0]==0 else gap[0]
    intr=C[ii]/O[ii]-1
    r=(1+prevp*gap)*(1+p*intr)*(1-cost*np.abs(p-prevp))-1
    return pd.Series(np.cumprod(1+r),idx[ii]),p
def stats(e,p=None):
    de=e.groupby(e.index.normalize()).last(); de=pd.concat([pd.Series([1.0],[de.index[0]-pd.Timedelta(days=1)]),de])
    r=de.pct_change().dropna(); yrs=(e.index[-1]-e.index[0]).days/365.25
    tot=e.iloc[-1]-1; cagr=(1+tot)**(1/yrs)-1; mdd=(1-e/e.cummax()).max()
    sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0
    o=dict(总收益=tot,CAGR=cagr,最大回撤=mdd,Sharpe=sh,Calmar=cagr/mdd if mdd>0 else np.nan)
    if p is not None:
        ent=np.where(np.diff(np.r_[0,p])==1)[0]; exi=np.where(np.diff(np.r_[p,0])==-1)[0]
        ev=e.values; e0=np.r_[1,ev[:-1]]
        tr=[ev[b]/e0[a]-1 for a,b in zip(ent,exi)]
        o.update(交易次数=len(tr),胜率=np.mean([x>0 for x in tr]) if tr else np.nan,持仓占比=p.mean())
    return o
def bh(lo=None,hi=None): return equity(np.ones(N),0,lo,hi)
SPLIT='2022-01-01'  # ~60% of bars (2015-01..2021-12 IS)
R8='2018-10-29'
if __name__=='__main__':
    rows=[]; P={}
    for m,entry,exitr,filt,T in itertools.product([1,2,3,5,7],['gr','gb','br','g40','boo40'],['sma','x','x|sma'],[0,1],[200,700,1400]):
        if exitr=='x' and not filt and T!=200: continue
        if exitr in('sma','x|sma') or filt: pass
        en,ex,w=signals(m,entry,exitr,filt,T); pos=run(en,ex,w); key=(m,entry,exitr,filt,T if (filt or exitr!='x') else 0)
        if key in P: continue
        P[key]=pos
        rec=dict(m=m,入场=entry,出场=exitr,趋势过滤=filt,SMA=key[4])
        for tag,lo,hi in [('IS','2015-01-01',SPLIT),('OOS',SPLIT,None)]:
            e,p=equity(pos,0,lo,hi); s=stats(e,p); rec.update({f'{tag}_{k}':v for k,v in s.items()})
        rows.append(rec)
    g=pd.DataFrame(rows); g['IS_score']=g.IS_Sharpe.rank(pct=True)+g.IS_Calmar.rank(pct=True)
    g=g[g.IS_交易次数>=8].sort_values('IS_score',ascending=False); g.round(4).to_csv('grid_results.csv',index=False)
    print(len(g)); print(g.head(15).round(3).to_string())
    pd.to_pickle(P,'pos.pkl')
