# MyRSI 逃顶 v3：在 td.py（上一轮顶背离框架，标签/切分/搜索/检验不变）上扩展三类防卖飞候选
import os; os.environ['IND']='MyRSI'
import sys; sys.path.insert(0,'/workspace/quant_myrsi_v3')
import numpy as np,pandas as pd,math,random
import td_snapshot as P
n,c,o,h,l,day,IDX=P.n,P.c,P.o,P.h,P.l,P.day,P.IDX
dcl=P.dcl
# 前日实现波动率（20日，年化）与前日长均线状态（全部 shift(1)，无前视）
dret=dcl.pct_change()
def RV(N):
    k=('rv',N)
    if k not in P.CA: P.CA[k]=(dret.rolling(N).std()*math.sqrt(252)).shift(1).reindex(day).values
    return P.CA[k]
def SLOPE(N):
    k=('sl',N)
    if k not in P.CA: m=dcl.rolling(N).mean(); P.CA[k]=(m/m.shift(20)-1).shift(1).reindex(day).values
    return P.CA[k]
SPACE=dict(P.SPACE)
SPACE.update(trig=[0,1],thr=(20.0,120.0),            # 0=顶背离(td.setup)，1=原版族 boo下穿thr
             tf=[0,1,2],tN=(50,250),                   # 趋势转弱：1=前日收盘<SMA(tN)日线，2=SMA(tN)近20日斜率<0
             kc=(0,10),buf=(0.0,0.02),nb=(1,4))        # 确认/缓冲：kc根内收盘≤触发收盘×(1−buf)；boo<绿 连续nb根
FL=P.FL|{'thr','buf'}
P.SPACE.clear(); P.SPACE.update(SPACE); P.FL=FL
def raw(p):
    x,fa,sm,mx=P.ind(p)
    if p['trig']==0: s=P.setup(p,x)
    else:
        with np.errstate(invalid='ignore'): s=np.nan_to_num((np.r_[np.nan,fa[:-1]]>=p['thr'])&(fa<p['thr'])).astype(bool)
    sh=lambda z:np.r_[np.nan,z[:-1]]
    if p['conf']:
        with np.errstate(invalid='ignore'): X=(sh(fa)>=sh(sm))&(fa<sm)
        Ls=pd.Series(np.where(s,IDX,np.nan)).ffill().values
        s=np.nan_to_num(X&(IDX-Ls<=p['W'])&(IDX-Ls>=0)).astype(bool)
    if p['nb']>1:   # 确认：boo<绿 连续 nb 根
        with np.errstate(invalid='ignore'): below=np.nan_to_num(fa<sm).astype(int)
        run=pd.Series(below).rolling(p['nb']).sum().values>=p['nb']; s&=np.nan_to_num(run).astype(bool)
    if p['kc']>0:   # 价格缓冲带：触发后 kc 根内收盘跌破 触发收盘×(1−buf) 才发信号
        t0=pd.Series(np.where(s,IDX,np.nan)).ffill().values; ref=pd.Series(np.where(s,c,np.nan)).ffill().values
        with np.errstate(invalid='ignore'): s=np.nan_to_num((IDX-t0>=1)&(IDX-t0<=p['kc'])&(c<=ref*(1-p['buf']))).astype(bool)
    s[:max(400,3*mx)]=False
    if p['tf']==1: z=np.nan_to_num(P.SMAREL(p['tN']),nan=1); s&=z<0
    elif p['tf']==2: z=np.nan_to_num(SLOPE(p['tN']),nan=1); s&=z<0
    if p['vixmax']>11.5: s&=np.nan_to_num(P.VIXp,nan=99)<=p['vixmax']
    if p['vratio']>0.75: s&=np.nan_to_num(P.VR,nan=9)<=p['vratio']
    if p['trend']: z=np.nan_to_num(P.SMAREL(p['smaN'])); s&=(z>0) if p['trend']==1 else (z<0)
    if len(P.CA)>1500: P.CA.clear()
    return s
P.raw=raw
_rp=P.rand_p
def rand_p():
    p=_rp()
    if random.random()<0.5: p['tf']=0
    if random.random()<0.5: p['kc']=0
    if random.random()<0.5: p['nb']=1
    return p
P.rand_p=rand_p
_fm0=P.filt_mask
def filt_mask(p):
    f=_fm0(p)
    if p['tf']==1: f&=np.nan_to_num(P.SMAREL(p['tN']),nan=1)<0
    elif p['tf']==2: f&=np.nan_to_num(SLOPE(p['tN']),nan=1)<0
    return f
P.filt_mask=filt_mask
# ---- 仓位：波动率缩放 × 分批减仓 ----
rh_=P.rh_; di=P.di; nd=len(P.dlist); RD=P.RD; DY=P.DY; H=P.H; COST=P.COST
def position(sig,f=1.0,vt=0.0,rvN=20):
    """小时级仓位：基础仓 = min(1, vt/前日RV)（vt=0 则 1）；信号后 t+1..t+35 减 f（t+1 开盘执行）。"""
    base=np.ones(n) if vt<=0 else np.clip(vt/np.nan_to_num(RV(rvN),nan=vt),0,1)
    w=base.copy()
    for i in sig: w[i+1:i+1+H]=base[i+1:i+1+H]*(1-f)
    return w
def daily(w):
    # 复核必须改1修正：w[t]=第t根K线持有的仓位（position 在 i+1 起减仓=信号后次根开盘成交）。
    # 第t根收益拆成 c[t-1]→o[t]（按前一根仓位）与 o[t]→c[t]（按本根仓位），不再额外平移；敞口与收益同口径。
    wp=np.r_[1.0,w[:-1]]; og=np.r_[0.0,o[1:]/c[:-1]-1]; oc=c/o-1
    r=wp*og+w*oc-COST*np.abs(w-wp)
    d=np.expm1(np.bincount(di,np.log1p(r),minlength=nd)); ex=np.bincount(di,w,minlength=nd)/np.bincount(di,minlength=nd)
    return d,ex
def missed(sig,f=1.0):
    """卖出后错过的上涨：每个信号 t+1开盘→t+35收盘 的正收益×f 之和；以及窗口内最高价相对开盘的平均涨幅。"""
    up=[max(0,c[i+H]/o[i+1]-1) for i in sig]; mx=[h[i+1:i+1+H].max()/o[i+1]-1 for i in sig]
    return dict(n=len(sig),missed_sum=float(np.sum(up)*f) if len(sig) else 0.0,n_rally=int(sum(u>0 for u in up)),
                avg_max_runup=float(np.mean(mx)) if len(sig) else None)
