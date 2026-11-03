"""Apply Gemini's 5 production gates to C1-C5 (and P1/P2 for comparison). 5 bps/side, 2000-01-03..2026-10-29."""
import pickle
from p12 import P, stats, df, np, pd, returns, c, s200, N_
out=pickle.load(open('round2_out.pkl','rb')); V=(out['meta']['Vsr_ann']/np.sqrt(252))**2; NT=out['meta']['Ntot']
def dsr(st,N=NT):
    g=0.5772156649; sr0=np.sqrt(V)*((1-g)*N_.inv_cdf(1-1/N)+g*N_.inv_cdf(1-1/(N*np.e)))
    return N_.cdf((st['srd']-sr0)*np.sqrt(st['T']-1)/np.sqrt(1-st['skew']*st['srd']+(st['kurt']-1)/4*st['srd']**2))
FULL=('2000-01-03','2026-10-29')
def gate(name,R,nb_sh,overlay=False,full=FULL,bh=None):
    f=stats(df,R,*full,5); o=stats(df,R,'2022-01-01','2026-10-29',5)
    a=stats(df,R,'2000-01-03','2002-12-31',5); b8=stats(df,R,'2008-01-01','2008-12-31',5); g22=stats(df,R,'2022-01-01','2022-12-31',5)
    drop=max([(f['sharpe']-x)/abs(f['sharpe']) for x in nb_sh]) if nb_sh else np.nan; flip=any(np.sign(x)!=np.sign(f['sharpe']) for x in nb_sh)
    G=[('交易≥100',f['trades'],f['trades']>=100),('DSR≥0.95',dsr(f),dsr(f)>=0.95),('PF≥1.7',f['PF'],f['PF']>=1.7),
       ('全期Sharpe≥0.85',f['sharpe'],f['sharpe']>=0.85),('OOS Sharpe≥0.80',o['sharpe'],o['sharpe']>=0.80),
       ('Calmar≥%.2f'%(0.85 if overlay else 0.65),f['calmar'],f['calmar']>=(0.85 if overlay else 0.65)),
       ('MDD优于%d%%'%(-25 if overlay else -15),f['MDD'],f['MDD']>=(-0.25 if overlay else -0.15)),('回撤期≤18月',f['dd_days'],f['dd_days']<=548),
       ('胜率≥70%',f['win'],f['win']>=0.70),('盈亏比≥0.85',f['WL'],f['WL']>=0.85),
       ('±20%邻域降幅≤25%',drop,(drop<=0.25) and not flip),('2000-02收益≥0',a['tot'],a['tot']>=0 if full[0]<'2001' else None),
       ('2008 MDD优于-12%',b8['MDD'],b8['MDD']>=-0.12),('2022 Sharpe≥0.6',g22['sharpe'],(g22['sharpe']>=0.6) if g22['trades'] or overlay else False)]
    if bh is not None:
        B=stats(df,bh,*full,0); G.append(('同时胜B&H(CAGR/Sharpe/MDD)',f"{f['CAGR']:.3f}/{f['sharpe']:.2f}/{f['MDD']:.3f} vs {B['CAGR']:.3f}/{B['sharpe']:.2f}/{B['MDD']:.3f}",
              f['CAGR']>B['CAGR'] and f['sharpe']>B['sharpe'] and f['MDD']>B['MDD']))
    return name,G
from cands import C1,C2,C3,C4,C5,bh

BASE={'C1':dict(rsi_t=15,wmult=2.0,stop=0.06,bt=1.05,bull_maxd=5,bear_sma=10,bear_rsi=65),'C2':dict(rsi_t=15,tmf_t=-0.05,mo_t=-40,nd_t=25,maxd=6,stop=0.04),
      'C3':dict(bt=1.05,rsi_t=25,exs=10,maxd=8,stop=0.05,ibs_t=0.3,cont=0.92),'C4':dict(blen=21,ibs_t=0.15,exs=5,atr_t=1.15,trend=150,maxd=4),'C5':dict(rsi_t=15,wmult=2.0,maxd=5,stop=0.04,sat=0.5)}
FN={'C1':C1,'C2':C2,'C3':C3,'C4':C4,'C5':C5}; res=[]
B=bh()
for k,f in FN.items():
    nb=[x[2] for x in out[k]['nb']]; res.append(gate(k,f(**BASE[k]),nb,overlay=(k=='C5'),bh=B if k=='C5' else None))
# P1/P2 for comparison (P2 only from 2008 because VIX3M starts 2007-12-05)
import cands
def P1v(rt=15,ex=70,cost=5):
    from cands import sim,r2,s200,c
    return sim(df,lambda i:'x' if (not np.isnan(s200[i]) and c[i]>s200[i] and r2[i]<rt) else None,lambda i,s:r2[i]>ex,cost)
def P2v(rt=15,tt=1.0,sm=5,cost=5):
    from cands import sim,r2,c,ts_real; from ind import sma; t=ts_real.values; S=sma(df.close,sm).values
    return sim(df,lambda i:'x' if (not np.isnan(t[i]) and r2[i]<rt and t[i]<tt) else None,lambda i,s:c[i]>S[i],cost)
nb1=[stats(df,P1v(**kw),*FULL,5)['sharpe'] for kw in [dict(rt=12),dict(rt=18),dict(ex=56),dict(ex=84)]]
F8=('2008-01-02','2026-10-29')
nb2=[stats(df,P2v(**kw),*F8,5)['sharpe'] for kw in [dict(rt=12),dict(rt=18),dict(tt=0.95),dict(tt=1.05),dict(sm=4),dict(sm=6)]]
res.append(gate('P1',P1v(),nb1)); res.append(gate('P2(2008+)',P2v(),nb2,full=F8))
# overlay P2 base=sma200 (+0.5 satellite) 2008+
R2=P2v(); base=np.where(c>s200,1.0,0.0); t=base+0.5*R2['tgt']; r,w=returns(df,t,5); OV=dict(tr=R2['tr'],r=r,w=w,tgt=t,open=False,pend=None)
res.append(gate('P2叠加(2008+)',OV,[],overlay=True,full=F8,bh=B))
R1=P1v(); t=base+0.5*R1['tgt']; r,w=returns(df,t,5); OV1=dict(tr=R1['tr'],r=r,w=w,tgt=t,open=False,pend=None)
res.append(gate('P1叠加',OV1,[],overlay=True,bh=B))
rows=[]
for n,G in res:
    for g,v,ok in G: rows.append(dict(model=n,gate=g,value=v if isinstance(v,str) else round(float(v),3),pass_=('—' if ok is None else ('✅' if ok else '❌'))))
T=pd.DataFrame(rows); T.to_csv('gates.csv',index=False)
P_=T.pivot(index='gate',columns='model',values='pass_'); Vv=T.pivot(index='gate',columns='model',values='value')
order=[g for g,_,_ in res[0][1]]+['同时胜B&H(CAGR/Sharpe/MDD)']
pd.set_option('display.width',300); pd.set_option('display.max_columns',20)
print((Vv.astype(str)+' '+P_).reindex(order).to_string())
print('passes:',{n:sum(1 for _,_,ok in G if ok) for n,G in res},'of',{n:len(G) for n,G in res})
print('P1 nb',nb1,'P2 nb',nb2)
