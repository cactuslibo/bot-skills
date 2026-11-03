# MyRSI strategy search on 20 ETFs, 1h bars. Indicator & fill logic reused from myrsi/batch/bt3.py and myrsi_hourly/bt_hourly.py
# Sparse tickers: reindexed onto the full regular-session hourly calendar (XLF timestamps), missing bars ffilled (O=H=L=C=prev close),
# so all periods are time-based (7 bars = 1 trading day). Position changes only execute at the open of the next REAL bar.
import pandas as pd, numpy as np, itertools, sys
from multiprocessing import Pool
T20="XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY ARKK ARKG ARKW ARKQ ARKF ARKX PRNT IZRL ARKB".split()
def rd(t):
    d=pd.read_csv(f'/workspace/data/{t}_1h.csv'); d['time']=pd.to_datetime(d.time,utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
    return d.set_index('time')[['open','close']]
CAL=rd('XLF').index
def load(t):
    d=rd(t); d=d[~d.index.duplicated()]; cal=CAL[(CAL>=d.index[0])&(CAL<=d.index[-1])]; cal=cal.union(d.index)
    x=d.reindex(cal); real=x.close.notna().values; x['close']=x.close.ffill(); x['open']=x.open.fillna(x.close)
    return x,real
def ema(x,n): return x.ewm(span=n,adjust=False).mean()
def xup(a,b): return (a>b)&(a.shift()<=b.shift())
def xdn(a,b): return (a<b)&(a.shift()>=b.shift())
class BT:
    def __init__(s,t):
        s.t=t; s.d,s.real=load(t); s.idx=s.d.index; s.O=s.d.open.values; s.C=s.d.close.values; s.N=len(s.d); s.I={}; s.S={}
    def ind(s,m):
        if m in s.I: return s.I[m]
        c=s.d.close; L=21*m; sd=c.rolling(L).std(ddof=0); boo=100*(c+2*sd-c.rolling(L).mean())/(4*sd)
        boo=boo.replace([np.inf,-np.inf],np.nan); bv=boo.dropna(); I={'boo':boo,'g':ema(bv,12*m).reindex(s.idx),'b':ema(bv,26*m).reindex(s.idx),'r':ema(bv,120*m).reindex(s.idx),
           'm40':pd.Series(-40.,s.idx),'zero':pd.Series(0.,s.idx)}
        p=5*m; mn=boo.rolling(2*p+1,center=True).min(); pl=boo.where(boo==mn).shift(p)  # pivot low confirmed p bars later (bt.py/opt3 pivot logic)
        pv=pl.dropna(); last=pv.reindex(s.idx).ffill(); prev=pv.shift().reindex(s.idx).ffill(); I['hl']=(last>prev)
        s.I[m]=I; return I
    def sma(s,T):
        if T not in s.S: s.S[T]=s.d.close.rolling(T).mean()
        return s.S[T]
    def signals(s,m,en_pair,exitr,filt,T):
        I=s.ind(m); up=s.d.close>s.sma(T); f,sl=I[en_pair[0]],I[en_pair[1]]; en=xup(f,sl)
        rev=xdn(f,sl) if sl.name!=None or en_pair[1] not in('m40','zero') else None
        if en_pair[1] in ('m40','zero'): rev=xdn(I['g'],I['b'])  # oscillator-level entries exit on green<blue
        if filt=='sma': en=en&up
        elif filt=='br': en=en&(I['b']>I['r'])
        elif filt=='hl': en=en&I['hl']
        ex={'sma':~up,'x':rev,'x|sma':rev|~up}[exitr]
        warm=max(T if (filt=='sma' or exitr!='x') else 0,141*m)
        return en.fillna(False).values,ex.fillna(False).values,warm
    def run(s,en,ex,warm):
        pos=np.zeros(s.N); p=0; want=0; R=s.real
        for t in range(1,s.N):
            if want==0 and en[t-1]: want=1
            elif want==1 and ex[t-1]: want=0
            if R[t]: p=want
            pos[t]=p
        pos[:warm+1]=0; return pos
    def equity(s,pos,cost=0.,lo=None,hi=None):
        msk=np.ones(s.N,bool)
        if lo is not None: msk&=s.idx>=pd.Timestamp(lo)
        if hi is not None: msk&=s.idx<pd.Timestamp(hi)
        ii=np.where(msk)[0]; p=pos[ii]; prevp=np.r_[0,p[:-1]]
        gap=np.r_[0,s.O[ii[1:]]/s.C[ii[1:]-1]-1]; intr=s.C[ii]/s.O[ii]-1
        r=(1+prevp*gap)*(1+p*intr)*(1-cost*np.abs(p-prevp))-1
        return pd.Series(np.cumprod(1+r),s.idx[ii]),p
def stats(e,p=None):
    de=e.groupby(e.index.normalize()).last(); r=np.r_[de.iloc[0]-1,de.pct_change().dropna().values]
    yrs=max((e.index[-1]-e.index[0]).days/365.25,1e-9); tot=e.iloc[-1]-1; cagr=(1+tot)**(1/yrs)-1; mdd=(1-e/e.cummax()).max()
    sd=r.std(); o=dict(总收益=tot,CAGR=cagr,最大回撤=mdd,Sharpe=r.mean()/sd*np.sqrt(252) if sd>0 else 0,Calmar=cagr/mdd if mdd>0 else np.nan)
    if p is not None:
        ent=np.where(np.diff(np.r_[0,p])==1)[0]; exi=np.where(np.diff(np.r_[p,0])==-1)[0]; ev=e.values; e0=np.r_[1,ev[:-1]]
        tr=[ev[b]/e0[a]-1 for a,b in zip(ent,exi)]
        o.update(交易次数=len(tr),胜率=np.mean([x>0 for x in tr]) if tr else np.nan,持仓占比=p.mean())
    return o
PAIRS=[('g','r'),('g','b'),('b','r'),('boo','g'),('boo','r'),('g','m40'),('boo','m40'),('boo','zero')]
MS=[1,2,3,5,7]; FILT=['none','sma','br','hl']; EXITS=['sma','x','x|sma']; TS=[200,700,1400]
def grid_keys():
    ks=set()
    for m,pr,ex,fl,T in itertools.product(MS,PAIRS,EXITS,FILT,TS):
        if fl!='sma' and ex=='x': T=0
        ks.add((m,pr,ex,fl,T))
    return sorted(ks,key=str)
UNIV=(7,('g','r'),'sma','sma',1400)  # 规则三×7
def one(t):
    b=BT(t); i0=b.idx[0]; i1=b.idx[-1]; split=i0+(i1-i0)*0.6; nis=(b.idx<split).sum()
    rows=[]; keep={}
    for k in grid_keys():
        m,pr,ex,fl,T=k; en,exs,w=b.signals(m,pr,ex,fl,T if T else 200)
        if w>0.5*nis: continue  # warm-up too long for this sample
        pos=b.run(en,exs,w); rec=dict(ticker=t,m=m,入场=pr[0]+'↑'+pr[1],出场=ex,过滤=fl,SMA=T,warm=w)
        for tag,lo,hi in [('IS',None,split),('OOS',split,None)]:
            e,p=b.equity(pos,0,lo,hi); rec.update({f'{tag}_{a}':v for a,v in stats(e,p).items()})
            e,p=b.equity(pos,0.0005,lo,hi); rec[f'{tag}_Sharpe_c']=stats(e)['Sharpe']
        rows.append(rec); keep[k]=pos
    g=pd.DataFrame(rows); g['key']=[str(k) for k in keep]
    ok=g[(g.IS_交易次数>=5)]
    ok=ok.assign(score=ok.IS_Sharpe_c.rank(pct=True)+ok.IS_Calmar.rank(pct=True)).sort_values('score',ascending=False)
    best=eval(ok.key.iloc[0]); out={'grid':g,'ranked':ok,'split':split,'best':best,'n':len(g)}
    res={}
    for nm,pos in [('best',keep[best]),('univ',keep.get(UNIV)),('bh',np.ones(b.N))]:
        if pos is None: continue
        for per,lo,hi in [('full',None,None),('IS',None,split),('OOS',split,None)]:
            for c in [0,0.0005]:
                if nm=='bh' and c: continue
                e,p=b.equity(pos,c,lo,hi); res[(nm,per,c)]=stats(e,None if nm=='bh' else p)
                if per=='full' and c==0: out['eq_'+nm]=e.groupby(e.index.normalize()).last()
    out['res']=res; out['start']=b.idx[0]; out['real_frac']=b.real.mean()
    print(t,'done',best,flush=True); return t,out
if __name__=='__main__':
    with Pool(8) as P: R=dict(P.map(one,T20))
    pd.to_pickle(R,'results.pkl')
