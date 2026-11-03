from hyb2 import *
prev=pickle.load(open('round1_h.pkl','rb')); Vsr=prev['Vsr']; NT=prev['NT']+14
def dsr(s):
    g=0.5772156649; sr0=np.sqrt(Vsr)*((1-g)*ND.inv_cdf(1-1/NT)+g*ND.inv_cdf(1-1/(NT*np.e)))
    return ND.cdf((s['srd']-sr0)*np.sqrt(s['T']-1)/np.sqrt(max(1e-9,1-s['skew']*s['srd']+(s['kurt']-1)/4*s['srd']**2)))
A,B='2015-01-02','2026-10-30'
def full(kw,cost=2.5):
    R=sim(cost=cost,**kw); s=stats(q,R,A,B,cost); s['IS']=stats(q,R,A,'2021-12-31',cost)['sharpe']; s['OOS']=stats(q,R,'2022-01-01',B,cost)['sharpe']
    s['dur']=np.mean([e-st for st,e,*_ in R['tr']]); s['dsr']=dsr(s); s['R']=R; return s
base={cb:full({},cb) for cb in (0,2,2.5,4)}
b=base[2.5]
print(f"P2 baseline: n={b['trades']} win={b['win']:.3f} avg={b['avg_net_bp']:.1f}bp SR={b['sharpe']:.3f} MDD={b['MDD']:.3f} CAGR={b['CAGR']:.3f} IS={b['IS']:.2f} OOS={b['OOS']:.2f} dur={b['dur']:.1f} bars tot={b['tot']:.3f} exp={b['exposure']:.3f} dsr={b['dsr']:.3f}")
rows=[]
def show(lab,kw,crit):
    s={cb:full(kw,cb) for cb in (0,2,2.5,4)}; x=s[2.5]
    d=dict(lab=lab,n=x['trades'],win=x['win'],avg=x['avg_net_bp'],SR=x['sharpe'],dSR=x['sharpe']-b['sharpe'],MDD=x['MDD'],CAGR=x['CAGR'],IS=x['IS'],OOS=x['OOS'],
           dur=x['dur'],tot=x['tot'],exp=x['exposure'],dsr=x['dsr'],dSR_costs={cb:round(s[cb]['sharpe']-base[cb]['sharpe'],3) for cb in (0,2,4)})
    d['gates']=crit(d,s); rows.append(d)
    print(f"{lab:38s} n={d['n']} win={d['win']:.3f} avg={d['avg']:.1f} SR={d['SR']:.3f} dSR={d['dSR']:+.3f} MDD={d['MDD']:.3f} IS={d['IS']:.2f} OOS={d['OOS']:.2f} dur={d['dur']:.1f} tot={d['tot']:.3f} dsr={d['dsr']:.3f} dSRcost={d['dSR_costs']}")
    print('     ',[(g,'✅' if ok else '❌') for g,ok in d['gates']])
c1=lambda d,s:[('均笔+8bp',d['avg']-b['avg_net_bp']>=8),('ΔSR≥+0.10',d['dSR']>=0.10),('N≥150',d['n']>=150)]
c2=lambda d,s:[('MDD改善≥2pp',d['MDD']-b['MDD']>=0.02),('胜率+3pp',d['win']-b['win']>=0.03),('ΔSR≥0.08(0/2/4bp)',all(v>=0.08 for v in d['dSR_costs'].values()))]
c3=lambda d,s:[('持仓-15%且净利降≤5%',d['dur']<=0.85*b['dur'] and d['tot']>=0.95*b['tot']),('ΔSR≥+0.10',d['dSR']>=0.10),('胜率≥70%',d['win']>=0.70)]
print('--- H1 optimistic (fill=min(open,L) when low<=L)')
for X,fb in itertools.product([0.002,0.004,0.006],[4,6]): show(f'H1 opt X={X*100:.1f}% fb=bar{fb}',dict(entry_mode='h1',X=X,fb=fb),c1)
print('--- H1 conservative')
for cb_ in (2,5):
    for X,fb in itertools.product([0.002,0.004,0.006],[4,6]): show(f'H1 cons{cb_}bp X={X*100:.1f}% fb=bar{fb}',dict(entry_mode='h1',X=X,fb=fb,cons_bp=cb_),c1)
for X in [0.002,0.004,0.006]: show(f'H1 cons5bp X={X*100:.1f}% 未成交放弃',dict(entry_mode='h1',X=X,fb=6,cons_bp=5,unfilled='skip'),c1)
print('--- H2')
for t,fbh in itertools.product(['A','B'],[6,7]): show(f'H2 trig={t} fallback=bar{fbh}open',dict(entry_mode='h2',trig=t,fbh=fbh),c2)
print('--- H3')
for Y,hm in itertools.product([80,90],[3,7]): show(f'H3 Y={Y} Hmin={hm}',dict(Y=Y,hmin=hm),c3)
# fill stats for H1
for X in [0.002,0.004,0.006]:
    for cb_ in (None,2,5):
        R=sim(entry_mode='h1',X=X,fb=6,cons_bp=cb_); fb=sum(1 for t in R['tr'] if bar[t[0]]==6 and t[2]==o[t[0]]); print('H1 fill X',X,'cons',cb_,'trades',len(R['tr']),'fallback fills',fb)
# state
R=sim(); print('P2 state: open',R['open'],'armed',R['arm'],'last daily RSI2',round(dr2.iat[-1],1),'ratio',round(dratio.iat[-1],3),'last trade',q.index[R['tr'][-1][0]],q.index[R['tr'][-1][1]])
pickle.dump(dict(rows=rows,base={k:{kk:vv for kk,vv in v.items() if kk!='R'} for k,v in base.items()},NT=NT),open('round2_h.pkl','wb'))
print('NT',NT)
