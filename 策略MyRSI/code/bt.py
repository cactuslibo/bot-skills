import pandas as pd, numpy as np, itertools
def load(s):
    d=pd.read_csv(s+'.csv',index_col=0,parse_dates=True); return d
def ema(x,n): return x.ewm(span=n,adjust=False).mean()
def ind(d,L,f=12,s=26,r=120):
    c=d.Close; sd=c.rolling(L).std(ddof=0); boo=100*(c+2*sd-c.rolling(L).mean())/(4*sd)
    return pd.DataFrame(dict(c=c,o=d.Open,boo=boo,g=ema(boo,f),b=ema(boo,s),r=ema(boo,r),sma200=c.rolling(200).mean()))
def pivots(x,p):
    x=x.values;n=len(x);lastL=np.full(n,np.nan);prevL=lastL.copy();lastH=lastL.copy();prevH=lastL.copy()
    lL=pL=lH=pH=np.nan
    for i in range(n):
        j=i-p
        if j>=p and not np.isnan(x[j-p:i+1]).any():
            w=x[j-p:i+1]
            if x[j]==w.min(): pL,lL=lL,x[j]
            if x[j]==w.max(): pH,lH=lH,x[j]
        lastL[i]=lL;prevL[i]=pL;lastH[i]=lH;prevH[i]=pH
    return lastL>prevL, lastH<prevH
def xo(a,b): return (a>b)&(a.shift()<=b.shift())
def xu(a,b): return (a<b)&(a.shift()>=b.shift())
def lines(I,k): return {'boo':I.boo,'g':I.g,'b':I.b,'r':I.r,'m40':pd.Series(-40.,I.index),'zero':pd.Series(0.,I.index)}[k]
def run(I,entry,exit_,filt,hl,lh,lvl,start,end,short=False,lev=1.0):
    en=xo(lines(I,entry[0]),lines(I,entry[1])).values
    ex=xu(lines(I,exit_[0]),lines(I,exit_[1])).values
    hlv,lhv=PV
    if hl: en=en&hlv
    if lh: ex=ex&lhv&(I.boo.values>lvl)
    if filt=='sma200': fl=(I.c>I.sma200).values
    elif filt=='br': fl=(I.b>I.r).values
    else: fl=np.ones(len(I),bool)
    idx=I.index; o=I.o.values; c=I.c.values
    m=(idx>=pd.Timestamp(start))&(idx<=pd.Timestamp(end)); ii=np.where(m)[0]
    pos=0; eq=1.0; eqs=[]; trades=0; prev=None
    for t in ii:
        # position decided at close t-1 applies from open t
        if prev is not None:
            # return from prev close to this open with old pos, then new pos open->close
            eq*=1+lev*pos*(o[t]/c[prev]-1)
        newpos=pos
        s=t-1
        if s>=0 and prev is not None:
            if pos==0 or pos==-1:
                if en[s] and fl[s]: newpos=1
                elif pos==0 and short and ex[s] and not fl[s]: newpos=-1
                elif pos==-1 and not short: newpos=0
            if pos==1 and (ex[s] or (filt!='none' and not fl[s])): newpos=-1 if (short and ex[s]) else 0
        if newpos!=pos: trades+= (newpos!=0)
        pos=newpos
        eq*=1+lev*pos*(c[t]/o[t]-1)
        eqs.append(eq); prev=t
    e=pd.Series(eqs,idx[ii]); r=e.pct_change().dropna()
    yrs=(e.index[-1]-e.index[0]).days/365.25
    return dict(ret=e.iloc[-1]/1-1 if False else e.iloc[-1]-1,cagr=e.iloc[-1]**(1/yrs)-1,dd=(1-e/e.cummax()).max(),
                sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0,tr=trades,expo=0)
