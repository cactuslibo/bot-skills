import numpy as np,pandas as pd,importlib,json
from scipy.stats import norm,skew,kurtosis
from r5 import EFFR
def mydsr(x,N,v):
    sr=x.mean()/x.std(ddof=0); e=np.euler_gamma
    sr0=np.sqrt(v)*((1-e)*norm.ppf(1-1/N)+e*norm.ppf(1-1/(N*np.e)))
    g3=skew(x); g4=kurtosis(x,fisher=False)
    return norm.cdf((sr-sr0)*np.sqrt(len(x)-1)/np.sqrt(1-g3*sr+(g4-1)/4*sr**2)),sr*np.sqrt(252),sr0*np.sqrt(252)
for modn,N,targets in [('r8',10909,{'H2_breadth_rev':dict(rp=30,z=0.6,y=0.006),'H3_vix_rev':dict(rp=30,y=0.04,z=0.65)}),('r7',10804,{'G1_vix_panic':dict(y=0.03,z=0.6,rp=5)})]:
    mod=importlib.import_module(modn); m=mod.M('QQQ'); C=mod.cands(); rf=np.array([EFFR.get(d.year,0)/100/252 for d in m.days])
    cache={}
    for fam,p in targets.items():
        lo,hi=mod.TRAIN[fam]; mt=(m.days>=pd.Timestamp(lo))&(m.days<pd.Timestamp(hi))
        srs=[]
        for ff,pp in C:
            with np.errstate(invalid='ignore'): x=(m.returns(*mod.build(m,ff,pp),True)-rf)[mt]
            srs.append(x.mean()/x.std())
        with np.errstate(invalid='ignore'): x=(m.returns(*mod.build(m,fam,p),True)-rf)[mt]
        print(modn,fam,lo,hi,[round(float(v),3) for v in mydsr(x,N,np.var(srs))], 'var(ddof1)', round(float(mydsr(x,N,np.var(srs,ddof=1))[0]),3))
