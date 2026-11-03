import json,math,itertools,os,sys,hashlib,datetime,numpy as np,pandas as pd,multiprocessing as mp
import v3; P=v3.P
from scipy.stats import norm,skew,kurtosis
TRN=P.TRAIN; CUMBASE=360300
FG=[0.25,0.5,0.75,1.0]; VG=[0.0,0.12,0.16,0.20,0.25]
def tst(d,ex,mask):
    s=d[mask]; r=v3.RD[mask]; y=v3.DY[mask]; wy=np.array([ex[mask][y==u].mean() for u in y]); b=wy*r
    mdd=lambda x:-(np.cumprod(1+x)/np.maximum.accumulate(np.cumprod(1+x))-1).min(); sh=lambda x:x.mean()/(x.std()+1e-12)*math.sqrt(252)
    cv=lambda x:-np.sort(x)[:max(1,int(len(x)*.05))].mean(); ann=lambda x:np.prod(1+x)**(252/len(x))-1
    return dict(expo=float(ex[mask].mean()),sh_s=sh(s),sh_b=sh(b),sh_bh=sh(r),mdd_s=mdd(s),mdd_b=mdd(b),mdd_bh=mdd(r),cvar_s=cv(s),cvar_b=cv(b),cvar_bh=cv(r),ann_s=ann(s),ann_b=ann(b),ann_bh=ann(r)),s-b
def size_pick(sig,years):
    m=np.isin(v3.DY,years); best=None
    for f in FG:
        for vt in VG:
            d,ex=v3.daily(v3.position(sig,f,vt)); t,_=tst(d,ex,m); sc=t['sh_s']-t['sh_b']
            if t['expo']>=0.6 and (best is None or sc>best[0]): best=(sc,f,vt)
    return best
def volbase_pick(years):
    m=np.isin(v3.DY,years); best=None
    for vt in VG[1:]:
        d,ex=v3.daily(v3.position([],0,vt)); t,_=tst(d,ex,m); sc=t['sh_s']-t['sh_b']
        if best is None or sc>best[0]: best=(sc,vt)
    return best
def fold(y):
    P.TR[0]=0; P.LOG.clear(); yrs=[t for t in TRN if t!=y] if y else TRN
    res=P.search(yrs,3000+(y or 0),log=True)
    rob=[r for r in res if r['jit_p10']>0]; pick=(rob or res)[0]
    sz=size_pick(P.signals(pick['p'],yrs),yrs); vb=volbase_pick(yrs)
    return y,res[:10],pick,bool(rob),sz,vb,P.TR[0]+len(FG)*len(VG)+len(VG)-1,[p for s,p in P.LOG if s>-1]
if __name__=='__main__':
    print('PLAN sha256',hashlib.sha256(open('PLAN.md','rb').read()).hexdigest(),datetime.datetime.now().isoformat(),flush=True)
    for f in sorted(os.listdir('.')):
        if f.endswith('.py'): print('code sha256',f,hashlib.sha256(open(f,'rb').read()).hexdigest(),flush=True)
    with mp.Pool(8) as pool: outs=pool.map(fold,[None]+TRN)
    main=outs[0]; best=main[2]['p']; trials=sum(x[6] for x in outs); cumN=CUMBASE+trials
    O=dict(trials_this=trials,cum_base=CUMBASE,cum_N=cumN,top5=main[1][:5],best=best,best_robust_found=main[3],best_jit_p10=main[2]['jit_p10'],size_train=main[4],volbase_train=main[5])
    O['train']=P.ev(best,TRN)
    # 邻域：200 次抖动
    import random; random.seed(7); js=[P.score(P.mutate(P.mutate(best,.5),.5),TRN) for _ in range(200)]
    O['neigh']=dict(p10=float(np.percentile(js,10)),median=float(np.median(js)),frac_pos=float(np.mean(np.array(js)>0)),frac_guard_fail=float(np.mean(np.array(js)==-1)))
    lo={}; oos=[]; dm=np.isin(v3.DY,TRN); wS=np.ones(P.n); wV=np.ones(P.n)
    for y,res,pk,rb,sz,vb,_,_ in outs[1:]:
        p=pk['p']; e=P.ev(p,[y]); sg=P.signals(p,[y]); oos+=list(sg)
        lo[y]=dict(p=p,robust=rb,jit_p10=pk['jit_p10'],size=sz,volbase=vb,**{k:e[k] for k in('n','prec','base','cp_lo','binom_p','avoid')})
        hm=P.yr==y; wS[hm]=v3.position(sg,sz[1],sz[2])[hm]; wV[hm]=v3.position([],0,vb[1])[hm]
    oos=np.array(sorted(oos)); k=int(P.lab[oos].sum()); N=len(oos); pb=float(np.mean([P.BR[y] for y in P.yr[oos]]))
    O['loyo']=lo; O['loyo_concat']=dict(n=N,hits=k,prec=k/N,base=pb,cp_lo=P.cp_lo(k,N),binom_p=P.binomtest(k,N,pb,'greater').pvalue,avoid=float(sum(lo[y]['avoid'] for y in lo)),missed=v3.missed(oos))
    d,ex=v3.daily(v3.position(oos,1,0)); O['loyo_trade_full_exit'],xo=tst(d,ex,dm)
    d,ex=v3.daily(wS); O['loyo_trade_sized'],xs=tst(d,ex,dm)
    d,ex=v3.daily(wV); O['loyo_trade_volbase'],_=tst(d,ex,dm)
    sb=P.signals(best,TRN); d,ex=v3.daily(v3.position(sb,1,0)); O['train_trade_full_exit'],_=tst(d,ex,dm)
    d,ex=v3.daily(v3.position(sb,main[4][1],main[4][2])); O['train_trade_sized'],_=tst(d,ex,dm); O['train_missed']=v3.missed(sb)
    # SPA/PBO：全部独特候选（全仓退出口径，与前几轮一致）
    uq={}
    for x in outs:
        for p in x[7]: uq[json.dumps(p,sort_keys=True,default=float)]=p
    X=[]
    for p in uq.values():
        d,ex=v3.daily(v3.position(P.signals(p,TRN),1,0)); X.append(tst(d,ex,dm)[1])
    X=np.array(X,dtype=np.float32); nn=X.shape[1]; O['n_cands_spa']=len(X)
    mu=X.mean(1); sd=X.std(1)+1e-12; Tobs=max((np.sqrt(nn)*mu/sd).max(),0); thr=-np.sqrt(2*np.log(np.log(nn)))*sd/np.sqrt(nn); muc=np.where(mu>=thr,mu,0)
    rng=np.random.default_rng(1); Tb=[]
    for b in range(1000):
        ii=np.empty(nn,int); t=rng.integers(nn); u=rng.random(nn); jm=rng.integers(nn,size=nn)
        for j in range(nn): ii[j]=t; t=jm[j] if u[j]<0.1 else (t+1)%nn
        Tb.append(max((np.sqrt(nn)*(X[:,ii].mean(1)-muc)/sd).max(),0))
    O['spa_p']=float(np.mean(np.array(Tb)>=Tobs)); V=(mu/sd).var(); g=0.5772156649
    def dsr(x,NN):
        SR=x.mean()/x.std(); SR0=math.sqrt(V)*((1-g)*norm.ppf(1-1/NN)+g*norm.ppf(1-1/(NN*math.e)))
        return float(norm.cdf((SR-SR0)*math.sqrt(len(x)-1)/math.sqrt(1-skew(x)*SR+(kurtosis(x,fisher=False)-1)/4*SR*SR))),float(SR)
    O['dsr_full_exit'],O['loyo_excess_sr_daily_full_exit']=dsr(xo,cumN); O['dsr_sized'],O['loyo_excess_sr_daily_sized']=dsr(xs,cumN)
    mon=pd.Series(P.dlist[dm]).dt.to_period('M').values; um=pd.unique(mon)
    M=np.stack([X[:,mon==u].sum(1) for u in um],1); bl=np.array_split(np.arange(M.shape[1]),16)
    BS=np.stack([M[:,b].mean(1) for b in bl],1); BV=np.stack([M[:,b].var(1)*len(b) for b in bl],1); lam=[]
    for comb in itertools.combinations(range(16),8):
        oo=[j for j in range(16) if j not in comb]; cc=list(comb)
        isr=BS[:,cc].mean(1)/np.sqrt(BV[:,cc].mean(1)+1e-12); osr=BS[:,oo].mean(1)/np.sqrt(BV[:,oo].mean(1)+1e-12)
        kk=isr.argmax(); w=(osr<osr[kk]).mean()+0.5*(osr==osr[kk]).mean(); w=min(max(w,1e-6),1-1e-6); lam.append(math.log(w/(1-w)))
    O['pbo']=float(np.mean(np.array(lam)<=0))
    json.dump(O,open('main_results.json','w'),indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o))
    print(json.dumps({k:O[k] for k in O if k not in('top5','loyo')},default=lambda o:o.item() if hasattr(o,'item') else str(o),indent=0))
