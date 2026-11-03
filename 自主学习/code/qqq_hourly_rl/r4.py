"""Round 4: P2 + H4（P2 不在场时的小时级投降+反转信号）叠加；嵌套 WF；逐笔配对 bootstrap。
VIX/VIX3M：/workspace/data 无盘中 VIX 数据 -> 一律用前一交易日收盘比值。"""
import json, sys, numpy as np, pandas as pd, optuna
from multiprocessing import Pool
from r3eng import h,O,H,L,C,N,days,dayid,first,last,dly,SIG,SMA5,DC,rfbar,ATR,barpos,rsi
optuna.logging.set_verbosity(optuna.logging.WARNING)
COST=5e-4; V=h.volume.values.astype(float); YR=h.index.year.values; DYR=np.array([d.year for d in days])
RATIO_PREV=dly.ratio.shift(1).values[dayid]
RS={n:rsi(h.close,n).values for n in (2,3,5,8,14)}
DD={n:(h.close/h.high.rolling(n).max()-1).values for n in (7,14,35,70)}
# 成交量突增：与过去 20 天同一时段比较
vs=pd.Series(V); grp=barpos
VOLZ=np.zeros(N)
for b in range(7):
    m=grp==b; s=vs[m]; mu=s.shift(1).rolling(20).mean(); sd=s.shift(1).rolling(20).std(); VOLZ[m]=((s-mu)/sd).fillna(0).values
CLV=np.where(H>L,(C-L)/(H-L),0.5)              # 收盘在 bar 区间的位置（反转形态）
tp_=(H+L+C)/3; pv=pd.Series(tp_*V).groupby(dayid).cumsum().values; vv=pd.Series(V).groupby(dayid).cumsum().values
VWAPD=C/(pv/vv)-1                               # 与当日 VWAP 的距离
LASTHR=np.where(barpos==6,C/O-1,0.0)            # 最后一小时卖压（15:30 bar）
FIRSTREV=np.zeros(N)                            # 开盘首小时反转（1h 粒度无 30 分钟线，用首小时近似）：bar1 收盘收复 bar0 开盘
for i in range(1,N):
    if barpos[i]==1: FIRSTREV[i]=1.0 if (C[i-1]<O[i-1]*(1-0.003) and C[i]>O[i-1]) else 0.0
def h4_signal(p):
    s=(DD[p['ddn']]<-p['ddth'])&(RS[p['rn']]<p['rth'])
    if p['use_vol']: s&=VOLZ>p['vz']
    if p['use_rev']: s&=(CLV>p['clv'])&(C>O)
    if p['use_vwap']: s&=VWAPD<-p['vd']
    if p['use_last']: s&=LASTHR<-p['lh']
    if p['use_first']: s|=(FIRSTREV>0)&(DD[p['ddn']]<-p['ddth'])
    if p['reg']=='hi': s&=RATIO_PREV>=1
    elif p['reg']=='lo': s&=RATIO_PREV<1
    return np.nan_to_num(s).astype(bool)
def sim(p,use_h4=True):
    sig=h4_signal(p) if use_h4 else np.zeros(N,bool)
    w=np.zeros(N); mode=None; pend=None; ei=0; ef=0; eps=[]  # eps:(start,end,mode0)
    for i in range(N):
        d=dayid[i]
        if pend=='in_p2' or pend=='in_h4':
            mode='p2' if pend=='in_p2' else 'h4'; ei=i; ef=O[i]; m0=mode; pend=None
        elif pend=='out':
            eps.append((ei,i,m0)); mode=None; pend=None
        w[i]=1.0 if mode else 0.0
        if i==N-1: break
        if mode=='h4':
            if (p['tpk']<9 and C[i]>ef+p['tpk']*ATR[i]) or (p['stk']<9 and C[i]<ef-p['stk']*ATR[i]) or (i-ei)>=p['hb']: pend='out'
            if last[i] and SIG[d]: pend=None; mode='p2'      # P2 信号到来：转入 P2 管理，不另计成本
        elif mode=='p2':
            if last[i] and DC[d]>SMA5[d]: pend='out'
        else:
            if last[i] and SIG[d]: pend='in_p2'
            elif sig[i]: pend='in_h4'
    if mode: eps.append((ei,N-1,m0))
    wprev=np.r_[0,w[:-1]]; Cp=np.r_[C[0],C[:-1]]
    r=wprev*w*(O/Cp-1)+w*(C/O-1)-COST*np.abs(w-wprev)+(1-w)*rfbar
    # 卖出发生在 open：wprev=1,w=0 时 r= -cost + 现金，隔夜部分需计入
    r+=wprev*(1-w)*(O/Cp-1)
    return r,eps,w
def DR(r):
    s=np.zeros(len(days)); np.add.at(s,dayid,np.log1p(r)); return np.expm1(s)
def tr_pnl(r,eps):
    cum=np.cumprod(1+r); return [(a,b,m,cum[b]/cum[a-1]-1 if a>0 else cum[b]-1) for a,b,m in eps]
def cash_ret(a,b): return float(np.prod(1+rfbar[a:b])-1)
def year_stats(out,years):
    r,eps,w=out; dr=DR(r); m=np.isin(DYR,years); dr=dr[m]; eq=np.cumprod(1+dr); sd=dr.std()
    tp=[x for x in tr_pnl(r,eps) if YR[x[0]] in years]; mb=np.isin(YR,years)
    return dict(win=float(np.mean([x[3]>0 for x in tp])) if tp else 0.0,n=len(tp),n_h4=sum(x[2]=='h4' for x in tp),tot=float(eq[-1]-1),cagr=float(eq[-1]**(252/len(dr))-1),
      mdd=float((eq/np.maximum.accumulate(eq)-1).min()),sharpe=float(dr.mean()/sd*np.sqrt(252)) if sd>0 else 0.0,expo=float(w[mb].mean()))
def boot_h4(out,years,B=2000,seed=0):
    """逐笔配对：每笔 H4 交易收益 − 同期持有现金(EFFR)收益（P2 此时空仓，即 P2 的同期收益）。单侧 p 值 H0: 均值<=0"""
    r,eps,w=out; d=np.array([x[3]-cash_ret(x[0],x[1]+1) for x in tr_pnl(r,eps) if x[2]=='h4' and YR[x[0]] in years])
    if len(d)<5: return 1.0,len(d),float(d.mean()) if len(d) else 0.0
    rng=np.random.default_rng(seed); bs=rng.choice(d,(B,len(d))).mean(1)
    return float((bs<=0).mean()),len(d),float(d.mean())
BASE=None
def p2_out(): 
    global BASE
    if BASE is None: BASE=sim(DUMMY,use_h4=False)
    return BASE
DUMMY=dict(ddn=7,ddth=0.0,rn=2,rth=0,use_vol=0,use_rev=0,use_vwap=0,use_last=0,use_first=0,reg='any',tpk=9,stk=9,hb=7)
def rel(s,b): return (s['sharpe']-b['sharpe'])+(s['win']-b['win'])+0.5*(s['cagr']-b['cagr'])
def objective(p,years):
    out=sim(p); rs=[]
    for y in years:
        rs.append(rel(year_stats(out,[y]),year_stats(p2_out(),[y])))
    return float(np.mean(rs)-0.5*np.std(rs)),out
def suggest(t):
    return dict(ddn=t.suggest_categorical('ddn',[7,14,35,70]),ddth=t.suggest_float('ddth',0.01,0.08),rn=t.suggest_categorical('rn',[2,3,5,8,14]),
      rth=t.suggest_int('rth',3,35),use_vol=t.suggest_categorical('use_vol',[0,1]),vz=t.suggest_float('vz',0.5,4),
      use_rev=t.suggest_categorical('use_rev',[0,1]),clv=t.suggest_float('clv',0.4,0.9),use_vwap=t.suggest_categorical('use_vwap',[0,1]),vd=t.suggest_float('vd',0.002,0.03),
      use_last=t.suggest_categorical('use_last',[0,1]),lh=t.suggest_float('lh',0.002,0.02),use_first=t.suggest_categorical('use_first',[0,1]),
      reg=t.suggest_categorical('reg',['any','hi','lo']),tpk=t.suggest_float('tpk',0.5,8) if t.suggest_categorical('use_tp',[0,1]) else 9,
      stk=t.suggest_float('stk',1,10) if t.suggest_categorical('use_st',[0,1]) else 9,hb=t.suggest_int('hb',3,35))
FL=['ddth','vz','clv','vd','lh','tpk','stk']
def optimize(args):
    ytest,ntr=args; years=list(range(2016,ytest)); recs=[]
    def obj(t):
        p=suggest(t); o,out=objective(p,years); recs.append((o,p)); return o
    st=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=ytest,n_startup_trials=60)); st.optimize(obj,n_trials=ntr)
    rng=np.random.default_rng(0); cand=[]
    for o,p in sorted(recs,key=lambda x:-x[0])[:15]:
        if o<=0: continue
        pv,nh,md=boot_h4(sim(p),years)
        if pv>0.10: continue                       # 显著性入选门槛（训练段）
        nb=[]
        for _ in range(6):
            q=dict(p)
            for k in FL:
                if q[k]<9: q[k]=q[k]*rng.uniform(0.85,1.15)
            q['rth']=int(np.clip(q['rth']+rng.integers(-2,3),3,35)); q['hb']=int(np.clip(q['hb']+rng.integers(-2,3),3,35))
            nb.append(objective(q,years)[0])
        if np.mean(nb)<=0: continue
        cand.append(dict(score=0.5*o+0.5*float(np.mean(nb)),obj=o,nb=float(np.mean(nb)),p_boot=pv,n_h4_train=nh,mean_diff=md,params=p))
    cand.sort(key=lambda x:-x['score'])
    return dict(ytest=ytest,chosen=cand[0] if cand else None,n_pass=len(cand),best_raw=max(recs,key=lambda x:x[0])[0])
if __name__=='__main__':
    ys=[int(x) for x in sys.argv[2].split(',')]; NT=int(sys.argv[3])
    with Pool(6) as pool: res=pool.map(optimize,[(y,NT) for y in ys])
    json.dump(res,open(f'r4_{sys.argv[1]}.json','w'),indent=1,default=float)
    for r in res:
        c=r['chosen']; print(r['ytest'],'n_pass',r['n_pass'],'best_raw',round(r['best_raw'],3),None if c is None else {k:(round(v,3) if isinstance(v,float) else v) for k,v in c.items() if k!='params'})
