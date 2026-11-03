"""Round 2: P2 日线信号门控 + 小时线优化入场/出场; walk-forward(按年)+Optuna; DSR; 邻域稳健性。"""
import json, sys, numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
from engine import EFFR, vix_ratio, rsi
COST=5e-4
h=pd.read_csv('/workspace/data/QQQ_1h.csv'); h['time']=pd.to_datetime(h.time.str[:19]); h=h.set_index('time'); h['day']=h.index.normalize()
O,H,L,C=h.open.values,h.high.values,h.low.values,h.close.values; N=len(C)
days=pd.DatetimeIndex(sorted(h.day.unique())); dayid=np.searchsorted(days,h.day.values)
first=np.r_[True,dayid[1:]!=dayid[:-1]]; last=np.r_[dayid[1:]!=dayid[:-1],True]
# 由小时数据聚合日线(同一复权口径)
dly=h.groupby('day').agg(open=('open','first'),close=('close','last'))
dly['ratio']=vix_ratio().reindex(dly.index).ffill(limit=3)
dly['r2']=rsi(dly.close,2); dly['sma5']=dly.close.rolling(5).mean(); dly['sum4']=dly.close.rolling(4).sum()
dly['sig']=(dly.r2<15)&(dly.ratio<1)
dly['intra']=dly.close/dly.open-1; dly['over']=dly.open/dly.close.shift(1)-1
SIG,SMA5,SUM4prev=dly.sig.values,dly.sma5.values,dly.sum4.shift(1).values
INTRA,OVER,DC=dly.intra.values,dly.over.values,dly.close.values
rfbar=np.array([EFFR[t.year]/100 for t in h.index])/(252*7)
RSI={n:rsi(h.close,n).values for n in (2,3,5,8,14)}
barpos=np.zeros(N,int)
for i in range(1,N): barpos[i]=0 if first[i] else barpos[i-1]+1
def sim(p):
    """返回 bar 收益 r、episodes[(start,end)]、持仓 w。"""
    w_open=np.zeros(N); w_close=np.zeros(N); w=0.0; eps=[]; st=None
    pending=None      # 入场计划 dict
    exit_at=None      # 计划在某 bar open 卖出
    held_days=0; avg=0.0; rs=RSI[p['rn']]
    for i in range(N):
        d=dayid[i]
        # ---- open 成交 ----
        if exit_at is not None and i>=exit_at and w>0:
            w=0.0; exit_at=None; eps.append((st,i)); st=None; pending=None
        if pending is not None and pending.get('buy_now'):
            amt=pending['buy_now']; avg=(avg*w+O[i]*amt)/(w+amt) if w+amt>0 else O[i]; 
            if w==0: st=i; held_days=0
            w=min(1.0,w+amt); pending['buy_now']=0
            if w>=1-1e-9: pending=None
        w_open[i]=w
        # ---- 收盘前决策(MOC 用 15:30 价近似) ----
        moc=False
        if w>0 and p['exit']=='moc' and barpos[i]==6 and i>0 and d>=5:
            est=(SUM4prev[d]+C[i-1])/5      # 用 15:30 价估计今日 SMA5
            if C[i-1]>est: moc=True
        if moc:
            w_close[i]=0.0; eps.append((st,i+1 if i+1<N else i)); st=None; w=0.0; pending=None; exit_at=None; continue
        w_close[i]=w
        # ---- bar 收盘后决策 ----
        if w>0:
            if p['tp']<9 and C[i]>avg*(1+p['tp']) and exit_at is None: exit_at=i+1
            if last[i]:
                held_days+=1
                if exit_at is None and (( p['exit']!='moc' and DC[d]>SMA5[d]) or held_days>=p['hd']):
                    # 延后出场: 第二天第 k 根 open 卖出
                    k=p['delay'] if (DC[d]>SMA5[d] and p['exit']=='delay') else 0
                    exit_at=i+1+k
        if pending is not None and pending.get('window') is not None:
            pending['left']-=1
            hit=(C[i]<=pending['ref']*(1-p['dip'])) or (rs[i]<p['rth'])
            if hit: pending['buy_now']=1-w
            elif pending['left']<=0:
                if p['force']: pending['buy_now']=1-w
                else:
                    if w==0: pending=None
                    else: pending=None
        if w==0 and pending is None and exit_at is None and last[i] and SIG[d]:
            ok=True
            if p['decomp']=='intra_dn': ok=INTRA[d]<0
            elif p['decomp']=='over_up': ok=OVER[d]>0      # 跌幅来自日内而非隔夜
            if not ok: continue
            if p['entry']=='open': pending={'buy_now':1.0}
            else:
                f=p['frac'] if p['entry']=='split' else 0.0
                pending={'buy_now':f,'window':True,'left':p['win'],'ref':DC[d],'gap':p['gap']}
        # 跳空低开立即买(隔夜分解特征): 在下一 bar open 判断
        if pending is not None and pending.get('window') and i+1<N and first[i+1] and p['gap']<9:
            if O[i+1]/C[i]-1 < -p['gap']: pending['buy_now']=1-w-pending.get('buy_now',0)+pending.get('buy_now',0)
    r=np.zeros(N); wc_prev=0.0
    for i in range(N):
        r[i]=wc_prev*((O[i]/C[i-1]-1) if i>0 else 0)+w_open[i]*(C[i]/O[i]-1)-COST*abs(w_open[i]-wc_prev)-COST*abs(w_close[i]-w_open[i])+(1-w_open[i])*rfbar[i]
        wc_prev=w_close[i]
    if st is not None: eps.append((st,N-1))
    return r,eps,w_open
idx=h.index
def stats(r,eps,w,lo,hi):
    m=(idx>=pd.Timestamp(lo))&(idx<pd.Timestamp(hi))
    dr=pd.Series(r[m],index=dayid[m]).groupby(level=0).apply(lambda x:np.prod(1+x)-1).values
    eq=np.cumprod(1+dr); yrs=len(dr)/252
    ep=[e for e in eps if m[e[0]]]; cum=np.cumprod(1+r)
    pnl=[cum[e[1]]/cum[e[0]-1]-1 if e[0]>0 else cum[e[1]]-1 for e in ep]
    sd=dr.std()
    return dict(win=float(np.mean([x>0 for x in pnl])) if pnl else 0.0,n=len(ep),tot=float(eq[-1]-1),cagr=float(eq[-1]**(1/yrs)-1),
        mdd=float((eq/np.maximum.accumulate(eq)-1).min()),sharpe=float(dr.mean()/sd*np.sqrt(252)) if sd>0 else 0.0,expo=float((w[m]>0).mean()),
        avgw=float(w[m].mean())), dr
def reward(s):
    return s['sharpe']+(s['win']-0.6)+0.5*s['cagr']-5*max(0,-s['mdd']-0.15)
P2=dict(entry='open',exit='base',tp=9,hd=999,delay=0,rn=2,rth=0,dip=0.0,win=7,force=1,frac=0.0,gap=9,decomp='none')
YEARS=list(range(2016,2022))
def wf_objective(p):
    r,eps,w=sim(p); rs=[]; nt=0
    for y in YEARS:
        s,_=stats(r,eps,w,f'{y}-01-01',f'{y+1}-01-01'); rs.append(reward(s)); nt+=s['n']
    return float(np.mean(rs)-0.5*np.std(rs)),nt,rs
GRID=dict(entry=['open','dip','split'],exit=['base','moc','delay'],tp=[0.01,0.02,0.03,0.05,9],hd=[2,3,4,5],delay=[1,2,3,4,6],
  rn=[2,3,5,8,14],rth=[5,10,15,20,25,30],dip=[0.0025,0.005,0.01,0.015,0.02],win=[3,7,10,14],force=[0,1],frac=[0.25,0.5,0.75],gap=[0.003,0.006,0.01,9],decomp=['none','intra_dn','over_up'])
if __name__=='__main__':
    import optuna; optuna.logging.set_verbosity(optuna.logging.WARNING)
    p2obj,p2n,p2rs=wf_objective(P2); print('P2 WF obj',round(p2obj,3),'trades16-21',p2n,[round(x,2) for x in p2rs])
    log=open('r2_log.jsonl','w'); trials=[]
    def obj(t):
        p={k:t.suggest_categorical(k,v) for k,v in GRID.items()}
        o,nt,rs=wf_objective(p)
        if nt<0.7*p2n: o=-9.0
        r,eps,w=sim(p); s,dr=stats(r,eps,w,'2015-01-01','2022-01-01')
        rec=dict(trial=t.number,params=p,obj=o,trades_16_21=nt,fold_R=rs,pre_oos=s); log.write(json.dumps(rec)+'\n'); log.flush()
        trials.append((o,p,dr,s)); return o
    st=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=1,n_startup_trials=60))
    st.optimize(obj,n_trials=int(sys.argv[1]) if len(sys.argv)>1 else 300)
    best=st.best_params; bo=st.best_value; print('best',best,round(bo,3))
    # Deflated Sharpe (日度, 2015-2021)
    _,_,_,_=trials[0]; srs=np.array([x[2].mean()/x[2].std() for x in trials if x[0]>-9 and x[2].std()>0])
    bdr=[x for x in trials if x[1]==best][0][2]; sr=bdr.mean()/bdr.std(); T=len(bdr); Ntr=len(srs); g=0.5772
    sr0=np.sqrt(srs.var())*((1-g)*norm.ppf(1-1/Ntr)+g*norm.ppf(1-1/(Ntr*np.e)))
    dsr=norm.cdf((sr-sr0)*np.sqrt(T-1)/np.sqrt(1-skew(bdr)*sr+(kurtosis(bdr,fisher=False)-1)/4*sr**2))
    print('DSR',round(dsr,3),'SR_ann',round(sr*np.sqrt(252),3),'SR0_ann',round(sr0*np.sqrt(252),3),'N',Ntr)
    # 邻域稳健性
    nb=[]
    for k,v in GRID.items():
        if isinstance(v[0],str): continue
        j=v.index(best[k])
        for jj in (j-1,j+1):
            if 0<=jj<len(v):
                q=dict(best); q[k]=v[jj]; o,_,_=wf_objective(q); nb.append((k,v[jj],round(o,3),round((o-bo)/abs(bo),3)))
    print('neighbors',nb)
    json.dump(dict(best=best,obj=bo,p2_obj=p2obj,dsr=float(dsr),sr_ann=float(sr*np.sqrt(252)),sr0_ann=float(sr0*np.sqrt(252)),ntrials=Ntr,neighbors=nb),open('r2_selected.json','w'),indent=1)
