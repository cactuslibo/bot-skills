import glob, os, sys, pandas as pd, numpy as np
B='/workspace/wyckoff'; problems=[]
def load(p, raw):
    try:
        d=pd.read_csv(p)
        if raw: d=d[['time','open','high','low','close','Volume']].rename(columns={'time':'date','Volume':'volume'})
        else: d=d[['date','open','high','low','close','volume']]
        d['date']=pd.to_datetime(d['date'].astype(str).str[:10],errors='coerce')
        d=d.dropna(subset=['date','high','low','close']).drop_duplicates('date').sort_values('date').reset_index(drop=True)
        d['volume']=d['volume'].fillna(0); return d
    except Exception as e: problems.append(f'{os.path.basename(p)}: {e}'); return None
def files():
    f={os.path.basename(p)[:-4]:(p,False) for p in glob.glob(B+'/data_1b/*.csv')}
    f.update({os.path.basename(p)[:-4]:(p,True) for p in glob.glob(B+'/raw/*.csv')})
    if 'CRCL' not in f: f['CRCL']=(B+'/CRCL_daily.csv',False)
    return f
def analyze(full):
    r={'ok':False}; n0=len(full)
    if n0<120: r['fail']='too few bars'; return r
    off=max(0,n0-252); d=full.iloc[off:].reset_index(drop=True); n=len(d)
    lo,hi,cl,v=d.low.values,d.high.values,d.close.values,d.volume.values.astype(float)
    av20=pd.Series(full.volume.values.astype(float)).rolling(20).mean().shift(1).values[off:]
    # SC: lowest low; if it is a Spring (late, recovered in 3 days) use the earlier lowest low
    sc=int(np.argmin(lo)); spring=None
    if sc>40:
        sc2=int(np.argmin(lo[:sc-40])) 
        rec=any(cl[sc:sc+4]>lo[sc2])
        if rec and lo[sc]<lo[sc2]: spring=sc; sc=sc2
    r.update(sc_date=d.date[sc].date(),sc_price=lo[sc],spring_date=d.date[spring].date() if spring is not None else None)
    g=sc+off; pre=full.high.values[max(0,g-126):g+1]; ph=pre.max(); r['decline_pct']=round((1-lo[sc]/ph)*100,1)
    r['R1']=r['decline_pct']>=40
    vr=[v[i]/av20[i] for i in range(max(0,sc-3),min(n,sc+4)) if av20[i]>0]
    r['sc_vol_ratio']=round(max(vr),2) if vr else np.nan; r['R2']=bool(vr) and max(vr)>=1.3
    if sc+1>=n: r['fail']='no bars after SC'; return r
    ar=sc+1+int(np.argmax(hi[sc+1:sc+31])); r.update(ar_date=d.date[ar].date(),ar_price=hi[ar],ar_pct=round((hi[ar]/lo[sc]-1)*100,1))
    r['R3']=hi[ar]>=1.25*lo[sc]; H=hi[ar]-lo[sc]
    s=ar+40
    if s>=n: r['R4']=False; r['fail']='<40 bars after AR'; return r
    seg=lo[s:].copy()
    if spring is not None and spring>=s: seg[spring-s]=np.inf
    c=s+int(np.argmin(seg)); ago=n-1-c
    if spring is not None and spring>=s: c=spring; ago=n-1-c; cp=lo[c]; r4=30<=ago<=120
    else: cp=lo[c]; r4=(cp>lo[sc]) and (cp-lo[sc]<=0.25*H) and 30<=ago<=120
    r.update(c_low_date=d.date[c].date(),c_low_price=cp,c_days_ago=ago,c_pct_of_range=round((cp-lo[sc])/H*100,1),R4=bool(r4))
    mid=lo[sc]+H/2; rv=[v[i]/av20[i] for i in range(c,n) if av20[i]>0]
    r['max_vol_ratio']=round(max(rv),2) if rv else np.nan
    r['R5']=bool(cl[c:].max()>mid and rv and max(rv)>=1.5)
    r.update(last_close=cl[-1],range_pct=round((cl[-1]-lo[sc])/H*100,1))
    r['R6']=bool(cp<cl[-1]<hi[ar])
    r['broke_recent']=bool((cl[-10:]>hi[ar]).any())
    a10=v[-10:].mean(); a20=v[-20:].mean()
    r['low_vol_pullback']=bool(a10<a20); r['bo_vol']=bool(cl[-1]>hi[ar] and v[-1]>a20)
    r['last_date']=d.date.iloc[-1].date()
    base=all(r[k] for k in ['R1','R2','R3','R4','R5'])
    r['breakout']=bool(base and not r['R6'] and r['broke_recent'])
    r['ok']=bool(base and (r['R6'] or r['breakout'])); return r
if __name__=='__main__':
    u=pd.read_csv(B+'/universe.csv').drop_duplicates('ticker').set_index('ticker')
    F=files(); rows=[]; scanned=0; stale=[]
    for t,(p,raw) in sorted(F.items()):
        d=load(p,raw)
        if d is None or len(d)==0: continue
        scanned+=1
        if d.date.iloc[-1]<pd.Timestamp('2026-10-01'): stale.append((t,d.date.iloc[-1].date()))
        try: r=analyze(d)
        except Exception as e: problems.append(f'{t}: {e}'); continue
        if t=='CRCL': print('CRCL:',r)
        if r['ok']:
            r['ticker']=t; r['market_cap']=u.market_cap.get(t,np.nan); r['sector']=u.sector.get(t,'')
            r['bonus']=int(r['low_vol_pullback'])+int(r['bo_vol'] or r['breakout']); rows.append(r)
    cols=['ticker','sc_date','sc_price','ar_date','ar_price','c_low_date','c_low_price','max_vol_ratio','last_close','range_pct','low_vol_pullback','breakout','market_cap','sector']
    o=pd.DataFrame(rows)
    if len(o): o=o.sort_values(['bonus','range_pct'],ascending=[False,False])
    o.reindex(columns=cols).to_csv(B+'/scan_schematic2.csv',index=False)
    print('scanned',scanned,'hits',len(o),'breakouts',int(o.breakout.sum()) if len(o) else 0)
    print(o.reindex(columns=cols+['bonus','decline_pct','c_days_ago']).head(20).to_string())
    print('universe',len(u),'files not in universe',[t for t in F if t not in u.index][:20])
    print('stale',len(stale),stale[:15]); print('problems',problems[:20])
