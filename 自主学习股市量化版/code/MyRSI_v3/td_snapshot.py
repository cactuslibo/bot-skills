# 顶背离(lower high)逃顶：公共框架。标签/切分/搜索/检验逐行沿用 /workspace/myrsi_top/myr.py（v2），只替换指标与触发。
import os,sys,json,math,random,itertools,numpy as np,pandas as pd
from scipy.stats import beta,binomtest,fisher_exact,norm,skew,kurtosis
IND=os.environ['IND']  # RSI / PPO / MyRSI
H,DROP,RISE,COST=35,0.03,0.015,0.0005
TRAIN=[2015,2016,2017,2018,2019,2021,2023,2025]
df=pd.read_csv('/workspace/data/QQQ_1h.csv'); df['t']=pd.to_datetime(df.time.str[:19]); df=df.set_index('t'); df=df[df.index.year<=2025]  # 复核必须改3：不再加载2026
o=df.open.values; c=df.close.values; h=df.high.values; l=df.low.values; yr=df.index.year.values; n=len(c); day=df.index.normalize()
lab=np.zeros(n,bool); ok=np.zeros(n,bool)
for i in range(n-1-H):
    e=o[i+1]; j=i+1+H; up=h[i+1:j]>=e*(1+RISE); dn=l[i+1:j]<=e*(1-DROP)
    lab[i]=(dn.argmax() if dn.any() else 999)<(up.argmax() if up.any() else 999); ok[i]=yr[i+H]==yr[i]
ok[:120]=False
vix=pd.read_csv('/workspace/qqq_bottom/data/full/VIX.csv',parse_dates=['time']).set_index('time').close
v3=pd.read_csv('/workspace/data/VIX3M_1h.csv'); v3=v3[v3.time.str[11:16].isin(['15:30','15:00','15:15'])]; v3=v3.groupby(pd.to_datetime(v3.time.str[:10])).close.last()
dd=pd.DataFrame({'vix':vix,'v3':v3}); dd['r']=dd.vix/dd.v3; dd=dd.shift(1)
VIXp=dd.vix.reindex(day,method='ffill').values; VR=dd.r.reindex(day,method='ffill').values
dcl=df.close.groupby(day).last(); CA={}
def SMAREL(N):
    k=('s',N)
    if k not in CA: CA[k]=(dcl/dcl.rolling(N).mean()-1).shift(1).reindex(day).values
    return CA[k]
def _ma(x,L,m):
    s=pd.Series(x); return {'ema':lambda:s.ewm(span=L,adjust=False).mean(),'sma':lambda:s.rolling(L).mean(),'wilder':lambda:s.ewm(alpha=1/L,adjust=False).mean()}[m]().values
def rsi(x,L,mode):  # 与 rsi_top/evolve.py 相同
    d=np.diff(x,prepend=x[0]); g=np.clip(d,0,None); s=np.clip(-d,0,None); G,S=_ma(g,L,mode),_ma(s,L,mode); return 100-100/(1+G/(S+1e-12))
def ind(p):
    """返回 (用于背离的指标线, 确认用的快线, 确认用的平滑线, 最大周期)"""
    if IND=='RSI':
        k=('r',p['L'],p['mode'],p['Ls'])
        if k not in CA: r=rsi(c,p['L'],p['mode']); CA[k]=(r,r,_ma(r,p['Ls'],'ema'))
        return CA[k]+(max(p['L'],p['Ls']),)
    if IND=='PPO':
        k=('p',p['f'],p['s'],p['g'],p['ma'])
        if k not in CA: a,b=_ma(c,p['f'],p['ma']),_ma(c,p['s'],p['ma']); pp=100*(a-b)/b; CA[k]=(pp,pp,_ma(pp,p['g'],p['ma']))
        return CA[k]+(max(p['s'],p['g']),)
    k=('m',p['L'],p['L2'])  # MyRSI: boo=100(c+2σ-SMA)/(4σ)，绿=EMA(boo,L2)；确认=灰线boo下穿绿线
    if k not in CA:
        z=pd.Series(c); sd=z.rolling(p['L']).std(ddof=0); boo=(100*(z+2*sd-z.rolling(p['L']).mean())/(4*sd)).values
        CA[k]=(boo,_ma(boo,p['L2'],'ema'))
    boo,g=CA[k]; return ((boo if p['src']==0 else g),boo,g,max(p['L'],p['L2']))
COMMON=dict(dmode=[0,1],lb=(7,70),pl=(1,8),pr=(1,8),ptol=(0.0,0.005),conf=[0,1],W=(1,20),
            vixmax=(11,35),vratio=(0.74,1.05),trend=[0,1,2],smaN=(20,200),cool=(35,105))
if IND=='RSI':
    SPACE=dict(L=(4,40),mode=['wilder','ema','sma'],Ls=(3,30),dv=(0.0,15.0),lvl=(40.0,85.0),**COMMON); LVLOFF=40.0
    BASE=dict(L=14,mode='wilder',Ls=9,dv=0.0,lvl=40.0,dmode=1,lb=40,pl=3,pr=3,ptol=0.0,conf=0,W=10,vixmax=11,vratio=0.74,trend=0,smaN=50,cool=35)
elif IND=='PPO':
    SPACE=dict(f=(3,30),s=(10,80),g=(3,20),ma=['ema','sma','wilder'],dv=(0.0,0.5),lvl=(-0.5,1.5),**COMMON); LVLOFF=-0.5
    BASE=dict(f=12,s=26,g=9,ma='ema',dv=0.0,lvl=-0.5,dmode=1,lb=40,pl=3,pr=3,ptol=0.0,conf=0,W=10,vixmax=11,vratio=0.74,trend=0,smaN=50,cool=35)
else:
    SPACE=dict(L=(5,60),L2=(3,40),src=[0,1],dv=(0.0,40.0),lvl=(-50.0,120.0),**COMMON); LVLOFF=-50.0
    BASE=dict(L=21,L2=12,src=0,dv=0.0,lvl=-50.0,dmode=1,lb=40,pl=3,pr=3,ptol=0.0,conf=0,W=10,vixmax=11,vratio=0.74,trend=0,smaN=50,cool=35)
FL={'dv','lvl','ptol','vixmax','vratio'}
def fix(p):
    if IND=='PPO' and p['s']<p['f']+4: p['s']=min(80,p['f']+4)
    return p
def rand_p():
    p={k:(random.choice(v) if isinstance(v,list) else (random.uniform(*v) if k in FL else random.randint(*v))) for k,v in SPACE.items()}
    for k in('vixmax','vratio','lvl'):
        if random.random()<0.5: p[k]=SPACE[k][0]
    if random.random()<0.5: p['trend']=0
    return fix(p)
def mutate(p,T=1.0):
    q=dict(p); k=random.choice(list(SPACE)); v=SPACE[k]
    if isinstance(v,list): q[k]=random.choice(v); return fix(q)
    lo,hi=v; x=q[k]+random.gauss(0,(hi-lo)*0.15*T)
    while x<lo or x>hi: x=2*lo-x if x<lo else 2*hi-x
    q[k]=x if k in FL else int(round(x)); return fix(q)
IDX=np.arange(n)
def setup(p,x):
    """顶背离 setup（仅用 t 及之前数据）。pivot 高点：x[j]=max(x[j-pl..j+pr])，在 t=j+pr 确认。"""
    pl,pr,lb=p['pl'],p['pr'],p['lb']; w=pl+pr+1
    xs=pd.Series(x); rm=xs.rolling(w).max().values; xj=np.r_[np.full(pr,np.nan),x[:-pr]]
    with np.errstate(invalid='ignore'): piv=(xj==rm)&~np.isnan(rm)
    piv[:w]=False
    hp=pd.Series(h).rolling(w).max().values   # 该pivot窗口内价格最高（t时已知）
    pi=np.where(piv,IDX-pr,np.nan); pv=np.where(piv,xj,np.nan); ph=np.where(piv,hp,np.nan)
    if p['dmode']==0:
        Lv=pd.Series(pv).ffill().values; Li=pd.Series(pi).ffill().values
        prevH=pd.Series(h).shift(1).rolling(lb).max().values
        with np.errstate(invalid='ignore'):
            s=(h>=prevH*(1-p['ptol']))&(IDX-Li<=lb)&(x<Lv-p['dv'])&(Lv>=p['lvl'])
    else:
        e=pd.DataFrame({'i':pi,'v':pv,'h':ph}).dropna(); pe=e.shift(1)
        Pi=np.full(n,np.nan); Pv=Pi.copy(); Ph=Pi.copy(); ii=e.index.values
        Pi[ii]=pe.i.values; Pv[ii]=pe.v.values; Ph[ii]=pe.h.values
        with np.errstate(invalid='ignore'):
            s=piv&((IDX-pr)-Pi<=lb)&(xj<Pv-p['dv'])&(ph>=Ph*(1-p['ptol']))&(Pv>=p['lvl'])
    return np.nan_to_num(s).astype(bool)
def raw(p):
    x,fa,sm,mx=ind(p); s=setup(p,x)
    if p['conf']:  # lower high 后 W 根内，快线下穿自己的平滑线才确认
        sh=lambda z:np.r_[np.nan,z[:-1]]
        with np.errstate(invalid='ignore'): X=(sh(fa)>=sh(sm))&(fa<sm)
        Ls=pd.Series(np.where(s,IDX,np.nan)).ffill().values
        s=np.nan_to_num(X&(IDX-Ls<=p['W'])&(IDX-Ls>=0)).astype(bool)
    s[:max(400,3*mx)]=False   # EMA预热屏蔽 max(400,3×最大周期)
    if p['vixmax']>11.5: s&=np.nan_to_num(VIXp,nan=99)<=p['vixmax']
    if p['vratio']>0.75: s&=np.nan_to_num(VR,nan=9)<=p['vratio']
    if p['trend']: z=np.nan_to_num(SMAREL(p['smaN'])); s&=(z>0) if p['trend']==1 else (z<0)
    if len(CA)>1500: CA.clear()
    return s
def signals(p,years=None,s=None):
    s=(raw(p) if s is None else s)&ok
    if years is not None: s&=np.isin(yr,years)
    out=[];last=-10**9
    for i in np.flatnonzero(s):
        if i-last>=p['cool']: out.append(i); last=i
    return np.array(out,int)
BR={y:lab[(yr==y)&ok].mean() for y in range(2015,2026)}
def cp_lo(k,N,a=0.05): return 0.0 if k==0 else beta.ppf(a,k,N-k+1)
def score(p,years):
    s=signals(p,years); N=len(s)
    if N<12*len(years): return -1
    k=lab[s].sum(); yy=yr[s]; pb=np.mean([BR[y] for y in yy])
    lifts=[lab[s[yy==y]].mean()-BR[y] for y in years if (yy==y).sum()>=3]; pos=np.mean([x>0 for x in lifts]) if lifts else 0
    return cp_lo(k,N)-pb+0.02*pos
TR=[0]; LOG=[]
def S(p,years,log): TR[0]+=1; sc=score(p,years); (LOG.append((sc,p)) if log else None); return sc
def search(years,seed,log=False):
    random.seed(seed); np.random.seed(seed); pool=[]
    for _ in range(600): p=rand_p(); pool.append((S(p,years,log),p))
    for s0,p0 in sorted(pool,key=lambda x:-x[0])[:5]:
        cur,cs=p0,s0; T=1.0
        for _ in range(300):
            q=mutate(cur,T); sq=S(q,years,log); pool.append((sq,q))
            if sq>cs or random.random()<math.exp((sq-cs)/(0.01*T+1e-9)): cur,cs=q,sq
            T*=0.99
    pop=sorted(pool,key=lambda x:-x[0])[:30]
    for g in range(25):
        kids=[]
        for _ in range(40):
            a=random.choice(pop[:15])[1]; b=random.choice(pop[:15])[1]
            ch=fix({k:(a[k] if random.random()<.5 else b[k]) for k in SPACE}); ch=mutate(ch,1-g/30); kids.append((S(ch,years,log),ch))
        pool+=kids; pop=sorted(pop+kids,key=lambda x:-x[0])[:30]
    uniq={}
    for sc,p in pool:
        k=hash(signals(p,years).tobytes()) if sc>-1 else None
        if k is not None and (k not in uniq or sc>uniq[k][0]): uniq[k]=(sc,p)
    res=[]; mon=df.index.to_period('M')
    for sc,p in sorted(uniq.values(),key=lambda x:-x[0])[:40]:
        jit=[S(mutate(mutate(p,.5),.5),years,log) for _ in range(30)]
        sg=signals(p,years); mk=np.array(mon[sg].astype(str)); um=np.unique(mk); grp=[lab[sg[mk==u]] for u in um]
        bo=[np.concatenate([grp[i] for i in np.random.randint(0,len(grp),len(grp))]).mean() for _ in range(500)]
        res.append(dict(p=p,train=sc,jit_p10=float(np.percentile(jit,10)),boot_p5=float(np.percentile(bo,5)),stab=0.5*sc+0.5*float(np.percentile(jit,10))))
    res.sort(key=lambda r:-r['stab']); return res
dlist=pd.DatetimeIndex(pd.unique(day)); di=pd.Series(np.arange(len(dlist)),index=dlist).reindex(day).values
rh_=np.r_[0,c[1:]/c[:-1]-1]
RD=np.expm1(np.bincount(di,np.log1p(rh_))); DY=dlist.year.values
def strat_daily(sig):
    lr=np.log1p(rh_).copy(); cost=np.zeros(n); e=np.ones(n)
    for i in sig:
        lr[i+1]=math.log(o[i+1]/c[i]); lr[i+2:i+1+H]=0; e[i+1:i+1+H]=0; cost[i+1]+=COST; cost[i+H]+=COST
    d=np.expm1(np.bincount(di,lr,minlength=len(dlist)))-np.bincount(di,cost,minlength=len(dlist))
    ex=np.bincount(di,e,minlength=len(dlist))/np.bincount(di,minlength=len(dlist)); return d,ex
def tstats(d,ex,mask):
    s=d[mask]; r=RD[mask]; y=DY[mask]; wy=np.array([ex[mask][y==u].mean() for u in y]) ; b=wy*r
    mdd=lambda x:-(np.cumprod(1+x)/np.maximum.accumulate(np.cumprod(1+x))-1).min()
    cv=lambda x:-np.sort(x)[:max(1,int(len(x)*.05))].mean(); sh=lambda x:x.mean()/(x.std()+1e-12)*math.sqrt(252)
    return dict(expo=float(ex[mask].mean()),sh_s=sh(s),sh_b=sh(b),sh_bh=sh(r),mdd_s=mdd(s),mdd_b=mdd(b),mdd_bh=mdd(r),cvar_s=cv(s),cvar_b=cv(b),cvar_bh=cv(r),
                ann_s=np.prod(1+s)**(252/len(s))-1,ann_b=np.prod(1+b)**(252/len(s))-1),s-b
def filt_mask(p):
    f=np.ones(n,bool)
    if p['vixmax']>11.5: f&=np.nan_to_num(VIXp,nan=99)<=p['vixmax']
    if p['vratio']>0.75: f&=np.nan_to_num(VR,nan=9)<=p['vratio']
    if p['trend']: z=np.nan_to_num(SMAREL(p['smaN'])); f&=(z>0) if p['trend']==1 else (z<0)
    return f
def ev(p,years,sig=None,filt=None):
    """条件随机对照直接用与规则相同的过滤（GoogleAI 要求）；filt=None 时取 p 的过滤。"""
    s=signals(p,years) if sig is None else sig; N=len(s); k=int(lab[s].sum()); pb=float(np.mean([BR[y] for y in yr[s]])) if N else np.nan
    pool=np.isin(yr,years)&ok; ns=pool.copy(); ns[s]=False
    fe=fisher_exact([[k,N-k],[int(lab[ns].sum()),int((~lab[ns]).sum())]],alternative='greater')[1] if N else np.nan
    fm=filt_mask(p) if filt is None else filt; rng=np.random.default_rng(0); sims=[]
    for _ in range(2000 if N else 0):
        dr=np.concatenate([rng.choice(np.flatnonzero(pool&fm&(yr==y)),(yr[s]==y).sum(),replace=False) for y in years if (yr[s]==y).sum()])
        sims.append(lab[dr].mean())
    avoid=float(sum(1-c[i+H]/o[i+1] for i in s)-2*COST*N)
    return dict(n=N,hits=k,prec=k/N if N else None,base=pb,cp_lo=cp_lo(k,N) if N else None,binom_p=binomtest(k,N,pb,'greater').pvalue if N else None,fisher_p=fe,
                samefilt_rand_mean=float(np.mean(sims)) if N else None,samefilt_rand_p=float(np.mean(np.array(sims)>=k/N)) if N else None,avoid=avoid,
                per_year={int(y):dict(n=int((yr[s]==y).sum()),prec=float(lab[s[yr[s]==y]].mean()) if (yr[s]==y).sum() else None,base=BR[y]) for y in years})
