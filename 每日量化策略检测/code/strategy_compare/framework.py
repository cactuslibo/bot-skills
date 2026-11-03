"""通用多策略回测框架。新增策略：写一个 f(px, mkt)->仓位Series(0..1，T日收盘信号)，加入 STRATEGIES 字典即可。
px: DataFrame(open,high,low,close) 标的自身；mkt: dict 市场级序列(vix,vxn,hyg,lqd,rf) 已对齐到 px.index。
执行：shift(1) 次日，单边5bp，空仓部分拿T-bill(^IRX/252)。v1/v2 参数冻结自 /workspace/ndx_escape (bt.py/v2.py)。"""
import pandas as pd, numpy as np, json, sys
D='/workspace/ndx_escape/'; E='/workspace/etf19_data/daily/'
rd=lambda f: pd.read_csv(f,index_col=0,parse_dates=True)
MK={k:rd(D+f+'.csv').Close for k,f in dict(vix='VIX',vxn='VXN',hyg='HYG',lqd='LQD',irx='IRX').items()}
sma=lambda x,k:x.rolling(k).mean(); rma=lambda x,k:x.ewm(alpha=1/k,adjust=False).mean()
def load(t):
    if t=='NDX':
        d=rd(D+'NDX.csv'); d.columns=[c.lower() for c in d.columns]
    else: d=rd(E+t+'.csv')
    d=d[['open','high','low','close','volume']].dropna(subset=['close']); idx=d.index
    m={k:v.reindex(idx.union(v.index)).ffill().reindex(idx) for k,v in MK.items()}
    m['vxn']=m['vxn'].combine_first(m['vix']); m['rf']=(m['irx']/100/252).fillna(0)
    return d,m
def _score(px,m,volidx):
    c=px.close; ret=c.pct_change().fillna(0); s50,s200=sma(c,50),sma(c,200); v=m[volidx]
    D1=pd.Series(np.where(c<s200,1.0,np.where((c<s50)&(s50<s50.shift(5)),0.5,0.0)),c.index)
    rv=ret.rolling(20).std()*np.sqrt(252); rvp=rv.rolling(252).rank(pct=True)
    D2=(((v/sma(v,50))>1.25)|(rvp>0.8)).astype(float)*0.5+(rvp>0.9).astype(float)*0.5
    d=c.diff(); rsi=100-100/(1+rma(d.clip(lower=0),14)/rma((-d).clip(lower=0),14))
    macd=c.ewm(span=12).mean()-c.ewm(span=26).mean(); hist=macd-macd.ewm(span=9).mean()
    newhi=c>=c.rolling(63).max()
    div=newhi&((rsi<rsi.shift(10).rolling(53).max()-5)|(hist<hist.shift(10).rolling(53).max()*0.5))
    D3=div.astype(float).rolling(10).max().fillna(0)
    ext=c/s200-1; D4=(ext>ext.expanding(500).quantile(0.95).shift(1)).astype(float)
    cr=m['hyg']/m['lqd']; D5=(cr<sma(cr,50)).astype(float).where(cr.notna())
    W={'D1':35,'D2':25,'D3':15,'D4':10,'D5':15}; comp=dict(D1=D1,D2=D2,D3=D3,D4=D4,D5=D5)
    num=sum(comp[k].fillna(0)*W[k] for k in W); den=sum(comp[k].notna()*W[k] for k in W)
    return 100*num/den, dict(c=c,s50=s50,s20=sma(c,20),newhi=newhi,rv=rv,v=v)
def v1(px,m,lo=40,hi=60,band=10):
    sc,z=_score(px,m,'vix'); vx20=sma(z['v'],20); w=1.0; out=[]
    for i in range(len(sc)):
        s=sc.iloc[i]; tgt=1.0 if s<lo else (0.5 if s<hi else 0.0)
        if tgt<w: w=tgt
        elif tgt>w and s<(lo if w==0.5 else hi)-band and z['c'].iloc[i]>z['s20'].iloc[i]: w=min(1.0,w+0.5)
        if w<1 and z['c'].iloc[i]>z['s50'].iloc[i] and (np.isnan(vx20.iloc[i]) or z['v'].iloc[i]<vx20.iloc[i]): w=max(w,0.5)
        if z['newhi'].iloc[i]: w=1.0
        out.append(w)
    return pd.Series(out,sc.index),sc
def v2(px,m,lo=50,hi=70):
    sc,z=_score(px,m,'vxn'); c=z['c']; dh=c/c.rolling(252).max()-1
    volexp=(z['rv']/sma(z['rv'],50)>1.2)|(z['v']/sma(z['v'],50)>1.25); w=1.0; out=[]
    for i in range(len(sc)):
        s=sc.iloc[i]; tgt=1.0 if s<lo else (0.5 if s<hi else 0.0)
        if tgt<w: w=tgt
        elif tgt>w and s<(lo if w==0.5 else hi)-10 and c.iloc[i]>z['s20'].iloc[i]: w=min(1.0,w+0.5)
        if z['newhi'].iloc[i] or (dh.iloc[i]<-0.08 and volexp.iloc[i]): w=1.0
        out.append(w)
    return pd.Series(out,sc.index),sc
STRATEGIES={'v1':v1,'v2':v2}
def register_daily():
    import strategies_daily as S
    STRATEGIES.update({'MyRSI':S.myrsi,'园园1x':S.siji_1x,'园园AI_1x':S.yuanyuan_ai_1x,'园园AI_3x':S.yuanyuan_ai_3x,'P2':S.p2})
NDX_ONLY={'园园AI_1x','园园AI_3x'}   # 只适用 QQQ 信号/TQQQ 持仓
COST=0.0005
def port_returns(px,m,w):
    """w: 仓位Series(0..1, T日收盘信号) 或 dict(legs=[(权重Series,资产日收益Series),...])。返回(组合日收益, 总敞口ws)。T+1执行、单边5bp、剩余拿T-bill"""
    c=px.close; ret=c.pct_change().fillna(0)
    legs=w['legs'] if isinstance(w,dict) else [(w,ret)]
    r=pd.Series(0.0,c.index); tot=pd.Series(0.0,c.index); cost=pd.Series(0.0,c.index)
    for i,(wl,rl) in enumerate(legs):
        ws=wl.shift(1).fillna(1.0 if i==0 else 0.0); r+=ws*rl.fillna(0); tot+=ws; cost+=ws.diff().abs().fillna(0)
    return r+(1-tot)*m['rf']-cost*COST, tot
def run_year(px,m,w,yr):
    c=px.close; ret=c.pct_change().fillna(0); mk=c.index.year==yr
    R,T=port_returns(px,m,w); ws=T[mk]; r=R[mk].copy()   # 年初延续上一交易日的真实仓位（含预热期），不强制满仓
    b=ret[mk].copy()
    rfy=m['rf'][mk]
    def st(x):   # Sharpe 用超额收益(扣T-bill)，避免全年空仓时现金收益波动≈0导致 Sharpe 爆表
        eq=(1+x).cumprod(); ex=x-rfy; sd=ex.std()
        return dict(ret=eq.iloc[-1]-1,mdd=(eq/eq.cummax()-1).min(),sharpe=ex.mean()/sd*np.sqrt(252) if sd>1e-6 else 0.0)
    cuts=fly=0; idx=ws.index
    for i in range(1,len(ws)):
        if ws.iloc[i]<ws.iloc[i-1]:
            cuts+=1; j=c.index.get_loc(idx[i])+20
            if j<len(c) and c.iloc[j]>c.loc[idx[i-1]]: fly+=1
    s=st(r); bh=st(b)
    return dict(ret=s['ret'],mdd=s['mdd'],sharpe=s['sharpe'],bh_ret=bh['ret'],bh_mdd=bh['mdd'],bh_sharpe=bh['sharpe'],trades=int((ws.diff().abs()>0).sum()),cuts=cuts,sellfly=fly,avg_pos=ws.mean(),ndays=int(mk.sum()))
YEARS=[2018,1999,2005,2004,2006,2025,2007,2003,2021,2026]
TICK=['NDX','XLB','XLC','XLE','XLF','XLI','XLK','XLP','XLRE','XLU','XLV','XLY','ARKB','ARKF','ARKG','ARKK','ARKQ','ARKW','ARKX','IZRL','PRNT']
if __name__=='__main__':
    register_daily()
    rows=[];skips=[];cur=[];DAILY={}
    for t in TICK:
        px,m=load(t); grp='NDX' if t=='NDX' else ('XL' if t.startswith('XL') else 'ARK')
        W={k:f(px,m) for k,f in STRATEGIES.items() if not (t!='NDX' and k in NDX_ONLY)}
        cur.append(dict(ticker=t,date=str(px.index[-1].date()),close=px.close.iloc[-1],**{f'{k}_pos':(sum(l[0].iloc[-1] for l in W[k][0]['legs']) if isinstance(W[k][0],dict) else W[k][0].iloc[-1]) for k in W},**{f'{k}_score':W[k][1].iloc[-1] for k in W if W[k][1] is not None}))
        for y in YEARS:
            n=(px.index.year==y).sum(); warm=(px.index.year<y).sum()
            if n==0: skips.append(dict(ticker=t,year=y,reason='无数据')); continue
            if y!=2026 and n<200: skips.append(dict(ticker=t,year=y,reason=f'不完整({n}日)')); continue
            for k in W:
                w0=W[k][0]; wchk=w0['legs'][0][0] if isinstance(w0,dict) else w0
                if wchk[px.index.year==y].isna().any(): skips.append(dict(ticker=t,year=y,reason=f'{k}:数据缺(VIX3M)')); continue
                R_,T_=port_returns(px,m,W[k][0]); mk_=px.index.year==y; DAILY[(t,y,k)]=pd.DataFrame(dict(s=R_[mk_],b=px.close.pct_change()[mk_].fillna(0),rf=m['rf'][mk_],w=T_[mk_]))
                rows.append(dict(ticker=t,group=grp,year=y,strategy=k,warmup_days=int(warm),**run_year(px,m,W[k][0],y)))
    df=pd.DataFrame(rows); df.to_csv('results_by_year.csv',index=False)
    import pickle; pickle.dump(DAILY,open('daily_returns.pkl','wb'))
    pd.DataFrame(skips).to_csv('skipped.csv',index=False); pd.DataFrame(cur).to_csv('current_signals.csv',index=False)
    h=df[df.year!=2026].copy(); h['win']=h.ret>h.bh_ret; h['mdd_better']=h.mdd>h.bh_mdd; h['sh_win']=h.sharpe>h.bh_sharpe
    out={}
    for g,sub in [('XL',h[h.group=='XL']),('ARK',h[h.group=='ARK']),('ETF全部',h[h.group!='NDX']),('NDX',h[h.group=='NDX'])]:
        for k,s in sub.groupby('strategy'):
            out[f'{g}|{k}']=dict(n=len(s),ret=s.ret.mean(),bh=s.bh_ret.mean(),mdd=s.mdd.mean(),bh_mdd=s.bh_mdd.mean(),sh=s.sharpe.mean(),bh_sh=s.bh_sharpe.mean(),wins=int(s.win.sum()),mdd_better=int(s.mdd_better.sum()),sh_wins=int(s.sh_win.sum()),cuts=int(s.cuts.sum()),sellfly=int(s.sellfly.sum()))
    y26=df[df.year==2026].groupby(['group','strategy'])[['ret','bh_ret','mdd','bh_mdd']].mean()
    pt=h.groupby(['ticker','strategy']).agg(n=('year','size'),ret=('ret','mean'),bh=('bh_ret','mean'),wins=('win','sum'),mdd=('mdd','mean'),bh_mdd=('bh_mdd','mean')).reset_index(); pt.to_csv('per_ticker_summary.csv',index=False)
    json.dump(dict(summary=out,y2026=y26.reset_index().to_dict('records')),open('summary.json','w'),ensure_ascii=False,indent=1,default=float)
    print(pd.DataFrame(out).T.round(3).to_string()); print(y26.round(3)); print(pt.round(3).to_string()); print(pd.DataFrame(skips).groupby('ticker').year.apply(list).to_string()); print(pd.DataFrame(cur).round(2).to_string())
