# 纳斯达克逃顶推荐组合事件研究（样本内，未做样本外，未计成本）
import yfinance as yf, pandas as pd, numpy as np, json
def rma(x,n): return x.ewm(alpha=1/n,adjust=False).mean()
def sma(x,n): return x.rolling(n).mean()
q=yf.download('QQQ',start='1999-01-01',auto_adjust=True,progress=False)
vx=yf.download('^VIX',start='1999-01-01',auto_adjust=True,progress=False)
q.columns=[c[0] if isinstance(c,tuple) else c for c in q.columns]; vx.columns=[c[0] if isinstance(c,tuple) else c for c in vx.columns]
q.to_csv('QQQ_daily.csv'); vx.to_csv('VIX_daily.csv')
o,h,l,c,v=[q[k] for k in ['Open','High','Low','Close','Volume']]; vix=vx['Close'].reindex(c.index).ffill()
d=c.diff(); rsi=100-100/(1+rma(d.clip(lower=0),14)/rma((-d).clip(lower=0),14))
pc=c.shift(); tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1); atr=rma(tr,14)
up=h.diff(); dn=-l.diff(); pdm=up.where((up>dn)&(up>0),0); mdm=dn.where((dn>up)&(dn>0),0)
pdi=100*rma(pdm,14)/atr; mdi=100*rma(mdm,14)/atr; adx=rma(100*(pdi-mdi).abs()/(pdi+mdi),14)
er=(c-c.shift(10)).abs()/c.diff().abs().rolling(10).sum()
clv=((c-l)-(h-c))/(h-l).replace(0,np.nan); cmf=(clv*v).rolling(20).sum()/v.rolling(20).sum()
pvt=(c.pct_change()*v).cumsum(); pvtd=(pvt-sma(pvt,20))/(sma(v,20)*np.sqrt(20))
bias=c/sma(c,20)-1; z=(c-sma(c,20))/c.rolling(20).std()
dh=c/h.rolling(252).max()-1
mdd=c.rolling(252).apply(lambda a:np.min(a/np.maximum.accumulate(a)-1),raw=True)
# ---- 规则草案（假设） ----
D1=(rsi.rolling(10).max()>70)&(rsi<rsi.rolling(10).max()-5)                 # 动量：近10日曾>70且已回落5点
D2=((adx>25)&(adx<adx.shift(5)))|((er<0.3)&(dh>-0.03))                       # 趋势强度衰减
D3=(vix>sma(vix,20)*1.15)|(atr/sma(atr,50)>1.2)                              # 波动扩张
D4=(dh>-0.03)&((cmf<0)|(pvtd<0))                                             # 近高点但量价走弱
D5=(bias>bias.expanding(252).quantile(0.95).shift(1))|(z>2)                  # 极端偏离（扩展窗口分位，无前视）
D6=(dh<-0.08)&(dh.shift(1)>=-0.08)                                           # 回撤：首次跌破距252日高点-8%
score=sum(x.astype(int) for x in [D1,D2,D3,D4,D5]).rolling(5).max()         # 近5日内同时满足的维度数
valid=mdd.notna()&adx.notna()
def events(sig,cool=20):
    idx=[];last=-10**9
    for i,(t,s) in enumerate(sig.items()):
        if s and i-last>cool: idx.append(t); last=i
    return idx
def fwd(n):
    r=c.shift(-n)/c-1
    m=pd.concat([c.shift(-k)/c-1 for k in range(1,n+1)],axis=1).min(axis=1).clip(upper=0)
    return r,m
out={}
F={n:fwd(n) for n in (20,60)}
def stats(dates,name):
    s={'事件数':len(dates)}
    for n in (20,60):
        r,m=F[n]; rr=r.reindex(dates).dropna(); mm=m.reindex(dates).dropna()
        s[f'{n}日前向收益均值']=round(rr.mean()*100,2); s[f'{n}日前向收益中位数']=round(rr.median()*100,2)
        s[f'{n}日收益<0占比']=round((rr<0).mean()*100,1); s[f'{n}日最大回撤均值']=round(mm.mean()*100,2)
        s[f'{n}日最大回撤≤-10%占比']=round((mm<=-0.10).mean()*100,1)
    out[name]=s
base=c.index[valid & F[60][0].notna()]
stats(list(base),'无条件基准(全部交易日)')
sigs={'S_top: 5维中≥3维(近5日)':(score>=3)&valid,'S_top4: 5维中≥4维':(score>=4)&valid,
 'S_reduce: D6回撤-8%且D3波动扩张':D6&D3&valid,'D6单独':D6&valid}
for k,nm in zip([D1,D2,D3,D4,D5],['D1动量','D2趋势衰减','D3波动扩张','D4量价背离','D5极端偏离']): sigs[nm+'单独']=k&valid
ev={}
for k,s in sigs.items():
    e=events(s.fillna(False)); ev[k]=[str(t.date()) for t in e]; stats(e,k)
df=pd.DataFrame(out).T; df.to_csv('results.csv'); print(df.to_string())
json.dump(ev,open('event_dates.json','w'),ensure_ascii=False,indent=1)
print('样本区间',c.index[0].date(),c.index[-1].date(),'有效起点',base[0].date(),'终点',base[-1].date())
