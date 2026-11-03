"""Test 'intraday momentum' claim: autocorrelations (intraday vs overnight), variance ratios, P2-signal-day paths."""
from hyb2 import *
d=pd.DataFrame({'date':q.date,'bar':q.bar,'o':o,'c':c,'first':first})
d['ret']=np.where(first,c/o-1,c/np.r_[np.nan,c[:-1]]-1)      # intraday bar return (bar1 = open->close)
d['on']=np.where(first,o/np.r_[np.nan,c[:-1]]-1,np.nan)       # overnight gap
d=d.iloc[1:]
def ac(x,y): m=~(np.isnan(x)|np.isnan(y)); n=m.sum(); r=np.corrcoef(x[m],y[m])[0,1]; return r,r*np.sqrt(n),n
res={}
for lab,(a,b) in {'全样本':('2015','2026'),'IS 2015-21':('2015','2021'),'OOS 2022-26':('2022','2026')}.items():
    x=d[(d.date>=a)&(d.date<=b+'-12-31')]
    same=(x.date.values[1:]==x.date.values[:-1])
    r=x.ret.values
    lag1=ac(r[:-1][same],r[1:][same])                                   # within-day consecutive bars
    g=x.groupby('date')
    on=g.on.first().values; b1=g.apply(lambda z:z.ret.iloc[0]).values
    rest=g.apply(lambda z:(1+z.ret.iloc[1:]).prod()-1).values; last1=g.apply(lambda z:z.ret.iloc[-1]).values
    first_half=g.apply(lambda z:(1+z.ret.iloc[:-1]).prod()-1).values
    nxt_on=np.r_[on[1:],np.nan]; intraday=g.apply(lambda z:(1+z.ret).prod()-1).values
    res[lab]=dict(lag1=lag1,on_vs_bar1=ac(on,b1),bar1_vs_rest=ac(b1,rest),firsthalf_vs_last=ac(first_half,last1),intraday_vs_next_on=ac(intraday,nxt_on),
                  on_prev_vs_on=ac(on[:-1],on[1:]))
    # variance ratio on within-day returns (non-overlapping q-bar sums within day), q=2,3,6
    vr={}
    for k in (2,3,6):
        s1=np.nanvar(r); sums=[]
        for _,z in g:
            rr=z.ret.values
            for j in range(0,len(rr)-k+1,k): sums.append(rr[j:j+k].sum())
        sums=np.array(sums); vr[k]=np.var(sums)/(k*s1); 
        n=len(sums); vr[str(k)+'_z']=(vr[k]-1)/np.sqrt(2*(k-1)/ (n*k)) if n else np.nan
    res[lab]['VR']=vr
    # intraday cumulative mean and overnight mean
    res[lab]['mean_on_bp']=np.nanmean(on)*1e4; res[lab]['mean_intraday_bp']=np.nanmean(intraday)*1e4
for k,v in res.items():
    print(k)
    for kk,vv in v.items(): print('  ',kk, {a:(round(b,3) if isinstance(b,float) else b) for a,b in vv.items()} if isinstance(vv,dict) else (tuple(round(float(z),3) for z in vv) if isinstance(vv,tuple) else round(vv,2)))
# P2 signal days: D1 path
sd=[pd.Timestamp(x) for x in p2sig[p2sig].index]; dl=list(dclose.index)
rows=[]
for s in sd:
    k=dl.index(s)
    if k+1>=len(dl): continue
    d1=dl[k+1]; z=q[q.date==d1]
    if len(z)<7: continue
    op=z.open.iloc[0]; prev=dclose.iloc[k]
    rows.append(dict(gap=op/prev-1,b1=z.close.iloc[0]/op-1,o_to_c=z.close.iloc[-1]/op-1,minlow=z.low.min()/op-1,lowbar=int(z.low.values.argmin())+1,
                     path=[z.close.iloc[j]/op-1 for j in range(7)],b6_to_c=z.close.iloc[-1]/z.close.iloc[5]-1,d1_rest=z.close.iloc[-1]/z.close.iloc[0]-1))
P=pd.DataFrame(rows)
print('P2 signal days D1 n=',len(P))
print(' mean gap %.1fbp, bar1 %.1fbp, open->close %.1fbp, bar1close->close %.1fbp; share D1 close>open %.2f'%(P.gap.mean()*1e4,P.b1.mean()*1e4,P.o_to_c.mean()*1e4,P.d1_rest.mean()*1e4,(P.o_to_c>0).mean()))
print(' mean path (close of bar k vs D1 open, bp):',[round(np.mean([p[j] for p in P.path])*1e4,1) for j in range(7)])
print(' median intraday min low vs open %.1fbp; low occurs at bar distribution'%(P.minlow.median()*1e4),P.lowbar.value_counts().sort_index().to_dict())
r_=ac(P.gap.values,P.o_to_c.values); r2_=ac(P.b1.values,P.d1_rest.values); print(' corr(gap, open->close)',tuple(round(float(x),3) for x in r_),' corr(bar1, rest of day)',tuple(round(float(x),3) for x in r2_))
gd=P[P.gap<0]; gu=P[P.gap>=0]; print(' gap-down D1 n=%d open->close %.1fbp; gap-up n=%d open->close %.1fbp'%(len(gd),gd.o_to_c.mean()*1e4,len(gu),gu.o_to_c.mean()*1e4))
pickle.dump(dict(res=res,P=P),open('mom2.pkl','wb'))
