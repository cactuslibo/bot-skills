import pandas as pd, numpy as np, os, glob
from scipy import stats
u=pd.read_csv('/workspace/tv_db/universe_10B.csv'); T=[t for t in u[u.type=='stock'].Symbol if t not in ('ET','IMO','CVE')]
px={}
for t in T:
    p=f'/workspace/tv_db/daily/{t}.csv'
    if os.path.exists(p):
        d=pd.read_csv(p,parse_dates=['date']).drop_duplicates('date').set_index('date').sort_index()
        d=d[(d.close>0)&(d.low>0)]; px[t]=d
C=pd.DataFrame({t:d.close for t,d in px.items()})
# market benchmark: EW mean of forward returns across stocks
fwdmkt={h:(C.shift(-h)/C-1).mean(axis=1) for h in (20,60,120,250)}
def tz(x):
    try: return pd.Timestamp(x)
    except: return None
rows=[];cov=0
for t,d in px.items():
    p=f'ed/{t}.csv'
    if not os.path.exists(p): continue
    e=pd.read_csv(p)
    if 'Reported EPS' not in e: continue
    cov+=1
    idx=d.index; n=len(d); o,h,l,c,v=[d[k].values for k in ('open','high','low','close','volume')]
    ret=np.r_[np.nan,c[1:]/c[:-1]-1]
    gapdays=np.r_[0,np.diff(idx.values).astype('timedelta64[D]').astype(int)]
    for s,eps,sur in zip(e['Earnings Date'],e['Reported EPS'],e.get('Surprise(%)',np.nan)):
        if pd.isna(eps): continue
        ts=pd.Timestamp(str(s)[:19]); day=ts.normalize(); hr=ts.hour+ts.minute/60
        i0=idx.searchsorted(day)
        if i0>=n or i0<260: continue
        if idx[i0]!=day: i=i0
        elif hr>=16: i=i0+1
        elif 0<hr<9.5: i=i0
        else: i=i0 if abs(ret[i0])>=abs(ret[min(i0+1,n-1)]) else i0+1
        if i+252>=n+252 or i+2>=n: continue
        if gapdays[i-5:i+3].max()>7: continue
        C0=c[i-1]; r=c[i]/C0-1; sig=np.nanstd(ret[i-252:i]); lowr=l[i]/C0-1
        cc=(r<=-0.06) or (r<=-2*sig and r<=-0.03)
        cl=(lowr<=-0.06) or (lowr<=-2*sig and lowr<=-0.03)
        if not (cc or cl): continue
        rec1=(c[i+1]-c[i])/(C0-c[i]); rec2=(max(c[i+1],c[i+2])-c[i])/(C0-c[i])
        ent=i+2  # entry at D+2 close for all (no lookahead)
        row=dict(crash_close=cc,crash_low=cl,recL0=(c[i]-l[i])/(C0-l[i]),recL1=(c[i+1]-l[i])/(C0-l[i]),recL2=(max(c[i+1],c[i+2])-l[i])/(C0-l[i]),ticker=t,date=idx[i].date(),eps_time_hr=round(hr,2),surprise=sur,drop=r,sig1y=sig,drop_sig=r/sig,low_drop=lowr,
          gap=o[i]/C0-1,clv_D=(c[i]-l[i])/(h[i]-l[i]+1e-12),volx_D=v[i]/np.mean(v[i-21:i-1]),
          d1_ret=c[i+1]/c[i]-1,d1_gap=o[i+1]/c[i]-1,clv_D1=(c[i+1]-l[i+1])/(h[i+1]-l[i+1]+1e-12),volx_D1=v[i+1]/np.mean(v[i-21:i-1]),
          rec1=rec1,rec2=rec2,above_ma200=C0>np.mean(c[i-201:i-1]),pre60=C0/c[i-61]-1,pre250=C0/c[i-251]-1,
          clean_fwd=gapdays[i:min(n,ent+251)].max()<=7)
        for H in (20,60,120,250):
            if ent+H<n:
                seg=c[ent:ent+H+1]; row[f'r{H}']=seg[-1]/seg[0]-1
                row[f'mdd{H}']=(seg/np.maximum.accumulate(seg)-1).min()
                row[f'mkt{H}']=fwdmkt[H].get(idx[ent],np.nan); row[f'x{H}']=row[f'r{H}']-row[f'mkt{H}']
        if ent+120<n:
            y=np.log(c[ent:ent+121]); xx=np.arange(121); sl,ic,rr,_,_=stats.linregress(xx,y)
            row['slope120']=sl*252; row['r2_120']=rr**2; row['trend120']=(sl>0)&(rr**2>=0.6)
        rows.append(row)
E=pd.DataFrame(rows)
E['year']=pd.to_datetime(E.date).dt.year
E['grpA']=np.where(~E.crash_close,'NA',np.where(E.rec2>=0.7,'V',np.where(E.rec2<0.3,'CTRL','MID')))
E['grpB']=np.where(~E.crash_low,'NA',np.where(E.recL2>=0.7,'V',np.where(E.recL2<0.3,'CTRL','MID')))
E.to_csv('events_all.csv',index=False)
open('coverage.txt','w').write(f'stocks_used={len(px)} with_earn_dates={cov} cov={cov/len(px):.1%} crash_events={len(E)}\n')
print(open('coverage.txt').read()); print(E.grpA.value_counts(),E.grpB.value_counts())
