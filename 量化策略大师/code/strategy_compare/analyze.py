import pandas as pd, numpy as np, pickle, json
from scipy.stats import norm, skew, kurtosis
from framework import load, port_returns, register_daily, MK
import framework as F
register_daily()
import strategies_daily as S
df=pd.read_csv('results_by_year.csv'); D=pickle.load(open('daily_returns.pkl','rb'))
h=df[df.year!=2026]
nd=h[h.ticker=='NDX'].pivot_table(index='year',columns='strategy',values=['ret','mdd','sharpe']); bh=h[h.ticker=='NDX'].groupby('year')[['bh_ret','bh_mdd','bh_sharpe']].first()
print((nd['ret']*100).round(1).join((bh.bh_ret*100).round(1)).to_string()); print((nd['mdd']*100).round(1).join((bh.bh_mdd*100).round(1)).to_string()); print(nd['sharpe'].round(2).join(bh.bh_sharpe.round(2)).to_string())
h=h.assign(kind=np.where((h.bh_mdd<=-0.20)|(h.bh_ret<0),'急跌/下跌年','慢牛/上涨年'))
k=h.groupby(['kind','strategy']).apply(lambda s:pd.Series(dict(n=len(s),excess=(s.ret-s.bh_ret).mean(),mdd_gain=(s.mdd-s.bh_mdd).mean(),win=(s.ret>s.bh_ret).mean())))
print(k.round(3).to_string()); print(h[h.ticker=='NDX'].groupby('year').kind.first().to_string())
rng=np.random.default_rng(0); sig={}
for scope,sel in [('NDX',lambda t:t=='NDX'),('ETF全部',lambda t:t!='NDX')]:
  for s in sorted({k_[2] for k_ in D}):
    keys=[k_ for k_ in D if k_[2]==s and sel(k_[0]) and k_[1]!=2026]
    if not keys: continue
    blocks=[(D[x].s-D[x].b).values for x in keys]; mb=np.array([b.mean() for b in blocks]); L=np.array([len(b) for b in blocks])
    obs=(mb*L).sum()/L.sum()*252; bs=[]
    for _ in range(4000):
        i=rng.integers(0,len(blocks),len(blocks)); bs.append((mb[i]*L[i]).sum()/L[i].sum()*252)
    bs=np.array(bs)
    R=pd.concat([D[x].s-D[x].rf for x in keys]); B=pd.concat([D[x].b-D[x].rf for x in keys])
    sr=R.mean()/R.std(); sb=B.mean()/B.std(); T=len(R)
    psr=norm.cdf((sr-sb)*np.sqrt(T-1)/np.sqrt(1-skew(R)*sr+(kurtosis(R,fisher=False)-1)/4*sr**2))
    sig[f'{scope}|{s}']=dict(blocks=len(keys),ann_excess=obs,ci_lo=np.percentile(bs,2.5),ci_hi=np.percentile(bs,97.5),p_le0=(bs<=0).mean(),SR_ann=sr*np.sqrt(252),SR_bh=sb*np.sqrt(252),PSR_vs_bh=psr)
sig=pd.DataFrame(sig).T; print(sig.round(3).to_string())
def full(P,Mm,f,a,b,zero=False):
    old=F.COST
    if zero: F.COST=0; Mm=dict(Mm,rf=Mm['rf']*0)
    R,_=port_returns(P,Mm,f(P,Mm)[0]); F.COST=old
    R=R[(R.index>=a)&(R.index<=b)]; eq=(1+R).cumprod(); y=(R.index[-1]-R.index[0]).days/365.25
    return dict(cagr=eq.iloc[-1]**(1/y)-1,mdd=(eq/eq.cummax()-1).min(),sharpe=R.mean()/R.std()*np.sqrt(252))
q=pd.read_csv('/workspace/ndx_escape/QQQ.csv',index_col=0,parse_dates=True); q.columns=[c.lower() for c in q.columns]; qq=q[['open','high','low','close','volume']]
mqq={k_:v.reindex(qq.index.union(v.index)).ffill().reindex(qq.index) for k_,v in MK.items()}; mqq['vxn']=mqq['vxn'].combine_first(mqq['vix']); mqq['rf']=(mqq['irx']/100/252).fillna(0)
pxn,mn=load('NDX'); rec={}
for lab,(f,a,b) in {'园园AI_3x':(S.yuanyuan_ai_3x,'2010-02-11','2026-10-28'),'园园AI_1x':(S.yuanyuan_ai_1x,'2010-02-11','2026-10-28'),'P2':(S.p2,'2008-01-02','2026-10-29')}.items():
    for nm,(P,Mm) in {'QQQ':(qq,mqq),'NDX':(pxn,mn)}.items():
        rec[f'{lab}|{nm}|本框架']=full(P,Mm,f,a,b); rec[f'{lab}|{nm}|0成本0现金']=full(P,Mm,f,a,b,True)
rec=pd.DataFrame(rec).T; print(rec.round(4).to_string())
json.dump(dict(sig=sig.to_dict('index'),recon=rec.to_dict('index')),open('analysis.json','w'),ensure_ascii=False,indent=1,default=float)
sig.to_csv('significance.csv'); rec.to_csv('reconciliation.csv'); k.to_csv('crash_vs_bull.csv')
