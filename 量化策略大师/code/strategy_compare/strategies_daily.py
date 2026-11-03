"""每日量化策略检测 bot 的四个策略，按其代码原参数移植为“T日收盘目标仓位”函数（不调参）。
统一口径差异：原代码 收盘成交/次日开盘成交、整股、min_tr=500、现金0 —— 本框架统一为 T日信号→T+1收盘执行、5bp、空仓拿T-bill。"""
import pandas as pd, numpy as np
from framework import sma, MK, rd, D
VIX3M=rd(D+'VIX3M.csv').Close; TQQQ=rd(D+'TQQQ.csv').Close
def myrsi(px,m):
    c=px.close; sd=c.rolling(21).std(ddof=0); boo=100*(c+2*sd-c.rolling(21).mean())/(4*sd)
    g,r=boo.ewm(span=12,adjust=False).mean(),boo.ewm(span=120,adjust=False).mean(); s200=sma(c,200)
    buy=(g>r)&(g.shift()<=r.shift())&(c>s200); sell=c<s200; pos=0; out=[]
    for b,s in zip(buy.values,sell.values):
        if pos==0 and b: pos=1
        elif pos==1 and s: pos=0
        out.append(float(pos))
    return pd.Series(out,c.index),None
RISK_OFF=("BEAR_CASH","ZONE_BATTLE_DEFEND","TOP_ESCAPE"); RISK_ON=("ZONE_BATTLE_ATTACK","NORMAL")
def siji_states(px):
    c,o,h,v=px.close,px.open,px.high,px.volume
    ma200,ma20=sma(c,200),sma(c,20); pm=ma20.shift(1); vma60=v.shift(1).rolling(60).mean()
    st="INIT"; rod=0; ath=h.iloc[:252].max(); skip=False; out=[]
    W1={"NORMAL":1,"ZONE_BATTLE_ATTACK":1,"ZONE_DESPAIR_TQQQ":1,"ZONE_BATTLE_DEFEND":.5,"TOP_ESCAPE":.5,"HI":.5,"BEAR_CASH":0,"HI_CASH":0,"INIT":1}
    for i in range(len(c)):
        if i<252: out.append("INIT"); continue
        p=c.iloc[i]; rod=rod+1 if st in RISK_OFF else 0
        if skip: skip=False; out.append(st); continue      # 原代码：卖出后T+1只执行买入、不判信号
        if p>ath: ath=p
        dd=p/ath-1; a,b,pmi=ma200.iloc[i],ma20.iloc[i],pm.iloc[i]
        top=v.iloc[i]>0 and vma60.iloc[i]>0 and p>=ath*.95 and v.iloc[i]>vma60.iloc[i]*2.2 and p<o.iloc[i]
        nxt=st; hh=False
        if st=="HI" and p>a: hh=True; nxt="HI_CASH" if (p<b and b<pmi) else "HI"
        elif st=="HI_CASH" and p>a: hh=True; nxt="NORMAL" if p>b else "HI_CASH"
        if not hh:
            if p>a*1.2: nxt="HI"
            elif top: nxt="TOP_ESCAPE"
            elif p<a:
                if dd<=-.3: nxt="ZONE_DESPAIR_TQQQ" if b>pmi else "ZONE_BATTLE_DEFEND"
                elif dd<=-.1: nxt="ZONE_BATTLE_ATTACK" if p>b else "ZONE_BATTLE_DEFEND"
                else: nxt="BEAR_CASH"
            else: nxt="ZONE_BATTLE_ATTACK" if dd<-.1 else "NORMAL"
        if st in RISK_OFF and nxt in RISK_ON and (rod<2 or not b>pmi): nxt=st
        if nxt!=st:
            if W1.get(nxt,1)<W1.get(st,1): skip=True
            st=nxt
        out.append(st)
    return pd.Series(out,c.index),W1
def siji_1x(px,m):
    s,W1=siji_states(px); return s.map(W1).astype(float),None
WAI={"ZONE_DESPAIR_TQQQ":(0,.99),"ZONE_BATTLE_ATTACK":(0,.99),"ZONE_BATTLE_DEFEND":(.9,0),"BEAR_CASH":(0,0),"TOP_ESCAPE":(.9,0),"HI":(1,0),"HI_CASH":(0,0),"NORMAL":(0,.9),"INIT":(1,0)}
def _ai_states(px):
    # AI版：任一腿减仓即触发T+1跳过；与1x版状态机相同，仅跳过条件按两腿判断
    s,_=siji_states(px); return s
def yuanyuan_ai_1x(px,m):
    s=_ai_states(px); return s.map(lambda x:sum(WAI[x])).astype(float),None
def yuanyuan_ai_3x(px,m):
    s=_ai_states(px); r=px.close.pct_change().fillna(0)
    t=TQQQ.reindex(px.index).pct_change()
    r3=(3*r-0.0095/252).where(t.isna(),t)          # 2010-02-11前用 3×日收益−0.95%/252 合成
    return dict(legs=[(s.map(lambda x:WAI[x][0]).astype(float),r),(s.map(lambda x:WAI[x][1]).astype(float),r3)]),None
def p2(px,m):
    c=px.close; d=c.diff(); au=d.clip(lower=0).ewm(alpha=.5,adjust=False).mean(); ad=(-d.clip(upper=0)).ewm(alpha=.5,adjust=False).mean()
    rsi=100-100/(1+au/ad); s5=sma(c,5); ratio=m['vix']/VIX3M.reindex(c.index.union(VIX3M.index)).ffill().reindex(c.index)
    pos=0; out=[]
    for i in range(len(c)):
        if pos==0 and rsi.iloc[i]<15 and ratio.iloc[i]<1: pos=1
        elif pos==1 and c.iloc[i]>s5.iloc[i]: pos=0
        out.append(float(pos))
    w=pd.Series(out,c.index); w[ratio.isna()]=np.nan     # VIX3M 2006-07前无数据→该策略无定义
    return w,None
