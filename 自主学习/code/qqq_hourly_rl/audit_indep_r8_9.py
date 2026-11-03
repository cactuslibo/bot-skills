exec(open('/workspace/qqq_hourly_rl/audit_indep_base.py').read().split("p2,_=run()")[0])
D.loc[~D.full,'r2px']=np.nan
lo14=q[q.index.time<=pd.Timestamp('14:30').time()].groupby('day').low.min().reindex(D.index)
b14=q[q.index.time==pd.Timestamp('14:30').time()]; b14=pd.Series((b14.close>b14.open).values,index=b14.day.values).reindex(D.index).fillna(False)
br13=(at(AD,'decl','13:30')/(at(AD,'decl','13:30')+at(AD,'advn','13:30'))).reindex(D.index)
v13=at(VHr,'close','13:30').reindex(D.index)
def run2(sig,lo='2022-01-01',hi='2026-10-30'):
    c=D.c.values;o=D.o.values;n=len(D);es=[];xs=[];inpos=False;trig=[]
    for d in range(6,n):
        if inpos:
            if d>=e and c[d]>D.sma5.values[d]: inpos=False; xs.append(d+1)
            continue
        if sig[d] and D.full.values[d]: inpos=True;e=d+1;es.append(('moc',e));trig.append(D.index[d]);continue
        if D.r2.values[d]<15 and D.ratio.values[d]<1: inpos=True;e=d+1;es.append(('open',e))
    if len(xs)<len(es): xs.append(n)
    r=np.zeros(n);pc=np.r_[c[0],c[:-1]];tr=[];held=np.zeros(n)
    for (m,e),x in zip(es,xs):
        if m=='moc': r[e-1]-=5e-4
        else: r[e]-=5e-4
        for d in range(e,min(x,n)):
            if d>e or m=='moc': r[d]+=o[d]/pc[d]-1
            r[d]+=c[d]/o[d]-1
        if x<n: r[x]+=o[x]/pc[x]-1-5e-4
        held[e:min(x,n)]=1
        tr.append((D.index[min(e,n-1)],np.prod(1+r[(e-1 if m=='moc' else e):min(x,n-1)+1])-1))
    idx=D.index;mk=(idx>=lo)&(idx<hi);rf=np.array([EFFR[t.year]/100/252 for t in idx])
    eq=np.cumprod(1+r[mk]);exs=(r+(1-held)*rf-rf)[mk];t=[w for d0,w in tr if lo<=str(d0.date())<hi]
    tt=lambda a,b:sum(1 for x in trig if pd.Timestamp(a)<=x<pd.Timestamp(b))
    return dict(cagr=round(eq[-1]**(252/mk.sum())-1,4),mdd=round((eq/np.maximum.accumulate(eq)-1).min(),4),exS=round(exs.mean()/exs.std()*np.sqrt(252),3),n=len(t),win=round(np.mean([w>0 for w in t]),4),avgw=round(held[mk].mean(),4),trig_train=tt('2015-01-01','2022-01-01'),trig_val=tt('2022-01-01','2026-10-30'))
with np.errstate(invalid='ignore'):
  H2=((D.r2px<30)&(D.br>=0.6)&(D.px>=lo14*1.006)&b14&(D.br<br13)).values
  H3=((D.r2px<30)&(D.vix<=D.vhi*0.96)&(D.br>=0.65)&b14&(D.vix<v13)).values
print('H2',run2(H2)); print('H3',run2(H3)); print('P2',run2(np.zeros(len(D),bool)))
