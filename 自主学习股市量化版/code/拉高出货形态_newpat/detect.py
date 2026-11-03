import pandas as pd, numpy as np, os, sys
from multiprocessing import Pool
D='/workspace/tv_db/daily'; U=pd.read_csv('/workspace/tv_db/universe_10B.csv')
TYPE=dict(zip(U.Symbol,U.type))
BROAD={'SPY','QQQ','DIA','IWM','VTI','EFA','EEM','TLT','IEF','AGG','BND','VOO','IVV','LQD','HYG','SHY'}
P={'stock':dict(Ag=.40,Pr=.18,brk=.08,Bg=.20,C1=.30,C2=.25),'etf':dict(Ag=.20,Pr=.10,brk=.05,Bg=.10,C1=.20,C2=.15)}
def ind(df):
    c,h,l,v,o=df.close,df.high,df.low,df.volume,df.open
    r=np.log(c).diff(); df['sig']=r.rolling(252).std()
    df['r20']=c.pct_change(20); df['r20rank']=df.r20.expanding(252).rank(pct=True)
    df['hi252']=c.rolling(252).max(); df['ath']=c.cummax()
    df['obv']=(np.sign(c.diff()).fillna(0)*v).cumsum()
    mfm=((c-l)-(h-c))/(h-l).replace(0,np.nan); mfm=mfm.fillna(0)
    df['ad']=(mfm*v).cumsum(); df['cmf']=(mfm*v).rolling(20).sum()/v.rolling(20).sum()
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    df['atrp']=tr.rolling(14).mean()/c
    ma20=c.rolling(20).mean(); df['bbw']=4*c.rolling(20).std()/ma20
    df['atrp_pct']=df.atrp.rolling(504,min_periods=252).rank(pct=True)
    df['bbw_pct']=df.bbw.rolling(504,min_periods=252).rank(pct=True)
    d=c.diff(); up=d.clip(lower=0).ewm(alpha=1/14).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/14).mean()
    df['rsi']=100-100/(1+up/dn)
    df['ma50']=c.rolling(50).mean(); df['ma200']=c.rolling(200).mean(); df['v50']=v.rolling(50).mean()
    df['ush']=(h-np.maximum(o,c))/(h-l).replace(0,np.nan)
    return df
def run(t):
    try:
        df=pd.read_csv(f'{D}/{t}.csv',parse_dates=['date']).dropna(subset=['close']).reset_index(drop=True)
    except Exception: return []
    if t=='IMO': df=df[df.date>='1970-01-01'].reset_index(drop=True)
    if len(df)<400 or df.close.le(0).any(): return []
    df=ind(df); k=TYPE[t]; p=P[k]; C=df.close.values; Hh=df.high.values; L=df.low.values; n=len(C)
    lc=np.log(C); out=[]; lastH=-999
    cand=np.where((df.close>=df.hi252-1e-9).values & (pd.Series(C).rolling(11,center=True,min_periods=1).max().values<=C+1e-9))[0]
    for H in cand:
        if H<300 or H-lastH<30: continue
        done=False
        for b in range(H-5,H-31,-1):
            if done: break
            for pl in range(90,14,-1):
                ps,pe=b-pl,b-1
                if ps<260: continue
                pc=C[ps:pe+1]; up=pc.max(); lo=np.percentile(pc,10)
                if C[b]<=up*1.02 or C[b-1]>up*1.02: continue
                if (up-lo)/lo>p['Pr']: continue
                below=np.where(pc<lo)[0]; flag=0; ok=True
                for i in below:
                    if pc[i]<lo*(1-p['brk']): ok=False;break
                    flag=1
                if not ok: continue
                if H<n and C[H]/up-1<p['Bg']: continue
                # A
                aok=None
                for al in range(10,61):
                    a0,a1=ps-al,ps-1
                    seg=C[a0:a1+1]; imn=seg.argmin(); imx=seg.argmax()
                    if imx<=imn or imx<len(seg)-6: continue
                    g=seg[imx]/seg[imn]-1
                    if g<p['Ag']: continue
                    sl=(np.log(seg[imx])-np.log(seg[imn]))/(imx-imn)
                    crit=sl>=1.5*df.sig.iat[a1] or df.r20rank.iat[a1]>=.9
                    if not crit: continue
                    Amax,Amin=seg[imx],seg[imn]
                    if np.median(pc)<Amax-.3*(Amax-Amin): continue
                    aok=(a0+imn,a0+imx,g,sl);break
                if not aok: continue
                bsl=(lc[H]-lc[pe])/(H-pe)
                if bsl<1.2*aok[3]: continue
                out.append((ps,pe,b,flag,up,lo,aok)); done=True;break
        if done: lastH=H; out[-1]=out[-1]+(H,)
    rows=[]
    gapd=df.date.diff().dt.days.fillna(1).values; zv=(df.volume.values<=0); jr=df.close.pct_change().fillna(0).values
    for ps,pe,b,flag,up,lo,(as_,ae,ag,asl),H in out:
        e=min(H+64,n)
        if (gapd[as_:e]>7).any() or zv[as_:e].any() or (jr[as_:e]<-.4).any() or (jr[as_:e]>.6).any(): continue
        if t=='ET' and df.date.iat[as_]<=pd.Timestamp('2016-02-29') and df.date.iat[e-1]>=pd.Timestamp('2016-01-01'): continue
        if H+63>=n: status='pending'; 
        fut=L[H+1:H+64]; dd63=fut.min()/C[H]-1 if len(fut) else np.nan
        dd40=L[H+1:H+41].min()/C[H]-1 if H+1<n else np.nan
        if dd63<=-p['C1']: g='crash'
        elif dd40<=-p['C2']: g='crash2'
        elif H+63>=n: g='pending'
        else: g='control'
        ci=H+1+int(np.argmin(fut)) if len(fut) else H
        v=df.volume.values; w=slice(max(H-5,0),min(H+6,n))
        bv=v[b:H+1].mean(); pv=v[ps:pe+1].mean(); av=v[as_:ae+1].mean()
        # gaps in B
        o=df.open.values; gaps=0; filled=0
        for i in range(b,H+1):
            if L[i]>Hh[i-1]*1.0:
                gaps+=1
                if (L[i+1:min(i+64,n)]<=Hh[i-1]).any(): filled+=1
        ud=0;mx=0
        for i in range(as_,H+1):
            ud=ud+1 if C[i]>C[i-1] else 0; mx=max(mx,ud) if i>=b else mx
        rv=v[w]/df.v50.values[w]; ush=df.ush.values[w]; rr=np.abs(np.diff(lc[max(H-6,0):min(H+6,n)]))
        stall=int(sum((rv[j]>1.5) and (abs(C[w][j]/C[w.start+j-1]-1)<.01 or ush[j]>.5) for j in range(len(rv))))
        obv=df.obv.values; ad=df.ad.values
        rows.append(dict(ticker=t,type=k,year=df.date.iat[H].year,group=g,A_start=df.date.iat[as_].date(),A_end=df.date.iat[ae].date(),
          P_start=df.date.iat[ps].date(),P_end=df.date.iat[pe].date(),B_date=df.date.iat[b].date(),H_date=df.date.iat[H].date(),
          C_date=df.date.iat[ci].date() if g in('crash','crash2') else None,H_close=C[H],A_gain=ag,P_range=(up-lo)/lo,P_break_flag=flag,
          B_gain=C[H]/up-1,H_ath=int(C[H]>=df.ath.iat[H]-1e-9),dd63=dd63,dd40=dd40,
          volB_vs_P=bv/pv,volP_vs_A=pv/av,volH_vs_50=v[H]/df.v50.iat[H],volmaxH5_vs_50=np.nanmax(rv),
          ushadow_days_H5=int(np.nansum(ush>.5)),hivol_stall_H5=stall,gapsB=gaps,gaps_filled=filled,
          obv_div=int(obv[b:H+1].max()<=obv[ps:pe+1].max()),ad_div=int(ad[b:H+1].max()<=ad[ps:pe+1].max()),
          cmf_H=df.cmf.iat[H],cmf_P=df.cmf.iat[pe],atrp_pct_P=df.atrp_pct.iat[pe],bbw_pct_P=df.bbw_pct.iat[pe],
          rsi_H=df.rsi.iat[H],dist_ma50=C[H]/df.ma50.iat[H]-1,dist_ma200=C[H]/df.ma200.iat[H]-1,
          slopeB_A=((lc[H]-lc[pe])/(H-pe))/asl,max_upstreak_B=mx,B_days=H-b+1,P_days=pe-ps+1))
    return rows
if __name__=='__main__':
    ts=[t for t in U.Symbol if t not in BROAD and os.path.exists(f'{D}/{t}.csv') and os.path.getsize(f'{D}/{t}.csv')>1000]
    with Pool(os.cpu_count()) as pl: R=pl.map(run,ts)
    ev=pd.DataFrame([r for x in R for r in x]); print(len(ts),'tickers',len(ev))
    ev.to_csv('events_all.csv',index=False)
    ev[ev.group.isin(['crash','crash2'])].to_csv('crash_list.csv',index=False)
    ev[ev.group=='control'].to_csv('control_list.csv',index=False)
    print(ev.groupby(['type','group']).size())
