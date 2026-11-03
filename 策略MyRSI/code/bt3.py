import pandas as pd, numpy as np, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
T="XLB XLE XLF XLI XLK XLP XLU XLV XLY XLRE XLC ARKK ARKG ARKW ARKQ ARKF ARKX PRNT IZRL ARKB".split()
def ema(x,n): return x.ewm(span=n,adjust=False).mean()  # Pine-style, seeded at first valid value
def load(p):
    d=pd.read_csv(p,parse_dates=['date']).set_index('date').sort_index(); return d
def stats(e,ntr=None):
    r=e.pct_change().dropna(); yrs=(e.index[-1]-e.index[0]).days/365.25
    tot=e.iloc[-1]/e.iloc[0]-1 if ntr is None else e.iloc[-1]-1
    return tot,(1+tot)**(1/yrs)-1,(1-e/e.cummax()).max(),r.mean()/r.std()*np.sqrt(252)
def bt(d,start=None,end=None):
    c,o=d.close,d.open; sd=c.rolling(21).std(ddof=0)
    boo=100*(c+2*sd-c.rolling(21).mean())/(4*sd); g,r=ema(boo,12),ema(boo,120); s200=c.rolling(200).mean()
    buy=((g>r)&(g.shift()<=r.shift())&(c>s200)).values; sell=(c<s200).values
    first=np.argmax(s200.notna().values)+1  # first possible fill bar
    idx=d.index; ii=np.arange(first,len(d))
    if start: ii=ii[idx[ii]>=pd.Timestamp(start)]
    if end: ii=ii[idx[ii]<=pd.Timestamp(end)]
    O,C=o.values,c.values; pos=0; eq=1.; eqs=[]; trades=[]; inm=0; ent=None
    for k,t in enumerate(ii):
        if k>0: eq*=1+pos*(O[t]/C[t-1]-1)
        s=t-1
        if pos==0 and buy[s] and k>=0: pos=1; ent=eq
        elif pos==1 and sell[s]: pos=0; trades.append(eq/ent-1)
        eq*=1+pos*(C[t]/O[t]-1); inm+=pos; eqs.append(eq)
    if pos: trades.append(eq/ent-1)
    e=pd.Series(eqs,idx[ii]); bh=pd.Series(C[ii]/O[ii[0]],idx[ii])
    return e,bh,trades,inm/len(ii)
if __name__=='__main__':
    q=load('/workspace/data/QQQ_daily.csv'); e,bh,tr,im=bt(q,'2016-10-01','2026-10-31')
    print('QQQ',e.index[0].date(),e.index[-1].date(),'strat',stats(e,1),len(tr),im,'BH',stats(bh,1))
    rows=[]; curves={}
    for t in T:
        d=load(f'/workspace/data/etf/{t}.csv'); e,bh,tr,im=bt(d); curves[t]=(e,bh)
        full=d.close.iloc[-1]/d.open.iloc[0]-1
        S=stats(e,1); B=stats(bh,1)
        rows.append(dict(ticker=t,data_start=d.index[0].date(),start=e.index[0].date(),end=e.index[-1].date(),years=round((e.index[-1]-e.index[0]).days/365.25,2),
          s_ret=S[0],s_cagr=S[1],s_mdd=S[2],s_sharpe=S[3],trades=len(tr),win=np.mean([x>0 for x in tr]) if tr else np.nan,time_in=im,
          bh_ret=B[0],bh_cagr=B[1],bh_mdd=B[2],bh_sharpe=B[3],bh_full_ret=full,
          beat_ret=S[0]>B[0],beat_sharpe=S[3]>B[3],beat_mdd=S[2]<B[2],beat_ret_mdd=S[1]/S[2]>B[1]/B[2]))
    df=pd.DataFrame(rows); df.round(4).to_csv('summary.csv',index=False)
    f=df.copy()
    for k in ['s_ret','s_cagr','s_mdd','time_in','win','bh_ret','bh_cagr','bh_mdd','bh_full_ret']: f[k]=(f[k]*100).round(1)
    for k in ['s_sharpe','bh_sharpe']: f[k]=f[k].round(2)
    print(f.drop(columns=['data_start']).to_markdown(index=False))
    for k in ['beat_ret','beat_sharpe','beat_mdd','beat_ret_mdd']: print(k,df[k].sum(),'| ARK-family',df[~df.ticker.str.startswith('XL')][k].sum(),'/9 XL',df[df.ticker.str.startswith('XL')][k].sum(),'/11')
    fig,ax=plt.subplots(4,5,figsize=(20,14))
    for a,t in zip(ax.flat,T):
        e,bh=curves[t]; a.plot(e,label='Rule3'); a.plot(bh,label='B&H',alpha=.7); a.set_yscale('log'); a.set_title(t); a.tick_params(labelsize=7)
    ax.flat[0].legend(); fig.tight_layout(); fig.savefig('equity.png',dpi=90)
