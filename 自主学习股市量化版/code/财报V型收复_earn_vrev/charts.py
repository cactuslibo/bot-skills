import os
import pandas as pd,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Noto Sans CJK SC','WenQuanYi Zen Hei','DejaVu Sans']; plt.rcParams['axes.unicode_minus']=False
E=pd.read_csv('events_all.csv')
u=pd.read_csv('/workspace/tv_db/universe_10B.csv'); T=[t for t in u[u.type=='stock'].Symbol if t not in ('ET','IMO','CVE')]
C=pd.DataFrame({t:pd.read_csv(f'/workspace/tv_db/daily/{t}.csv',parse_dates=['date']).drop_duplicates('date').set_index('date').close for t in T if os.path.exists(f'/workspace/tv_db/daily/{t}.csv')}).sort_index()
R=C.pct_change(); mk=R.mean(axis=1)
H=250
def path(sub):
    P=[]
    for _,r in sub.iterrows():
        s=C[r.ticker].dropna(); i=s.index.searchsorted(pd.Timestamp(r.date))-1  # day before D
        if i+2+H>=len(s): continue
        ix=s.index[i:i+3+H]; ex=(R[r.ticker].loc[ix[1:]]-mk.loc[ix[1:]]).fillna(0)
        P.append(np.r_[0,np.cumsum(ex.values)])
    return np.nanmean(P,axis=0),len(P)
fig,ax=plt.subplots(1,2,figsize=(13,4.5))
for j,g in enumerate('AB'):
    for k,cl in (('V','tab:green'),('MID','tab:gray'),('CTRL','tab:red')):
        m,n=path(E[E['grp'+g]==k]); ax[j].plot(np.arange(-1,len(m)-1),m*100,color=cl,label=f'{k} (n={n})')
    ax[j].axhline(0,color='k',lw=.5); ax[j].axvline(2,ls='--',color='b',lw=.7); ax[j].set_title(f'定义{g}: 相对等权全市场的累计超额(%)，从财报前收盘起'); ax[j].set_xlabel('交易日（0=反应日D，虚线=入场D+2）'); ax[j].legend()
plt.tight_layout(); plt.savefig('fig_paths.png',dpi=110)
yd=pd.read_csv('year_dist.csv',index_col=0)
fig,ax=plt.subplots(figsize=(12,3.5)); yd[['V_A','V_B']].plot.bar(ax=ax); ax.set_title('V型事件年份分布（A=收盘口径，B=盘中低点口径）'); plt.tight_layout(); plt.savefig('fig_years.png',dpi=110)
fig,ax=plt.subplots(1,3,figsize=(15,4))
for a,(t,d) in zip(ax,[('U','2025-08-07'),('HCA','2026-10-27'),('ISRG','2026-10-21')]):
    s=pd.read_csv(f'/workspace/tv_db/daily/{t}.csv',parse_dates=['date']).set_index('date')
    w=s.loc[pd.Timestamp(d)-pd.Timedelta(days=90):pd.Timestamp(d)+pd.Timedelta(days=200)]
    a.plot(w.index,w.close); a.fill_between(w.index,w.low,w.high,alpha=.25); a.axvline(pd.Timestamp(d),color='r',ls='--'); a.set_title(f'{t} 财报反应日 {d}'); a.tick_params(axis='x',rotation=30)
plt.tight_layout(); plt.savefig('fig_examples.png',dpi=110)
