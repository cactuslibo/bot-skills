import sys; sys.path.insert(0,'/workspace/strategy_compare')
import pandas as pd, numpy as np, yfinance as yf, json
import framework as F; F.register_daily()
from framework import MK, sma, rma, port_returns
d=yf.download('UPWK',start='2018-01-01',auto_adjust=True,progress=False); d.columns=[c[0].lower() for c in d.columns]
d=d[['open','high','low','close','volume']].dropna(subset=['close']); d=d[d.index<='2026-11-02']  # 剔除11-03盘中未收盘K线
d.to_csv('upwk/UPWK.csv')
m={k:v.reindex(d.index.union(v.index)).ffill().reindex(d.index) for k,v in MK.items()}
m['vxn']=m['vxn'].combine_first(m['vix']); m['rf']=(m['irx']/100/252).fillna(0)
c=d.close; print('mkt last',{k:str(v.dropna().index[-1].date()) for k,v in MK.items()})
dc=c.diff(); rsi=100-100/(1+rma(dc.clip(lower=0),14)/rma((-dc).clip(lower=0),14))
bg=dict(date=str(c.index[-1].date()),close=c.iloc[-1],dd52=c.iloc[-1]/d.high.iloc[-252:].max()-1,sma50=sma(c,50).iloc[-1],sma200=sma(c,200).iloc[-1],rsi14=rsi.iloc[-1],sma20=sma(c,20).iloc[-1],sma5=sma(c,5).iloc[-1])
print(bg)
res={}; ret=c.pct_change().fillna(0)
def st(r,rf):
    eq=(1+r).cumprod(); y=len(r)/252; ex=r-rf
    return dict(cagr=eq.iloc[-1]**(1/y)-1,mdd=(eq/eq.cummax()-1).min(),sharpe=ex.mean()/ex.std()*np.sqrt(252))
start=c.index[200]  # 预热200日后起算，统一区间
for k in ['v1','v2','MyRSI','园园1x','P2']:
    out=F.STRATEGIES[k](d,m); w=out[0]; sc=out[1]
    R,T=port_returns(d,m,w); mk=R.index>=start
    s=st(R[mk],m['rf'][mk]); b=st(ret[mk],m['rf'][mk])
    ch=w[w.diff().fillna(0)!=0].tail(4)
    chg=[dict(date=str(i.date()),frm=float(w.shift(1)[i]),to=float(w[i]),price=float(c[i])) for i in ch.index]
    a,bp=w.iloc[-1],w.iloc[-2]; state='买入' if a>bp else '卖出' if a<bp else ('持仓' if a>0 else '空仓')
    res[k]=dict(pos=float(a),state=state,changes=chg,score=None if sc is None else float(sc.iloc[-1]),bt=s,bh=b,avgpos=float(T[mk].mean()),ntrade=int((w[mk].diff().abs()>0).sum()))
    print(k,res[k])
print('区间',start.date(),c.index[-1].date())
# 诊断细节
s200=sma(c,200); sd=c.rolling(21).std(ddof=0); boo=100*(c+2*sd-c.rolling(21).mean())/(4*sd); g,r=boo.ewm(span=12,adjust=False).mean(),boo.ewm(span=120,adjust=False).mean()
print('MyRSI G,R',g.iloc[-3:].round(2).tolist(),r.iloc[-3:].round(2).tolist(),'s200',s200.iloc[-1])
d2=c.diff(); au=d2.clip(lower=0).ewm(alpha=.5,adjust=False).mean(); ad=(-d2.clip(upper=0)).ewm(alpha=.5,adjust=False).mean(); rsi2=100-100/(1+au/ad)
from strategies_daily import VIX3M, siji_states
print('P2 rsi2',rsi2.iloc[-3:].round(1).tolist(),'vix/vix3m',(m['vix']/VIX3M.reindex(c.index).ffill()).iloc[-1])
sts,_=siji_states(d); print('siji states',sts.iloc[-5:].tolist(),'ATH dd',c.iloc[-1]/max(d.high.iloc[:252].max(),c.max())-1,'ma20',sma(c,20).iloc[-1],'pma20',sma(c,20).iloc[-2])
sc,_=F._score(d,m,'vix'); print('score tail',sc.iloc[-5:].round(1).tolist())
json.dump(dict(bg=bg,res=res),open('upwk/result.json','w'),ensure_ascii=False,indent=1,default=float)
