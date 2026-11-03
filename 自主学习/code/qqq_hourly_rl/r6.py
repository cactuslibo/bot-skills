"""Round 6：盘中 VIX/VIX3M（15:30 用 14:30 K 线收盘值 = 已收盘 K 线）计算 P2 实时信号 + 恐慌确认；以及分批/TWAP 执行。
VIX 常规时段小时线从 2020 起 -> F1/F2 只有 2020–2021 两年可训练。"""
import json, itertools, numpy as np, pandas as pd
from r5 import Mkt, full_report, rc_spa, EFFR, COST
def ld(f,col='close'):
    import os; x=pd.read_csv(os.environ.get('QDATA','/workspace/data')+f'/{f}'); x['time']=pd.to_datetime(x.time.str[:19]); x=x.set_index('time')
    cut=os.environ.get('QCUT')                       # 与 r5.load 一致：按截断日（不含）丢弃之后的小时数据
    return x[x.index<pd.Timestamp(cut)] if cut else x
VIXH=ld('VIX_1h.csv'); V3H=ld('VIX3M_1h.csv'); AD=ld('ADV_DECL_1h.csv')
VIXH=VIXH[VIXH.index.time>=pd.Timestamp('09:30').time()]   # 只用常规时段
def at1430(df,col):  # 14:30 K 线（14:30–15:30）收盘值 -> 15:30 时已知
    s=df[df.index.time==pd.Timestamp('14:30').time()][col]; s.index=s.index.normalize(); return s
def dayhigh_to1430(df):
    d=df[(df.index.time>=pd.Timestamp('09:30').time())&(df.index.time<=pd.Timestamp('14:30').time())]
    return d.high.groupby(d.index.normalize()).max()
RT_RATIO=(at1430(VIXH,'close')/at1430(V3H,'close')).dropna()
VIX_RT=at1430(VIXH,'close'); VIX_HI=dayhigh_to1430(VIXH)
BR=at1430(AD,'decl')/(at1430(AD,'decl')+at1430(AD,'advn'))
class M6(Mkt):
    def __init__(s,tk):
        super().__init__(tk)
        s.rtr=RT_RATIO.reindex(s.days).values; s.vix_rt=VIX_RT.reindex(s.days).values; s.vix_hi=VIX_HI.reindex(s.days).values
        s.br=BR.reindex(s.days).values
    def rt(s,rth=15,sma=5,rmax=1.0,panic=None):
        """F1/F2：15:30 实时信号（QQQ 15:30 价 + 盘中比值），MOC 进出。panic=(y,z,rthp)：比值≥rmax 时，若 VIX 从盘中高点回落≥y 且下跌家数占比≥z 且 RSI2_px<rthp 也入场。"""
        ivals=[]; inpos=False; nd=len(s.days)
        for d in range(6,nd):
            if np.isnan(s.rtr[d]): 
                if inpos and d>e and s.PX[d]>(s.sum_prev[sma][d]+s.PX[d])/sma: inpos=False; ivals.append((e,d))
                continue
            if not inpos:
                ok=s.rsi2_px[d]<rth and s.rtr[d]<rmax
                if not ok and panic is not None:
                    y,z,rp=panic
                    ok=s.rtr[d]>=rmax and s.rsi2_px[d]<rp and s.vix_rt[d]<=s.vix_hi[d]*(1-y) and s.br[d]>=z
                if ok: inpos=True; e=d
            elif d>e and s.PX[d]>(s.sum_prev[sma][d]+s.PX[d])/sma: inpos=False; ivals.append((e,d))
        if inpos: ivals.append((e,nd-1))
        w_over=np.zeros(s.N); w_in=np.zeros(s.N)
        for e,x in ivals:
            a=s.fi[e+1] if e+1<nd else s.N; b=s.li[x]+1
            w_over[a:b]=1; w_in[a:b]=1
            w_in[s.li[e]]=1     # MOC 买入：按最后一根 bar 的收盘成交 -> 用"持有最后一根且 bar 开盘到收盘的收益"不对，修正见下
        # 修正：MOC 买入应只从 e 日收盘开始持有；上面的 w_in[li[e]] 会多算最后半小时，撤销
        for e,x in ivals: w_in[s.li[e]]=0
        return w_over,w_in
    def p2exec(s,mode='open',f=0.5,dd=0.0):
        """F3：原 P2 信号；执行方式 open / twap（次日 7 根 K 线均匀建仓、出场日均匀减仓）/ scale（次日开盘买 f，次日收盘若低于成本×(1−dd) 则再次日开盘补满，否则也在再次日开盘补满）"""
        wo,wi,ivals=s.p2()
        if mode=='open': return wo,wi
        w_over=np.zeros(s.N); w_in=np.zeros(s.N); nd=len(s.days)
        for e,x in ivals:
            a=s.fi[e]; b=s.fi[x] if x<nd else s.N
            w_in[a:b]=1; w_over[a+1:min(b+1,s.N)]=1
            if mode=='twap':
                for j in range(min(7,b-a)): w_in[a+j]=(j+1)/7; w_over[a+j]=j/7 if j>0 else 0
                if x<nd:
                    for j in range(7):
                        i=s.fi[x]+j
                        if i<=s.li[x]: w_over[i]=1-j/7 if j>0 else 1; w_in[i]=1-(j+1)/7
            elif mode=='scale':
                # e 日持 f；若 e 日收盘 < 开盘成本×(1−dd)，e+1 开盘补满，否则一直保持 f（dd=0 时总是补满）
                end=min(s.li[e]+1,b); w_in[a:end]=f; w_over[a+1:end]=f
                if end<b: w_over[end]=f
                if not (s.DC[e]<s.O[a]*(1-dd) or dd==0):
                    w_in[end:b]=f; w_over[end:min(b+1,s.N)]=f
        return w_over,w_in
def cands():
    C=[]
    for rth,sma,rmax in itertools.product([10,15,20],[4,5,6],[0.95,1.0,1.05]): C.append(('F1_rt',dict(rth=rth,sma=sma,rmax=rmax)))
    for y,z,rp in itertools.product([0.03,0.06,0.10],[0.6,0.7,0.8],[5,10,20]): C.append(('F2_rt+panic',dict(panic=(y,z,rp))))
    C.append(('F3_exec',dict(mode='twap')))
    for f,dd in itertools.product([0.33,0.5,0.67],[0.0,0.005,0.01,0.02]): C.append(('F3_exec',dict(mode='scale',f=f,dd=dd)))
    return C
def build(m,fam,p):
    if fam=='P2': return m.p2()[:2]
    if fam=='F1_rt': return m.rt(**p)
    if fam=='F2_rt+panic': return m.rt(**p)
    if fam=='F3_exec': return m.p2exec(**p)
M=M6
TRAIN={'F1_rt':('2020-01-01','2022-01-01'),'F2_rt+panic':('2020-01-01','2022-01-01'),'F3_exec':('2015-01-01','2022-01-01')}
