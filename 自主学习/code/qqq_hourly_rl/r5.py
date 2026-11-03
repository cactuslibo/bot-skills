"""Round 5: GoogleAI 点子（≤3 参数冻结规则族）：A=P2-MOC(15:30 近似收盘)、B=隔夜/日内拆分、C=最后半小时日内动量(叠加到 P2)。
多重检验：White RC + Hansen SPA（平稳 bootstrap）；DSR 计入五轮全部试验；PBO(CSCV)；跨 ETF 验证。
注：1h 数据最后一根是 15:30–16:00，'15:45 信号'用 15:30 价（=14:30 bar 收盘）近似；VIX/VIX3M 用前一日值。"""
import json, itertools, numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
from engine import EFFR, vix_ratio
COST=5e-4
RATIO=vix_ratio()
import os
QDATA=os.environ.get('QDATA','/workspace/data'); QCUT=os.environ.get('QCUT')   # 前推用：数据目录、截断日期（不含）
def load(tk):
    h=pd.read_csv(f'{QDATA}/{tk}_1h.csv'); h['time']=pd.to_datetime(h.time.str[:19]); h=h.set_index('time')
    h=h[h.index>='2015-01-02']
    if QCUT: h=h[h.index<pd.Timestamp(QCUT)]
    h['day']=h.index.normalize(); return h
class Mkt:
    def __init__(s,tk):
        h=load(tk); s.h=h; s.O,s.C=h.open.values,h.close.values; s.N=len(h)
        s.days=pd.DatetimeIndex(sorted(h.day.unique())); s.did=np.searchsorted(s.days,h.day.values)
        s.first=np.r_[True,s.did[1:]!=s.did[:-1]]; s.last=np.r_[s.did[1:]!=s.did[:-1],True]
        g=pd.Series(np.arange(s.N)).groupby(s.did); s.fi=g.first().values; s.li=g.last().values
        s.bp=np.arange(s.N)-s.fi[s.did]
        nb=s.li-s.fi+1; s.full=nb==7
        s.DC=s.C[s.li]; s.DO=s.O[s.fi]
        # 15:30 近似价：最后一根 bar 的开盘(=15:30)。半日/不完整交易日 15:30 不存在、MOC 也不可行 -> NaN（当天不做 15:30 决策）
        # [审计整改 2026-10-30：原为 np.where(s.full,O[li],DC)，半日用了真实收盘价 = 轻度前视]
        s.PX=np.where(s.full,s.O[s.li],np.nan)
        r=RATIO.reindex(s.days).ffill(limit=3).values; s.ratio=r; s.ratio_prev=np.r_[np.nan,r[:-1]]
        d=np.diff(s.DC,prepend=s.DC[0]); up=np.zeros(len(d)); dn=np.zeros(len(d)); a=0.5
        for i in range(1,len(d)): up[i]=up[i-1]*(1-a)+a*max(d[i],0); dn[i]=dn[i-1]*(1-a)+a*max(-d[i],0)
        s.rsi2=100-100/(1+up/np.maximum(dn,1e-12))
        dp=s.PX-np.r_[s.DC[0],s.DC[:-1]]; upp=np.r_[0,up[:-1]]*(1-a)+a*np.maximum(dp,0); dnp=np.r_[0,dn[:-1]]*(1-a)+a*np.maximum(-dp,0)
        s.rsi2_px=100-100/(1+upp/np.maximum(dnp,1e-12))
        cs=pd.Series(s.DC); s.sma={n:cs.rolling(n).mean().values for n in (4,5,6)}
        s.sum_prev={n:cs.rolling(n-1).sum().shift(1).values for n in (4,5,6)}
        s.rfbar=np.array([EFFR.get(t.year,0)/100 for t in h.index])/(252*7)
        s.yr=np.array([d.year for d in s.days])
    def returns(s,w_over,w_in,interest=False):
        Cp=np.r_[s.C[0],s.C[:-1]]; w_in_prev=np.r_[0,w_in[:-1]]
        r=w_over*(s.O/Cp-1)+w_in*(s.C/s.O-1)-COST*(np.abs(w_in-w_over)+np.abs(w_over-w_in_prev))
        if interest: r=r+(1-w_in)*s.rfbar
        dr=np.zeros(len(s.days)); np.add.at(dr,s.did,np.log1p(r)); return np.expm1(dr)
    # ---- 持仓区间 -> 权重 ----
    def hold_open_to_open(s,ivals,w_over,w_in):   # 从 day e 开盘到 day x 开盘
        for e,x in ivals:
            a=s.fi[e]; b=s.fi[x] if x<len(s.days) else s.N
            w_in[a:b]=1; w_over[a+1:min(b+1,s.N)]=1
    def p2(s,rth=15,sma=5,rmax=1.0,seg='both'):
        """原 P2：收盘信号，次日开盘买；收盘>SMA 次日开盘卖。seg: both/over(只持隔夜：信号日 MOC 买, 出场日开盘卖)/intra(只持日内)"""
        ivals=[]; inpos=False; nd=len(s.days)
        for d in range(5,nd-1):
            if not inpos and s.rsi2[d]<rth and s.ratio[d]<rmax: inpos=True; e=d+1
            elif inpos and d>=e and s.DC[d]>s.sma[sma][d]: inpos=False; ivals.append((e,d+1))
        if inpos: ivals.append((e,nd))
        w_over=np.zeros(s.N); w_in=np.zeros(s.N)
        if seg=='both': s.hold_open_to_open(ivals,w_over,w_in)
        elif seg=='intra':
            for e,x in ivals:
                for d in range(e,min(x,nd)): w_in[s.fi[d]:s.li[d]+1]=1; w_over[s.fi[d]+1:s.li[d]+1]=1
        elif seg=='over':
            for e,x in ivals:
                for d in range(e,min(x,nd-1)+1):
                    if d<nd: w_over[s.fi[d]]=1
        return w_over,w_in,ivals
    def p2moc(s,rth=15,sma=5,rmax=1.0):
        """A: 15:30 价近似收盘算 RSI2/SMA；VIX 用前一日；MOC 进出。"""
        ivals=[]; inpos=False; nd=len(s.days)
        for d in range(6,nd):
            if not inpos and s.rsi2_px[d]<rth and s.ratio_prev[d]<rmax: inpos=True; e=d
            elif inpos and d>e and s.PX[d]>(s.sum_prev[sma][d]+s.PX[d])/sma: inpos=False; ivals.append((e,d))
        if inpos: ivals.append((e,nd-1))
        w_over=np.zeros(s.N); w_in=np.zeros(s.N)
        for e,x in ivals:   # e 日收盘买 -> x 日收盘卖：持有 e+1..x 的全部
            a=s.fi[e+1] if e+1<nd else s.N; b=s.li[x]+1 if x<nd else s.N
            w_over[a:b]=1; w_in[a:b]=1
        return w_over,w_in,[(e+1,x+1) for e,x in ivals]
    def lhm(s,th=0.0025,mode='follow',reg='any',base=None):
        """C: 最后半小时动量：15:30 时 (15:30 价/昨收−1) > th 则做多最后一根 bar(15:30 开盘买, MOC 卖)；reverse = 跌超 th 时买(抄底)。
           base=(w_over,w_in) 时只在 base 空仓的 bar 叠加。"""
        nd=len(s.days); prevc=np.r_[np.nan,s.DC[:-1]]; m=s.PX/prevc-1
        sig=(m>th) if mode=='follow' else (m<-th)
        if reg=='lo': sig&=s.ratio_prev<1
        sig&=s.full
        w_over=np.zeros(s.N) if base is None else base[0].copy(); w_in=np.zeros(s.N) if base is None else base[1].copy()
        n=0
        for d in np.where(sig)[0]:
            i=s.li[d]
            if w_in[i]==0 and (i+1>=s.N or w_over[i+1]==0): w_in[i]=1; w_over[i]=0; n+=1
        return w_over,w_in,n
# -------- 统计 --------
def trades_from(dr_ivals,mk,w_over,w_in):
    pass
def stats(dr,yrs_mask,ntr=None,wins=None,expo=None):
    x=dr[yrs_mask]; eq=np.cumprod(1+x); n=len(x)
    return dict(cagr=float(eq[-1]**(252/n)-1),tot=float(eq[-1]-1),mdd=float((eq/np.maximum.accumulate(eq)-1).min()))
def ex_sharpe(dr,rf): x=dr-rf; return float(x.mean()/x.std()*np.sqrt(252))
def trade_list(mk,w_over,w_in):
    """把连续持仓（任一权重>0）切成交易，算每笔收益（含成本，不计息）。"""
    Cp=np.r_[mk.C[0],mk.C[:-1]]; w_in_prev=np.r_[0,w_in[:-1]]
    r=w_over*(mk.O/Cp-1)+w_in*(mk.C/mk.O-1)-COST*(np.abs(w_in-w_over)+np.abs(w_over-w_in_prev))
    held=(w_over+w_in)>0; out=[]; i=0
    while i<mk.N:
        if held[i]:
            j=i
            while j+1<mk.N and held[j+1]: j+=1
            j2=min(j+1,mk.N-1); out.append((i,float(np.prod(1+r[i:j2+1])-1)))   # 含出场 bar 的成本
            i=j+1
        else: i+=1
    return out
def full_report(mk,w_over,w_in,lo,hi):
    dr=mk.returns(w_over,w_in); dri=mk.returns(w_over,w_in,True)
    m=(mk.days>=pd.Timestamp(lo))&(mk.days<pd.Timestamp(hi))
    rf=np.array([EFFR.get(d.year,0)/100/252 for d in mk.days])
    tl=[t for t in trade_list(mk,w_over,w_in) if m[mk.did[t[0]]]]
    bm=np.isin(mk.did,np.where(m)[0])
    s=stats(dr,m); s['cagr_int']=stats(dri,m)['cagr']; s['exSharpe']=ex_sharpe(dri[m],rf[m])
    s['n']=len(tl); s['win']=float(np.mean([t[1]>0 for t in tl])) if tl else 0.0; s['expo']=float(((w_in+w_over)>0)[bm].mean()); s['avgw']=float(w_in[bm].mean())
    return s
# -------- 多重检验 --------
def stat_boot_idx(n,B,L,rng):
    p=1/L; idx=np.empty((B,n),int); idx[:,0]=rng.integers(0,n,B)
    for t in range(1,n):
        new=rng.random(B)<p; idx[:,t]=np.where(new,rng.integers(0,n,B),(idx[:,t-1]+1)%n)
    return idx
def rc_spa(D,B=2000,L=10,seed=0):
    """D: T×K（候选−基准 日收益差）。返回 White RC p 值、Hansen SPA(consistent) p 值。"""
    T,K=D.shape; rng=np.random.default_rng(seed); dbar=D.mean(0); idx=stat_boot_idx(T,B,L,rng)
    bm=np.stack([D[ix].mean(0) for ix in idx])           # B×K
    V=np.sqrt(T)*dbar; Vb=np.sqrt(T)*(bm-dbar)
    p_rc=float((Vb.max(1)>=V.max()).mean())
    om=np.sqrt(((np.sqrt(T)*(bm-dbar))**2).mean(0))+1e-12
    tstat=max(0,(V/om).max()); thr=-np.sqrt(2*np.log(np.log(T)))
    g=np.where(np.sqrt(T)*dbar/om>=thr,dbar,0.0)
    Zb=np.sqrt(T)*(bm-dbar+g)/om; p_spa=float((np.maximum(Zb.max(1),0)>=tstat).mean())
    return p_rc,p_spa
def pbo(R,S=16):
    """CSCV: R T×K 日收益, 指标=Sharpe。"""
    T,K=R.shape; blocks=np.array_split(np.arange(T),S); lam=[]
    for comb in itertools.combinations(range(S),S//2):
        tr=np.concatenate([blocks[i] for i in comb]); te=np.concatenate([blocks[i] for i in range(S) if i not in comb])
        sr_tr=R[tr].mean(0)/R[tr].std(0); sr_te=R[te].mean(0)/R[te].std(0)
        k=np.argmax(sr_tr); rank=(sr_te<sr_te[k]).sum()+0.5; w=rank/K; lam.append(np.log(w/(1-w)))
    lam=np.array(lam); return float((lam<=0).mean()),len(lam)
def dsr(x,ntrials,sr_var):
    sr=x.mean()/x.std(); g=0.5772
    sr0=np.sqrt(sr_var)*((1-g)*norm.ppf(1-1/ntrials)+g*norm.ppf(1-1/(ntrials*np.e)))
    return float(norm.cdf((sr-sr0)*np.sqrt(len(x)-1)/np.sqrt(1-skew(x)*sr+(kurtosis(x,fisher=False)-1)/4*sr**2))),float(sr*np.sqrt(252)),float(sr0*np.sqrt(252))
# -------- 候选集合 --------
def candidates():
    C=[]
    for rth,sma,rmax in itertools.product([10,15,20],[4,5,6],[0.95,1.0,1.05]): C.append(('A_p2moc',dict(rth=rth,sma=sma,rmax=rmax)))
    for seg,rth,sma in itertools.product(['over','intra','both'],[10,15,20],[4,5,6]): C.append(('B_seg',dict(seg=seg,rth=rth,sma=sma)))
    for th,mode,reg in itertools.product([0.0,0.0025,0.005,0.01],['follow','reverse'],['any','lo']): C.append(('C_p2+lhm',dict(th=th,mode=mode,reg=reg)))
    return C
def build(mk,fam,p):
    if fam=='A_p2moc': return mk.p2moc(**p)[:2]
    if fam=='B_seg': return mk.p2(rth=p['rth'],sma=p['sma'],seg=p['seg'])[:2]
    if fam=='C_p2+lhm':
        b=mk.p2()[:2]; return mk.lhm(base=b,**p)[:2]
    if fam=='P2': return mk.p2()[:2]
