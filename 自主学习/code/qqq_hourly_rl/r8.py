"""Round 8：目标 = 比 P2 多出几十笔交易，且新分支在训练段触发 ≥5 次（WIN_CRITERIA A1）。
H1 多日分档：RSI2<rl（且比值<rmax）先买 f，出现 P2 信号再补满；出场同 P2。训练 2015–2021。
H2 低阈值恐慌 + 严格反转（涨跌家数版，训练 2015–2021）：RSI2(15:30)<rp，下跌家数占比≥z，15:30 价比日内低点反弹≥y，14:30 K 线收阳，且下跌家数占比较 13:30 下降。
H3 低阈值恐慌 + 严格反转（盘中 VIX 版，训练只有 2020–2021）：RSI2(15:30)<rp，VIX 从盘中高点回落≥y，下跌家数占比≥z，14:30 K 线收阳，且 VIX 14:30 收盘低于 13:30 收盘。
H4 上升趋势中的小时超卖：日线收盘>SMA(L)（用前一日），14:30 K 线收盘的小时 RSI2<th，前一日比值<rmax。
H2–H4 均只在 P2 空仓时触发，15:30 判断，MOC 入场；出场同 P2（收盘>SMA5，次日开盘卖）。半日交易日不触发。"""
import itertools, numpy as np, pandas as pd
from r7 import M7
from r6 import VIXH, AD
from engine import rsi
def atT(df,col,t): s=df[df.index.time==pd.Timestamp(t).time()][col]; s.index=s.index.normalize(); return s
VIX1330=atT(VIXH,'close','13:30'); BR1330=(atT(AD,'decl','13:30')/(atT(AD,'decl','13:30')+atT(AD,'advn','13:30')))
class M8(M7):
    def __init__(s,tk):
        super().__init__(tk); nd=len(s.days)
        i5=np.minimum(s.fi+5,s.N-1); s.bull1430=np.where(s.full,s.C[i5]>s.O[i5],False)
        hr=rsi(s.h.close,2).values; s.hrsi1430=np.where(s.full,hr[i5],np.nan)
        s.vix1330=VIX1330.reindex(s.days).values; s.br1330=BR1330.reindex(s.days).values
        cs=pd.Series(s.DC); s.smaL={L:cs.rolling(L).mean().shift(1).values for L in (50,100,200)}; s.DCprev=np.r_[np.nan,s.DC[:-1]]
    def overlay(s,sig):
        nd=len(s.days); ivals=[]; inpos=False; e=None; mode=None
        for d in range(6,nd):
            if inpos:
                if d>=e and s.DC[d]>s.sma[5][d]: inpos=False; ivals.append((e,d+1,mode))
                continue
            if sig[d] and s.full[d]: inpos=True; e=d+1; mode='moc'; continue
            if s.rsi2[d]<15 and s.ratio[d]<1: inpos=True; e=d+1; mode='open'
        if inpos: ivals.append((e,nd,mode))
        s._ivals=ivals; w_over=np.zeros(s.N); w_in=np.zeros(s.N)
        for e,x,mode in ivals:
            a=s.fi[e] if e<nd else s.N; b=s.fi[x] if x<nd else s.N
            w_in[a:b]=1; w_over[a+1:min(b+1,s.N)]=1
            if mode=='moc' and a<s.N: w_over[a]=1
        return w_over,w_in
    def ladder(s,rl,f,rmax):
        """单一状态机：st 0=空仓，1=分档持 f，2=满仓。d 日收盘决定 tg[d+1]（d+1 日开盘执行）；同时记录区间用于触发计数。"""
        nd=len(s.days); st=0; tg=np.zeros(nd+1); ivals=[]; e=None; lad=False
        for d in range(6,nd):
            if st>0 and s.DC[d]>s.sma[5][d]:
                ivals.append((e,d+1,'ladder' if lad else 'open')); st=0
            elif st<2 and s.rsi2[d]<15 and s.ratio[d]<1:
                if st==0: e=d+1; lad=False
                st=2
            elif st==0 and s.rsi2[d]<rl and s.ratio[d]<rmax: st=1; e=d+1; lad=True
            tg[d+1]=[0,f,1][st]
        s._ivals=ivals
        w_over=np.zeros(s.N); w_in=np.zeros(s.N)
        for d in range(nd):
            a,b=s.fi[d],s.li[d]+1
            w_in[a:b]=tg[d]; w_over[a+1:b]=tg[d]
            w_over[a]=tg[d-1] if d>0 else 0      # 隔夜持有前一日权重，开盘调到 tg[d]
        return w_over,w_in
    def sigH2(s,rp,z,y):
        return (s.rsi2_px<rp)&(s.br>=z)&(s.PX>=s.lo1530*(1+y))&s.bull1430&(s.br<s.br1330)
    def sigH3(s,rp,y,z):
        return (s.rsi2_px<rp)&(s.vix_rt<=s.vix_hi*(1-y))&(s.br>=z)&s.bull1430&(s.vix_rt<s.vix1330)
    def sigH4(s,th,L,rmax):
        return (s.DCprev>s.smaL[L])&(s.hrsi1430<th)&(s.ratio_prev<rmax)
M=M8
def cands():
    C=[]
    for rl,f,rmax in itertools.product([20,25,30,35],[0.5,0.67],[1.0,1.05,9]): C.append(('H1_ladder',dict(rl=rl,f=f,rmax=rmax)))
    for rp,z,y in itertools.product([15,20,30],[0.55,0.6,0.65],[0.003,0.006,0.01]): C.append(('H2_breadth_rev',dict(rp=rp,z=z,y=y)))
    for rp,y,z in itertools.product([15,20,30],[0.02,0.04,0.06],[0.55,0.6,0.65]): C.append(('H3_vix_rev',dict(rp=rp,y=y,z=z)))
    for th,L,rmax in itertools.product([5,10,20],[50,100,200],[0.95,1.0,1.05]): C.append(('H4_uptrend_dip',dict(th=th,L=L,rmax=rmax)))
    return C
def build(m,fam,p):
    with np.errstate(invalid='ignore'):
        if fam=='P2': return m.p2()[:2]
        if fam=='H1_ladder': return m.ladder(**p)
        if fam=='H2_breadth_rev': return m.overlay(np.nan_to_num(m.sigH2(**p)).astype(bool))
        if fam=='H3_vix_rev': return m.overlay(np.nan_to_num(m.sigH3(**p)).astype(bool))
        if fam=='H4_uptrend_dip': return m.overlay(np.nan_to_num(m.sigH4(**p)).astype(bool))
def triggers(m,fam,lo,hi):
    """新分支在 [lo,hi) 的触发次数（按入场日计）。"""
    return sum(1 for e,x,md in m._ivals if md in ('moc','ladder') and e<len(m.days) and pd.Timestamp(lo)<=m.days[e]<pd.Timestamp(hi))
TRAIN={'H1_ladder':('2015-01-01','2022-01-01'),'H2_breadth_rev':('2015-01-01','2022-01-01'),'H3_vix_rev':('2020-01-01','2022-01-01'),'H4_uptrend_dip':('2015-01-01','2022-01-01')}
