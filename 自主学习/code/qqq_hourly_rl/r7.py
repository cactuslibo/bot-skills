"""Round 7：P2（原时点：收盘信号、次日开盘）+ 恐慌叠加（15:30 判断，MOC 入场），出场同 P2（收盘>SMA5 次日开盘）。
G1：恐慌 = 实时比值≥1 且 VIX 从盘中高点回落≥y 且下跌家数占比≥z 且 RSI2(15:30)<rp（需盘中 VIX，训练只有 2020–2021）。
G2：恐慌 = 前一日比值≥1 且 下跌家数占比≥z 且 QQQ 15:30 价比日内低点反弹≥y 且 RSI2(15:30)<rp（不需盘中 VIX，训练 2015–2021）。
G3：第 6 轮 F3（执行优化），资金占用按平均权重修正后重新选参。
注意：本轮方向受第 6 轮 OOS 结果启发（F2 在 OOS 表现好），存在研究者已见过 OOS 的污染。"""
import itertools, numpy as np, pandas as pd
from r6 import M6, build as b6
class M7(M6):
    def __init__(s,tk):
        super().__init__(tk)
        lo=np.full(len(s.days),np.nan)
        for d in range(len(s.days)):
            if s.full[d]: lo[d]=s.h.low.values[s.fi[d]:s.fi[d]+6].min()
        s.lo1530=lo
    def p2panic(s,kind,y,z,rp):
        nd=len(s.days); ivals=[]; inpos=False; e=None
        for d in range(6,nd):
            if inpos:
                if d>=e and s.DC[d]>s.sma[5][d]: inpos=False; ivals.append((e,d+1,mode))
                continue
            pan=False
            if s.full[d] and s.rsi2_px[d]<rp and not np.isnan(s.br[d]) and s.br[d]>=z:
                if kind=='G1': pan=(not np.isnan(s.rtr[d])) and s.rtr[d]>=1 and s.vix_rt[d]<=s.vix_hi[d]*(1-y)
                else: pan=s.ratio_prev[d]>=1 and s.PX[d]>=s.lo1530[d]*(1+y)
            if pan: inpos=True; e=d+1; mode='moc'; continue      # e=持有起始日（MOC 在 d 日收盘买入）
            if s.rsi2[d]<15 and s.ratio[d]<1: inpos=True; e=d+1; mode='open'
        if inpos: ivals.append((e,nd,mode))
        s._ivals=ivals
        w_over=np.zeros(s.N); w_in=np.zeros(s.N)
        for e,x,mode in ivals:
            a=s.fi[e] if e<nd else s.N; b=s.fi[x] if x<nd else s.N
            w_in[a:b]=1; w_over[a+1:min(b+1,s.N)]=1
            if mode=='moc' and a<s.N: w_over[a]=1                 # 前一日收盘已持有 -> 持有隔夜
        return w_over,w_in
M=M7
def cands():
    C=[]
    for y,z,rp in itertools.product([0.03,0.06,0.10],[0.6,0.7,0.8],[5,10,20]): C.append(('G1_vix_panic',dict(y=y,z=z,rp=rp)))
    for y,z,rp in itertools.product([0.005,0.01,0.02],[0.6,0.7,0.8],[5,10,20]): C.append(('G2_breadth_panic',dict(y=y,z=z,rp=rp)))
    C.append(('G3_exec',dict(mode='twap')))
    for f,dd in itertools.product([0.33,0.5,0.67],[0.0,0.005,0.01,0.02]): C.append(('G3_exec',dict(mode='scale',f=f,dd=dd)))
    return C
def build(m,fam,p):
    if fam=='P2': return m.p2()[:2]
    if fam=='G1_vix_panic': return m.p2panic('G1',**p)
    if fam=='G2_breadth_panic': return m.p2panic('G2',**p)
    if fam=='G3_exec': return m.p2exec(**p)
TRAIN={'G1_vix_panic':('2020-01-01','2022-01-01'),'G2_breadth_panic':('2015-01-01','2022-01-01'),'G3_exec':('2015-01-01','2022-01-01')}
