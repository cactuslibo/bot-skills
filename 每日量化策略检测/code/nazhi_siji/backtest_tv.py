"""纳指四季 V22.3 回测（忠实复现 Futu 源码逻辑；收盘信号+收盘成交；整股；初始10万）"""
import pandas as pd, numpy as np, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
q=pd.read_csv("/workspace/data/QQQ_daily.csv",parse_dates=["date"]).set_index("date").sort_index()
t=pd.read_csv("/workspace/data/TQQQ_daily.csv",parse_dates=["date"]).set_index("date").sort_index()
q["ma200"]=q.close.rolling(200).mean(); q["ma20"]=q.close.rolling(20).mean()
q["pma20"]=q.ma20.shift(1); q["vma60"]=q.volume.shift(1).rolling(60).mean()
START=t.index[0]
W={"ZONE_DESPAIR_TQQQ":(0,.99),"ZONE_BATTLE_ATTACK":(0,.99),"ZONE_BATTLE_DEFEND":(.9,0),"BEAR_CASH":(0,0),
   "TOP_ESCAPE":(.9,0),"HI":(1,0),"HI_CASH":(0,0),"NORMAL":(0,.9)}
def run(cost=0.0, cap=1e5):
    idx=q.index[q.index>=START].intersection(t.index)
    pre=q[q.index<START]; ath=pre.high.iloc[-252:].max()
    st="INIT"; pend=None; rod=0; cash=cap; sq=st_=0; ntr=0; eq=[]; states=[]
    def trade(sym,qty,px):
        nonlocal cash,sq,st_,ntr
        cash-=qty*px+abs(qty)*px*cost; ntr+=1
        if sym=="Q": sq+=qty
        else: st_+=qty
    def buy(tq,tt,pq,pt):
        E=cash+sq*pq+st_*pt
        for sym,tg,cur,px in (("Q",tq,sq,pq),("T",tt,st_,pt)):
            need=E*tg-cur*px
            if need>500:
                n=min(int(need/px), int(cash/(px*(1+cost))))
                if n>0: trade(sym,n,px)
    for d in idx:
        r=q.loc[d]; pq=r.close; pt=t.close[d]
        rod = rod+1 if st in("BEAR_CASH","ZONE_BATTLE_DEFEND","TOP_ESCAPE") else 0
        if pend:
            buy(*pend,pq,pt); pend=None
        else:
            if pq>ath: ath=pq
            dd=pq/ath-1; ma200,ma20,pm=r.ma200,r.ma20,r.pma20
            top = pq>=ath*.95 and r.volume>r.vma60*2.2 and pq<r.open
            a200=pq>ma200; a20=pq>ma20; b20=pq<ma20; up=ma20>pm; dn=ma20<pm
            nxt=st; h=False
            if st=="HI" and a200:
                h=True; nxt="HI_CASH" if (b20 and dn) else "HI"
            elif st=="HI_CASH" and a200:
                h=True; nxt="NORMAL" if a20 else "HI_CASH"
            if not h:
                if pq>ma200*1.2: nxt="HI"
                elif top: nxt="TOP_ESCAPE"
                elif pq<ma200:
                    if dd<=-.3: nxt="ZONE_DESPAIR_TQQQ" if up else "ZONE_BATTLE_DEFEND"
                    elif dd<=-.1: nxt="ZONE_BATTLE_ATTACK" if pq>ma20 else "ZONE_BATTLE_DEFEND"
                    else: nxt="BEAR_CASH"
                else: nxt="ZONE_BATTLE_ATTACK" if dd<-.1 else "NORMAL"
            if st in("BEAR_CASH","ZONE_BATTLE_DEFEND","TOP_ESCAPE") and nxt in("ZONE_BATTLE_ATTACK","NORMAL"):
                if rod<2 or ma20<=pm: nxt=st
            if nxt!=st:
                st=nxt; tq,tt=W[st]; E=cash+sq*pq+st_*pt; sold=False
                if E*tq-sq*pq< -500 and sq>0:
                    n=sq if tq==0 else min(sq,int((sq*pq-E*tq)/pq))
                    if n>0: trade("Q",-n,pq); sold=True
                if E*tt-st_*pt< -500 and st_>0:
                    n=st_ if tt==0 else min(st_,int((st_*pt-E*tt)/pt))
                    if n>0: trade("T",-n,pt); sold=True
                if sold: pend=(tq,tt)
                else: buy(tq,tt,pq,pt)
        eq.append(cash+sq*pq+st_*pt); states.append(st)
    global LAST; LAST=dict(st=st,pend=pend,ath=ath,cash=cash,sq=sq,stq=st_,rod=rod)
    return pd.Series(eq,idx), pd.Series(states,idx), ntr
def stats(s):
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return dict(总收益=f"{s.iloc[-1]/s.iloc[0]-1:,.1%}",CAGR=f"{(s.iloc[-1]/s.iloc[0])**(1/yrs)-1:.2%}",
        最大回撤=f"{(s/s.cummax()-1).min():.2%}",夏普=f"{r.mean()/r.std()*np.sqrt(252):.2f}",
        年化波动=f"{r.std()*np.sqrt(252):.1%}")
eq,sts,n=run(); SNAP=dict(LAST); eqc,_,nc=run(0.0005)
idx=eq.index; bq=q.close[idx]/q.close[idx[0]]*1e5; bt=t.close[idx]/t.close[idx[0]]*1e5
res=pd.DataFrame({"策略V22.3":stats(eq),"策略+0.05%成本":stats(eqc),"持有QQQ":stats(bq),"持有TQQQ":stats(bt)}).T
res["交易笔数"]=[n,nc,1,1]; print(res.to_string())
yr=pd.DataFrame({k:v.groupby(v.index.year).last()/v.groupby(v.index.year).last().shift(1).fillna(v.iloc[0])-1
   for k,v in {"策略":eq,"策略+成本":eqc,"QQQ":bq,"TQQQ":bt}.items()})
print((yr*100).round(1).to_string())
print((sts.value_counts(normalize=True)*100).round(1).to_string())
ch=sts[sts!=sts.shift()]; print("状态切换次数",len(ch)); print(ch.tail(15).to_string())
plt.figure(figsize=(12,6))
for s,l in((eq,"Nazhi Siji V22.3"),(eqc,"V22.3 +0.05% cost"),(bq,"Buy&Hold QQQ"),(bt,"Buy&Hold TQQQ")): plt.plot(s,label=l)
plt.yscale("log"); plt.legend(); plt.grid(alpha=.3); plt.title("Equity (log), start $100k, 2010-02-11~"); plt.tight_layout()
plt.savefig("/workspace/nazhi_siji/equity_tv.png",dpi=120)

# ---- 最新状态快照 ----
d=eq.index[-1]; r=q.loc[d]; L=SNAP; pq=r.close; pt=t.close[d]; E=eq.iloc[-1]
print("\n==== 快照",d.date(),"====")
print("状态",L["st"],"目标",W[L["st"]],"待执行T+1",L["pend"],"risk_off_days",L["rod"])
print(f"QQQ {L['sq']}股 {L['sq']*pq/E:.2%}; TQQQ {L['stq']}股 @{pt:.2f} {L['stq']*pt/E:.2%}; 现金 {L['cash']:.0f} {L['cash']/E:.2%}; 净值 {E:,.0f}")
print(f"close {pq:.2f} open {r.open:.2f} ma200 {r.ma200:.2f} ma20 {r.ma20:.2f} prev {r.pma20:.2f} ATH {L['ath']:.2f}")
print(f"回撤 {pq/L['ath']-1:.2%} 乖离 {pq/r.ma200-1:.2%} 距MA20 {pq/r.ma20-1:.2%} 乖离20%价 {r.ma200*1.2:.2f}({r.ma200*1.2/pq-1:.2%}) 回撤-10%价 {L['ath']*0.9:.2f}({L['ath']*0.9/pq-1:.2%}) 0.95ATH {L['ath']*.95:.2f} vma60x2.2 {r.vma60*2.2:,.0f} vol {r.volume:,.0f}")
print(sts[sts!=sts.shift()].tail(3).to_string())
