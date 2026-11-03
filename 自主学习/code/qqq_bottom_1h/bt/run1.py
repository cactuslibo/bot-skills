from models import *
PER={'FULL':('2015-01-02','2026-10-30'),'IS':('2015-01-02','2021-12-31'),'OOS':('2022-01-01','2026-10-30')}
VIXM={'M4'}
def per(k,p):
    a,b=PER[p]
    if k in VIXM and a<'2020-01-02': a='2020-01-02'
    return a,b
S=lambda cb=2.5: Sim(q,cb)
out={}; allsr=[]; ntr=0
def evaluate(k,f,base,grid,select_is=False):
    global ntr
    rows=[]
    for combo in itertools.product(*grid.values()):
        kw=dict(base); kw.update(dict(zip(grid.keys(),combo))); R=S().run(**f(**kw)); ntr+=1
        st={p:stats(q,R,*per(k,p)) for p in PER}; rows.append((kw,st)); allsr.append(st['FULL']['srd'])
    if select_is: base=max(rows,key=lambda x: (x[1]['IS']['sharpe'] if x[1]['IS']['trades']>=30 else -9))[0]
    else: ntr+=1
    R=S().run(**f(**base)); st={p:stats(q,R,*per(k,p)) for p in PER}
    cost={cb:stats(q,S(cb).run(**f(**base)),*per(k,'FULL'),cb)['sharpe'] for cb in (0,2,2.5,4)}
    cost_oos={cb:stats(q,S(cb).run(**f(**base)),*per(k,'OOS'),cb)['sharpe'] for cb in (0,2,4)}
    gs=[x[1]['FULL']['sharpe'] for x in rows]
    stab=(min(gs)/max(gs)) if max(gs)>0 else np.nan
    # state
    i=N-1; e=f(**base)['entry']
    out[k]=dict(base=base,st=st,cost=cost,cost_oos=cost_oos,grid=[(json.dumps({a:str(b) for a,b in kw.items()}),s['FULL']['sharpe'],s['IS']['sharpe'],s['OOS']['sharpe']) for kw,s in rows],
                stab=stab,open=R['open'],pend=R['pend'],sig_last=bool(e(i)),last_trade=(str(q.index[R['tr'][-1][0]]),str(q.index[R['tr'][-1][1]])) if R['tr'] else None)
for k,f in FN.items(): evaluate(k,f,BASE[k],GRID[k])
for k,(f,g) in OWN.items(): evaluate(k,f,{},g,select_is=True)
NT=441+ntr; Vsr=np.nanvar(allsr)
def dsr(s):
    g=0.5772156649; sr0=np.sqrt(Vsr)*((1-g)*ND.inv_cdf(1-1/NT)+g*ND.inv_cdf(1-1/(NT*np.e)))
    return ND.cdf((s['srd']-sr0)*np.sqrt(s['T']-1)/np.sqrt(max(1e-9,1-s['skew']*s['srd']+(s['kurt']-1)/4*s['srd']**2)))
for k,ob in out.items():
    f=ob['st']['FULL']; g0=stats(q,S(0).run(**(FN.get(k) or OWN[k][0])(**ob['base'])),*per(k,'FULL'),0)
    ob['avg0']=g0['avg_net_bp']; ob['dsr']=dsr(f)
    ob['gates']=[('N≥300',f['trades'],f['trades']>=300),('DSR≥0.90',ob['dsr'],ob['dsr']>=0.9),('PF≥1.40',f['PF'],f['PF']>=1.4),('均笔(0bp)≥12bp',ob['avg0'],ob['avg0']>=12),
        ('MDD优于-10%',f['MDD'],f['MDD']>=-0.10),('OOS Sharpe≥1.0',ob['st']['OOS']['sharpe'],ob['st']['OOS']['sharpe']>=1.0),
        ('隔夜方差占比≤40%',f['overnight_share'],f['overnight_share']<=0.4),('稳定指数≥0.75',ob['stab'],ob['stab']>=0.75 if ob['stab']==ob['stab'] else False)]
# benchmarks
BH=dict(r=np.r_[0,(c[1:]/c[:-1]-1)],gap=np.r_[0,np.where(first[1:],o[1:]/c[:-1]-1,0)],intr=np.r_[0,np.where(first[1:],c[1:]/o[1:]-1,c[1:]/c[:-1]-1)],w=np.ones(N),tr=[],open=True,pend=None,held=np.ones(N,bool))
PV=Sim(q).run(entry=lambda i: bar[i]==1, exitf=lambda i,st: False, moc=lambda i,st: last[i])
bench={'B&H':{p:stats(q,BH,*PER[p],0) for p in PER},'10:30买16:00卖':{p:stats(q,PV,*PER[p]) for p in PER}}
# daily P2 on daily bars built from adjusted hourly RTH; VIX/VIX3M daily same-day close; 2.5bp/side
dd=pd.DataFrame({'open':dopen,'close':dclose}); dd=dd[dd.index<=pd.Timestamp('2026-10-29')]
F='/workspace/qqq_bottom/data/full/'
dv=pd.read_csv(F+'VIX.csv',parse_dates=['time']).set_index('time')['close']; dm=pd.read_csv(F+'VIX3M.csv',parse_dates=['time']).set_index('time')['close']
dd['ratio']=(dv/dm).reindex(dd.index); R2d=rsi(dd.close,2).values; S5d=sma(dd.close,5).values; dO=dd.open.values; dC=dd.close.values
pos=0; pend=None; rr=np.zeros(len(dd)); trs=[]; cb=2.5e-4
for i in range(len(dd)):
    hld=pos
    if pend=='in': pos=1; ei=i; pend=None
    elif pend=='out': pos=0; trs.append(dO[i]/dO[ei]-1); pend=None
    rr[i]=(hld*(dO[i]/dC[i-1]-1) if i else 0)+pos*(dC[i]/dO[i]-1)-abs(pos-hld)*cb
    if pos and dC[i]>S5d[i]: pend='out'
    elif not pos and R2d[i]<15 and dd.ratio.values[i]<1: pend='in'
P2s={}
for p,(a,b) in PER.items():
    m=(dd.index>=a)&(dd.index<=b); x=pd.Series(rr[m]); eq=(1+x).cumprod(); yrs=m.sum()/252
    P2s[p]=dict(sharpe_daily=x.mean()/x.std()*np.sqrt(252),CAGR=eq.iat[-1]**(1/yrs)-1,MDD=(eq/eq.cummax()-1).min(),exposure=None)
P2s['trades']=len(trs); P2s['win']=np.mean(np.array(trs)>0); P2s['state']=dict(pos=pos,pend=pend,rsi2=R2d[-1],ratio=dd.ratio.values[-1])
pickle.dump(dict(out=out,bench=bench,P2=P2s,NT=NT,Vsr=Vsr,ntr=ntr),open('round1_h.pkl','wb'))
print('NT',NT,'new trials',ntr)
for k,ob in out.items():
    s=ob['st']
    print(f"\n{k} base={ob['base']} FULL n={s['FULL']['trades']} win={s['FULL']['win']:.2f} CAGR={s['FULL']['CAGR']:.3f} SR={s['FULL']['sharpe']:.2f} (obs {s['FULL']['sharpe_obs']:.2f}, daily {s['FULL']['sharpe_daily']:.2f}) MDD={s['FULL']['MDD']:.3f} exp={s['FULL']['exposure']:.3f} IS={s['IS']['sharpe']:.2f}({s['IS']['trades']}) OOS={s['OOS']['sharpe']:.2f}({s['OOS']['trades']}) avg_net={s['FULL']['avg_net_bp']:.1f}bp")
    print('   cost',{a:round(b,2) for a,b in ob['cost'].items()},'oos',{a:round(b,2) for a,b in ob['cost_oos'].items()},'stab',round(ob['stab'],2) if ob['stab']==ob['stab'] else None)
    print('   gates',[(g,round(float(v),3),'Y' if ok else 'N') for g,v,ok in ob['gates']])
    print('   state open',ob['open'],'pend',ob['pend'],'sig_last',ob['sig_last'],'last',ob['last_trade'])
    print('   grid',[(a,round(b,2),round(c_,2),round(d,2)) for a,b,c_,d in ob['grid']])
for k,b in bench.items(): print(k,{p:(round(v['sharpe'],2),round(v['CAGR'],3),round(v['MDD'],3),round(v['sharpe_daily'],2)) for p,v in b.items()})
print('P2',{p:v for p,v in P2s.items()})
