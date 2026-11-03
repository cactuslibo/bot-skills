import pandas as pd,numpy as np
T="XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY ARKK ARKQ ARKW ARKG ARKF ARKX ARKB IZRL PRNT".split()
def ema(s,n):
    a=2/(n+1);out=np.full(len(s),np.nan);v=np.nan
    for i,x in enumerate(s):
        if np.isnan(x): continue
        v=x if np.isnan(v) else a*x+(1-a)*v; out[i]=v
    return out
for t in T:
    d=pd.read_csv(f"/workspace/data/etf/{t}.csv");n=pd.read_csv(f"/workspace/data/etf/new/{t}.csv")
    n=n[n.date>d.date.max()];d=pd.concat([d,n[d.columns]],ignore_index=True);c=d.close
    sd=c.rolling(21).std(ddof=0);boo=100*(c+2*sd-c.rolling(21).mean())/(4*sd)
    g=ema(boo.values,12);r=ema(boo.values,120);sma=c.rolling(200).mean().values
    pos=0;ch=""
    for i in range(1,len(d)):
        if np.isnan(sma[i]): continue
        ch=""
        if pos==0 and g[i]>r[i] and g[i-1]<=r[i-1] and c[i]>sma[i]: pos=1;ch="买入"
        elif pos==1 and c[i]<sma[i]: pos=0;ch="卖出"
    print(t,d.date.iloc[-1],"持有" if pos else "空仓",ch or "-","收%.2f SMA%.2f 绿%.1f 红%.1f"%(c.iloc[-1],sma[-1],g[-1],r[-1]))
