import pandas as pd,numpy as np
T="XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY ARKK ARKQ ARKW ARKG ARKF ARKX PRNT IZRL ARKB".split()
def ema(s,n):
    a=2/(n+1);out=np.full(len(s),np.nan);v=np.nan
    for i,x in enumerate(s):
        if np.isnan(x): continue
        v=x if np.isnan(v) else a*x+(1-a)*v; out[i]=v
    return out
for t in T:
    d=pd.read_csv(f"/workspace/data/etf/{t}.csv");c=d.close
    sd=c.rolling(21).std(ddof=0);boo=100*(c+2*sd-c.rolling(21).mean())/(4*sd)
    g=ema(boo.values,12);r=ema(boo.values,120);sma=c.rolling(200).mean().values
    pos=0;last=None
    for i in range(1,len(d)):
        if np.isnan(sma[i]): continue
        if pos==0 and g[i]>r[i] and g[i-1]<=r[i-1] and c[i]>sma[i]:
            pos=1
            if d.date[i]>="2026-08-29": print(t,"买入",d.date[i],"绿%.1f(前%.1f) 红%.1f(前%.1f) 收%.2f SMA200 %.2f"%(g[i],g[i-1],r[i],r[i-1],c[i],sma[i]))
        elif pos==1 and c[i]<sma[i]:
            pos=0
            if d.date[i]>="2026-08-29": print(t,"卖出",d.date[i],"收%.2f(前%.2f) SMA200 %.2f(前%.2f)"%(c[i],c[i-1],sma[i],sma[i-1]))

