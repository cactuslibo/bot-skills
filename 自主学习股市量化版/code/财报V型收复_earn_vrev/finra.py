import pandas as pd,numpy as np,os,subprocess
from concurrent.futures import ThreadPoolExecutor
E=pd.read_csv('events_all.csv'); E=E[E.grpB.isin(['V','CTRL'])&(E.year>=2023)].copy()
os.makedirs('finra',exist_ok=True)
need={}
for _,r in E.iterrows():
    d=pd.read_csv(f'/workspace/tv_db/daily/{r.ticker}.csv').date.tolist(); i=d.index(r.date)
    need[(r.ticker,r.date)]=[d[k] for k in list(range(i-10,i-5))+[i,i+1,i+2]]
dates=sorted({x for v in need.values() for x in v})
print(len(E),len(dates))
def get(x):
    p=f'finra/{x}.txt'
    if not os.path.exists(p): subprocess.run(['curl','-s','-f','-o',p,f'https://cdn.finra.org/equity/regsho/daily/CNMSshvol{x.replace("-","")}.txt'])
with ThreadPoolExecutor(8) as ex: list(ex.map(get,dates))
cache={}
def load(x):
    if x not in cache:
        try: cache[x]=pd.read_csv(f'finra/{x}.txt',sep='|').set_index('Symbol')
        except: cache[x]=None
    return cache[x]
rows=[]
for (t,dt),ds in need.items():
    vals=[]
    for x in ds:
        f=load(x); s=t.replace('.','')  # FINRA uses e.g. BRK.B? 
        if f is None or (t not in f.index): vals.append(np.nan); continue
        rr=f.loc[t]; vals.append(rr.ShortVolume/rr.TotalVolume)
    rows.append(dict(ticker=t,date=dt,ssr_base=np.nanmean(vals[:5]),ssr_D=vals[5],ssr_D1=vals[6],ssr_D2=vals[7]))
F=pd.DataFrame(rows).merge(E[['ticker','date','grpB','x60','x120']],on=['ticker','date'])
F.to_csv('finra_shortvol.csv',index=False)
F['dD']=F.ssr_D-F.ssr_base; F['dD1']=F.ssr_D1-F.ssr_base
print(F.groupby('grpB')[['ssr_base','ssr_D','ssr_D1','ssr_D2','dD','dD1']].agg(['mean','count']).round(3).T)
from scipy import stats
for c in ('dD','dD1'):
    print(c,stats.ttest_ind(F[F.grpB=='V'][c].dropna(),F[F.grpB=='CTRL'][c].dropna(),equal_var=False))
