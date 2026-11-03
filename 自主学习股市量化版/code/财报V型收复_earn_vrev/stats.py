import pandas as pd, numpy as np
from scipy import stats
E=pd.read_csv('events_all.csv'); E['date']=pd.to_datetime(E.date)
E['crash_lowB']=(E.low_drop<=-0.05)&(E.low_drop<=-2.5*E.sig1y)&(E['drop']<0)
E['grpB']=np.where(~E.crash_lowB,'NA',np.where(E.recL2>=0.7,'V',np.where(E.recL2<0.3,'CTRL','MID')))
E.to_csv('events_all.csv',index=False)
out=[]
def summ(df,name):
    r={'组':name,'N':len(df)}
    for H in (20,60,120,250):
        x=df[f'r{H}'].dropna(); xs=df[f'x{H}'].dropna()
        r[f'r{H}均值']=x.mean(); r[f'r{H}中位']=x.median(); r[f'超额{H}均值']=xs.mean(); r[f'胜率{H}']=(x>0).mean(); r[f'超额胜率{H}']=(xs>0).mean()
        r[f'MDD{H}中位']=df[f'mdd{H}'].median()
    r['趋势120比例']=df.trend120.dropna().astype(bool).mean()
    return r
for g in 'AB':
    col='grp'+g
    for k in ('V','MID','CTRL'): out.append(summ(E[E[col]==k],f'{g}-{k}'))
S=pd.DataFrame(out); S.to_csv('summary_groups.csv',index=False)
# significance V vs CTRL
sig=[]
for g in 'AB':
    v=E[E['grp'+g]=='V']; c=E[E['grp'+g]=='CTRL']
    for H in (20,60,120,250):
        a=v[f'x{H}'].dropna(); b=c[f'x{H}'].dropna()
        t,p=stats.ttest_ind(a,b,equal_var=False); u,pu=stats.mannwhitneyu(a,b)
        t1,p1=stats.ttest_1samp(a,0)
        # cluster by month: average per month then t
        m=v.dropna(subset=[f'x{H}']).groupby(v.date.dt.to_period('M'))[f'x{H}'].mean(); tm,pm=stats.ttest_1samp(m,0)
        sig.append(dict(定义=g,H=H,V均超额=a.mean(),CTRL均超额=b.mean(),差=a.mean()-b.mean(),Welch_t=t,p=p,MWU_p=pu,V超额t=t1,V超额p=p1,月聚类t=tm,月聚类p=pm))
    a=v.trend120.dropna().astype(bool); b=c.trend120.dropna().astype(bool)
    tab=[[a.sum(),len(a)-a.sum()],[b.sum(),len(b)-b.sum()]]; sig.append(dict(定义=g,H='trend120',V均超额=a.mean(),CTRL均超额=b.mean(),差=a.mean()-b.mean(),p=stats.chi2_contingency(tab)[1]))
pd.DataFrame(sig).to_csv('significance.csv',index=False)
# unconditional trend120 base rate: random sample all stock-days
import os
pd.set_option('display.width',250)
print(S[['组','N','r20均值','r60均值','r120均值','r250均值','超额120均值','超额250均值','胜率120','MDD120中位','趋势120比例']].round(3).to_string())
print(pd.DataFrame(sig).round(4).to_string())
yr=pd.crosstab(E.year,[E.grpA,E.grpB]); 
pd.crosstab(E.year,E.grpA).join(pd.crosstab(E.year,E.grpB),lsuffix='_A',rsuffix='_B').to_csv('year_dist.csv')
for g in 'AB': E[E['grp'+g]=='V'].sort_values('date').to_csv(f'events_V_{g}.csv',index=False); E[E['grp'+g]=='CTRL'].to_csv(f'events_CTRL_{g}.csv',index=False)
