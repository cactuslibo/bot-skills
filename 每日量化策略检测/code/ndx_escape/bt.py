import pandas as pd, numpy as np, json, itertools, hashlib
from scipy.stats import norm, skew, kurtosis
L=lambda t: pd.read_csv(t+'.csv',index_col=0,parse_dates=True)
n=L('NDX'); c=n.Close; h=n.High; l=n.Low
vix=L('VIX').Close.reindex(c.index).ffill()
rf=(L('IRX').Close.reindex(c.index).ffill()/100/252).fillna(0)
hyg=L('HYG').Close.reindex(c.index); lqd=L('LQD').Close.reindex(c.index)
rsp=L('RSP').Close.reindex(c.index); qqq=L('QQQ').Close.reindex(c.index)
rma=lambda x,k:x.ewm(alpha=1/k,adjust=False).mean(); sma=lambda x,k:x.rolling(k).mean()
ret=c.pct_change().fillna(0)
s50,s200=sma(c,50),sma(c,200)
# D1 趋势(35): 价<SMA200 =1；价<SMA50且SMA50 5日下降 =0.5
D1=np.where(c<s200,1.0,np.where((c<s50)&(s50<s50.shift(5)),0.5,0.0))
# D2 波动(25): VIX/其50日均值>1.25 或 20日实现波动在过去252日分位>0.8 （VIX缺失时只用后者）
rv=ret.rolling(20).std()*np.sqrt(252); rvp=rv.rolling(252).rank(pct=True)
D2=(((vix/sma(vix,50))>1.25)|(rvp>0.8)).astype(float)*0.5+(rvp>0.9).astype(float)*0.5
# D3 动量顶背离(15): 近10日内创63日新高，但RSI14或MACD柱低于前一高点(前63日内)时的值
d=c.diff(); rsi=100-100/(1+rma(d.clip(lower=0),14)/rma((-d).clip(lower=0),14))
macd=c.ewm(span=12).mean()-c.ewm(span=26).mean(); hist=macd-macd.ewm(span=9).mean()
newhi=c>=c.rolling(63).max()
prev_rsi=rsi.shift(10).rolling(53).max(); prev_h=hist.shift(10).rolling(53).max()
div=newhi&((rsi<prev_rsi-5)|(hist<prev_h*0.5))
D3=div.rolling(10).max().fillna(0)
# D4 过度偏离(10): 价/SMA200-1 高于扩展窗口95分位
ext=c/s200-1; D4=(ext>ext.expanding(500).quantile(0.95).shift(1)).astype(float)
# D5 信用/宽度(15, 2007+): HYG/LQD<其50日均线 ；RSP/QQQ 20日变化<-3%(?) -> 用 HYG/LQD 0.6 + RSP/QQQ 新20日高(领涨收窄反向) 不用；仅信用
cr=hyg/lqd; D5=(cr<sma(cr,50)).astype(float).where(cr.notna())
W={'D1':35,'D2':25,'D3':15,'D4':10,'D5':15}
comp=pd.DataFrame({'D1':D1,'D2':D2,'D3':D3,'D4':D4,'D5':D5},index=c.index)
def score_fn():
    num=sum(comp[k].fillna(0)*W[k] for k in W); den=sum(comp[k].notna()*W[k] for k in W)
    return 100*num/den
score=score_fn()
def position(lo,hi,band=10):
    # 三档：<lo满仓1.0；lo..hi半仓0.5；>=hi空仓0。再入场：分数回落到阈值-band 以下且收盘>SMA20才上调一档（防来回打脸）；
    # 快速再入场：收盘重新站上SMA50且VIX<其20日均值，则至少回到0.5；任何时候价格创63日新高直接满仓（防卖飞）
    s20=sma(c,20); w=1.0; out=[]
    vx20=sma(vix,20)
    for i in range(len(c)):
        sc=score.iloc[i]; tgt=1.0 if sc<lo else (0.5 if sc<hi else 0.0)
        if tgt<w: w=tgt
        elif tgt>w:
            thr=lo if w==0.5 else hi
            if sc<thr-band and c.iloc[i]>s20.iloc[i]: w=min(1.0,w+0.5)
        if w<1 and c.iloc[i]>s50.iloc[i] and (np.isnan(vx20.iloc[i]) or vix.iloc[i]<vx20.iloc[i]): w=max(w,0.5)
        if newhi.iloc[i]: w=1.0
        out.append(w)
    return pd.Series(out,index=c.index)
def voltarget(tv=0.20): return (tv/rv).clip(0,1).fillna(1)
COST=0.0005
def run(w,yr):
    m=c.index.year==yr; ws=w.shift(1).fillna(1.0)[m]   # 次日执行
    turn=ws.diff().abs(); turn.iloc[0]=abs(ws.iloc[0]-1.0)   # 年初从满仓开始
    r=ws*ret[m]+(1-ws)*rf[m]-turn*COST
    return r,ws
def stats(r):
    eq=(1+r).cumprod(); dd=(eq/eq.cummax()-1).min()
    return dict(ret=eq.iloc[-1]-1,mdd=dd,sharpe=(r.mean()/r.std()*np.sqrt(252)) if r.std()>0 else 0)
def sellfly(ws,yr):
    # 卖飞：一次减仓执行日后20个交易日NDX收盘高于执行前一日收盘
    idx=ws.index; cnt=0; cuts=0
    for i in range(1,len(ws)):
        if ws.iloc[i]<ws.iloc[i-1]:
            cuts+=1; p0=c.loc[idx[i-1]]; j=c.index.get_loc(idx[i])+20
            if j<len(c) and c.iloc[j]>p0: cnt+=1
    return cuts,cnt
TRAIN=[y for y in list(range(1990,2015)) if y not in (1999,2003,2004,2005,2006,2007)]
grid=list(itertools.product([30,40,50],[60,70,80]))
trials={}
for lo,hi in grid:
    w=position(lo,hi); r=pd.concat([run(w,y)[0] for y in TRAIN]); trials[f'{lo}/{hi}']=r
for tv in (0.15,0.20,0.25):
    w=voltarget(tv); trials[f'VT{tv}']=pd.concat([run(w,y)[0] for y in TRAIN])
bh=pd.concat([ret[c.index.year==y] for y in TRAIN])
tr=pd.DataFrame({k:{**stats(v),'ann':(1+v).prod()**(252/len(v))-1} for k,v in trials.items()}).T
tr.loc['B&H']=[*stats(bh).values(),(1+bh).prod()**(252/len(bh))-1]
print(tr.round(3)); N=len(trials)
best=tr.drop(['B&H']).filter(like='/',axis=0).sharpe.idxmax(); print('best',best,'N',N)
lo,hi=map(int,best.split('/'))
W_best=position(lo,hi); VT=voltarget(0.20)
TEST=[2018,1999,2005,2004,2006,2025,2007,2003,2021,2026]
rows=[];allr=[]
for y in TEST:
    r,ws=run(W_best,y); rv_,_=run(VT,y); b=ret[c.index.year==y]
    s=stats(r); sb=stats(b); sv=stats(rv_); cuts,fly=sellfly(ws,y)
    trades=int((ws.diff().abs()>0).sum())
    rows.append(dict(year=y,S_ret=s['ret'],BH_ret=sb['ret'],S_mdd=s['mdd'],BH_mdd=sb['mdd'],S_sh=s['sharpe'],BH_sh=sb['sharpe'],VT_ret=sv['ret'],VT_mdd=sv['mdd'],trades=trades,cuts=cuts,sellfly=fly,avg_pos=ws.mean()))
    if y!=2026: allr.append(r)
df=pd.DataFrame(rows); print(df.round(3).to_string())
# DSR on test (excl 2026) daily returns
R=pd.concat(allr); sr=R.mean()/R.std(); T=len(R)
srs=np.array([v.mean()/v.std() for v in trials.values()]); var=srs.var(ddof=1); g=0.5772
sr0=np.sqrt(var)*((1-g)*norm.ppf(1-1/N)+g*norm.ppf(1-1/(N*np.e)))
dsr=norm.cdf((sr-sr0)*np.sqrt(T-1)/np.sqrt(1-skew(R)*sr+(kurtosis(R,fisher=False)-1)/4*sr**2))
Rb=pd.concat([ret[c.index.year==y] for y in TEST if y!=2026])
psr_vs_bh=norm.cdf((sr-Rb.mean()/Rb.std())*np.sqrt(T-1)/np.sqrt(1-skew(R)*sr+(kurtosis(R,fisher=False)-1)/4*sr**2))
print('DSR',dsr,'SR0',sr0,'sr',sr,'PSR vs BH SR',psr_vs_bh)
last=c.index[-1]
cur=dict(date=str(last.date()),close=float(c.iloc[-1]),score=float(score.iloc[-1]),**{k:float(comp[k].iloc[-1]) for k in W},pos=float(W_best.iloc[-1]),vt=float(VT.iloc[-1]),vix=float(vix.iloc[-1]),sma50=float(s50.iloc[-1]),sma200=float(s200.iloc[-1]),rsi=float(rsi.iloc[-1]),rv20=float(rv.iloc[-1]))
print(cur); print(score.tail(10).round(1).to_string())
# 敏感性: 所有网格在测试年(不含2026)的超额
sens={k:None for k in trials}
for lo2,hi2 in grid:
    w=position(lo2,hi2); ex=[stats(run(w,y)[0])['ret']-stats(ret[c.index.year==y])['ret'] for y in TEST if y!=2026]
    sens[f'{lo2}/{hi2}']=(np.mean(ex),sum(e>0 for e in ex))
print(sens)
json.dump(dict(train=tr.round(4).to_dict(),best=best,N=N,test=df.to_dict('records'),dsr=dsr,sr0=sr0,sr=sr,psr_vs_bh=psr_vs_bh,cur=cur,sens=sens,sha=hashlib.sha256(open(__file__,'rb').read()).hexdigest()),open('out.json','w'),default=float,indent=1)
