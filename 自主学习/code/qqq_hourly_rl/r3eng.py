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
tr_=np.maximum(H-L,np.maximum(abs(H-np.r_[C[0],C[:-1]]),abs(L-np.r_[C[0],C[:-1]])))
ATR=pd.Series(tr_).ewm(alpha=1/14,adjust=False).mean().values
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
            if exit_at is None and ((p['tpk']<9 and C[i]>avg+p['tpk']*ATR[i]) or (p['stk']<9 and C[i]<avg-p['stk']*ATR[i])): exit_at=i+1
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
