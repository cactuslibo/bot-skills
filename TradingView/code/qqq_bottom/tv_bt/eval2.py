import itertools, json
from cands import *
from statistics import NormalDist
class norm:
    cdf=staticmethod(NormalDist().cdf); ppf=staticmethod(NormalDist().inv_cdf)
PER={'FULL':('2000-01-03','2026-10-29'),'IS':('2000-01-03','2021-12-31'),'OOS':('2022-01-01','2026-10-29'),'2016+':('2016-01-22','2026-10-29'),
     '2000-02':('2000-01-03','2002-12-31'),'2008':('2008-01-01','2008-12-31'),'2020':('2020-01-01','2020-12-31'),'2022':('2022-01-01','2022-12-31'),'2008+':('2008-01-02','2026-10-29')}
FN={'C1':C1,'C2':C2,'C3':C3,'C4':C4,'C5':C5}
BASE={'C1':dict(rsi_t=15,wmult=2.0,stop=0.06,bt=1.05,bull_maxd=5,bear_sma=10,bear_rsi=65),
      'C2':dict(rsi_t=15,tmf_t=-0.05,mo_t=-40,nd_t=25,maxd=6,stop=0.04),
      'C3':dict(bt=1.05,rsi_t=25,exs=10,maxd=8,stop=0.05,ibs_t=0.3,cont=0.92),
      'C4':dict(blen=21,ibs_t=0.15,exs=5,atr_t=1.15,trend=150,maxd=4),
      'C5':dict(rsi_t=15,wmult=2.0,maxd=5,stop=0.04,sat=0.5)}
GRID={'C1':dict(rsi_t=[10,12,15,18],wmult=[1.8,2.0,2.2],stop=[0.04,0.06,0.08]),
      'C2':dict(rsi_t=[10,15,20],tmf_t=[-0.03,-0.05,-0.08],mo_t=[-30,-40,-60]),
      'C3':dict(bt=[1.02,1.05,1.08],rsi_t=[20,25,30],exs=[8,10,12]),
      'C4':dict(blen=[14,21,28],ibs_t=[0.10,0.15,0.20],exs=[3,5,8]),'C5':{}}
NB={'C1':dict(rsi_t=[12,18],wmult=[1.6,2.4],stop=[0.048,0.072],bt=[1.04,1.06],bull_maxd=[4,6],bear_sma=[8,12],bear_rsi=[52,78]),
    'C2':dict(rsi_t=[12,18],tmf_t=[-0.04,-0.06],mo_t=[-32,-48],nd_t=[20,30],maxd=[5,7],stop=[0.032,0.048]),
    'C3':dict(bt=[1.04,1.06],rsi_t=[20,30],exs=[8,12],maxd=[6,10],stop=[0.04,0.06],ibs_t=[0.24,0.36],cont=[0.90,0.94]),
    'C4':dict(blen=[17,25],ibs_t=[0.12,0.18],exs=[4,6],atr_t=[1.12,1.18],trend=[120,180],maxd=[3,5]),
    'C5':dict(rsi_t=[12,18],wmult=[1.6,2.4],maxd=[4,6],stop=[0.032,0.048],sat=[0.4,0.6])}
def S(R,p,cost=5): return stats(df,R,*PER[p],cost_bps=cost)
out={}; allsr=[]; ntrials=0
for k,f in FN.items():
    b=BASE[k]; o={}
    R=f(**b); o['base']={p:S(R,p) for p in PER}
    o['cost']={cb:S(f(**b,cost=cb),'FULL',cb)['sharpe'] for cb in (0,2,5,10)}
    o['cost_oos']={cb:S(f(**b,cost=cb),'OOS',cb)['sharpe'] for cb in (0,2,5,10)}
    o['open']=R['open']; o['pend']=R['pend']; o['last_tgt']=float(R['tgt'][-1])
    o['trades_list']=[(str(df.index[s].date()),str(df.index[e].date()),round(x/p-1,4),br) for s,e,p,x,br in R['tr']]
    # neighbourhood
    nb=[]
    for pk,vals in NB[k].items():
        for v in vals:
            bb=dict(b); bb[pk]=v; RR=f(**bb); nb.append((pk,v,S(RR,'FULL')['sharpe'],S(RR,'OOS')['sharpe']))
    o['nb']=nb
    # grid + walk-forward
    g=GRID[k]; rows=[]; rets={}
    if g:
        for combo in itertools.product(*g.values()):
            bb=dict(b); bb.update(dict(zip(g.keys(),combo))); RR=f(**bb); key=json.dumps(dict(zip(g.keys(),combo)))
            rows.append(dict(key=key,FULL=S(RR,'FULL')['sharpe'],IS=S(RR,'IS')['sharpe'],OOS=S(RR,'OOS')['sharpe'],srd=S(RR,'FULL')['srd'],trades=S(RR,'FULL')['trades']))
            rets[key]=pd.Series(RR['r'],df.index)
        G=pd.DataFrame(rows); o['grid']=G; ntrials+=len(G); allsr+=list(G.srd.dropna())
        bi=G.loc[G.IS.idxmax()]; o['is_best']=bi.to_dict()
        wf=[]; R_=pd.DataFrame(rets)
        for y in range(2003,2027):
            tr_=R_.loc[str(y-3):str(y-1)]; sh=(tr_.mean()/tr_.std()).fillna(-9); best=sh.idxmax(); wf.append(R_.loc[str(y),best])
        wf=pd.concat(wf); eq=(1+wf).cumprod()
        o['wf']=dict(sharpe=wf.mean()/wf.std()*np.sqrt(252),CAGR=eq.iat[-1]**(252/len(wf))-1,MDD=(eq/eq.cummax()-1).min(),
                     oos_sharpe=wf.loc['2022':].mean()/wf.loc['2022':].std()*np.sqrt(252))
    ntrials+=len(nb)+1
    out[k]=o
# DSR (Bailey & Lopez de Prado 2014)
def dsr(st,N,Vsr):
    g=0.5772156649; sr0=np.sqrt(Vsr)*((1-g)*norm.ppf(1-1/N)+g*norm.ppf(1-1/(N*np.e)))
    sr=st['srd']; T=st['T']; z=(sr-sr0)*np.sqrt(T-1)/np.sqrt(1-st['skew']*sr+(st['kurt']-1)/4*sr**2); return norm.cdf(z),sr0*np.sqrt(252)
Vsr=np.var(allsr); Ntot=172+ntrials
for k in out: out[k]['dsr']=dsr(out[k]['base']['FULL'],Ntot,Vsr)
# extras
r3=C3(**BASE['C3']); hv=(df.vix>25).values
out['C3']['regime']={'VIX>25':float(r3['r'][hv].mean()/r3['r'][hv].std()*np.sqrt(252)),'VIX<=25':float(r3['r'][~hv].mean()/r3['r'][~hv].std()*np.sqrt(252)),
   'trades_hv':sum(hv[s-1] for s,_,_,_,_ in r3['tr']),'trades_lv':sum(not hv[s-1] for s,_,_,_,_ in r3['tr'])}
for k,kw in [('C1',BASE['C1']),('C3',BASE['C3'])]:
    RR=FN[k](**kw,proxy=False); out[k]['realonly']={p:S(RR,p) for p in ['2008','2008+','OOS']}
RR=C1(**BASE['C1'],lime=True); out['C1']['lime']={p:S(RR,p) for p in ['FULL','OOS','2008']}
# C4 stationary bootstrap of trade returns
rng=np.random.default_rng(0); tr4=np.array([x/p*(1-5e-4)**2-1 for s,e,p,x,_ in C4(**BASE['C4'])['tr']]); n=len(tr4); tots=[]
for _ in range(1000):
    idx=[];i=rng.integers(n)
    while len(idx)<n:
        idx.append(i); i=(i+1)%n if rng.random()>0.2 else rng.integers(n)
    tots.append(np.prod(1+tr4[idx])-1)
out['C4']['boot']=dict(VaR95=float(np.percentile(tr4,5)),ES95=float(tr4[tr4<=np.percentile(tr4,5)].mean()),tot_p5=float(np.percentile(tots,5)),tot_p50=float(np.median(tots)),p_loss=float(np.mean(np.array(tots)<0)))
B=bh(); out['BH']={p:S(B,p,0) for p in PER}
out['meta']=dict(Ntot=Ntot,Vsr_ann=float(np.sqrt(Vsr)*np.sqrt(252)),new_trials=ntrials)
import pickle; pickle.dump(out,open('round2_out.pkl','wb'))
print(json.dumps(out['meta']))
for k in FN:
    o=out[k]; f=o['base']['FULL']
    print(k,{p:(o['base'][p]['trades'],round(o['base'][p]['sharpe'],2),round(o['base'][p]['MDD'],3),round(o['base'][p]['tot'],3),round(o['base'][p]['CAGR'],3)) for p in PER})
    print('  win',round(f['win'],3),'PF',round(f['PF'],2),'WL',round(f['WL'],2),'calmar',round(f['calmar'],2),'ddd',f['dd_days'],'exp',round(f['exposure'],3),'dsr',[round(x,3) for x in o['dsr']])
    print('  cost',{a:round(b,2) for a,b in o['cost'].items()},'oos',{a:round(b,2) for a,b in o['cost_oos'].items()})
    print('  nb',[(a,b,round(c,2),round(d,2)) for a,b,c,d in o['nb']])
    if 'grid' in o: print('  grid FULL min/med/max',o['grid'].FULL.min().round(2),o['grid'].FULL.median().round(2),o['grid'].FULL.max().round(2),'IS-best',o['is_best']['key'],round(o['is_best']['IS'],2),round(o['is_best']['OOS'],2),'WF',{a:round(b,3) for a,b in o['wf'].items()})
    print('  open',o['open'],o['pend'],o['last_tgt'],'last trades',o['trades_list'][-2:])
for k in ['C1','C3']: print(k,'realonly',{p:(v['trades'],round(v['sharpe'],2),round(v['MDD'],3),round(v['tot'],3)) for p,v in out[k]['realonly'].items()})
print('C1 lime',{p:(v['trades'],round(v['sharpe'],2),round(v['MDD'],3)) for p,v in out['C1']['lime'].items()})
print('C3 regime',out['C3']['regime']); print('C4 boot',out['C4']['boot'])
print('BH',{p:(round(v['sharpe'],2),round(v['MDD'],3),round(v['CAGR'],3),round(v['tot'],3)) for p,v in out['BH'].items()})
