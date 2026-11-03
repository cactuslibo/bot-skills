import pandas as pd,numpy as np,os
from scipy import stats
E=pd.read_csv('events_all.csv'); E['date']=pd.to_datetime(E.date)
U={}
for f in os.listdir('ud'):
    try:
        d=pd.read_csv('ud/'+f); d['GradeDate']=pd.to_datetime(d.GradeDate).dt.normalize(); U[f[:-4]]=d
    except: pass
first=min(d.GradeDate.min() for d in U.values() if len(d))
rows=[]
for g in 'AB':
  for k in ('V','CTRL'):
    S=E[(E['grp'+g]==k)&(E.year>=2016)]
    for _,r in S.iterrows():
        d=U.get(r.ticker)
        if d is None or not len(d): continue
        w=d[(d.GradeDate>=r.date-pd.Timedelta(days=1))&(d.GradeDate<=r.date+pd.Timedelta(days=10))]
        pt=w[w.priorPriceTarget>0]
        rows.append(dict(定义=g,组=k,ticker=r.ticker,date=r.date,n=len(w),up=(w.Action=='up').sum(),down=(w.Action=='down').sum(),
          pt_raise=(w.priceTargetAction=='Raises').sum(),pt_lower=(w.priceTargetAction=='Lowers').sum(),
          pt_chg=(pt.currentPriceTarget/pt.priorPriceTarget-1).median() if len(pt) else np.nan,x120=r.x120))
A=pd.DataFrame(rows); A.to_csv('analyst_actions.csv',index=False)
A['net_pt']=(A.pt_raise-A.pt_lower)/(A.pt_raise+A.pt_lower).replace(0,np.nan)
G=A.groupby(['定义','组'])[['n','up','down','pt_raise','pt_lower','pt_chg','net_pt']].mean(); print(G.round(3)); G.to_csv('analyst_summary.csv')
for g in 'AB':
    a=A[(A.定义==g)&(A.组=='V')].pt_chg.dropna(); b=A[(A.定义==g)&(A.组=='CTRL')].pt_chg.dropna(); print(g,stats.ttest_ind(a,b,equal_var=False))
V=A[(A.定义=='B')&(A.组=='V')].dropna(subset=['pt_chg','x120']); print('corr ptchg vs x120 in BV',stats.spearmanr(V.pt_chg,V.x120))
print(first)
