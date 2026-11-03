# 去熊市版本：指标/信号在完整数据上连续计算；熊市区间内强制空仓且该区间收益不计入；
# 区间结束后第一根真实K线开盘按“信号状态 want”（区间内照常更新）直接重新进场。买入持有同样剔除。
import etf_bt as E, numpy as np, pandas as pd
from multiprocessing import Pool
BEARS=[('2018-10-01','2018-12-24'),('2020-02-19','2020-03-23'),('2021-11-19','2022-12-28')]  # QQQ 顶/底日（含首尾整日）
def bearmask(idx):
    m=np.zeros(len(idx),bool); dd=idx.normalize()
    for a,b in BEARS: m|=(dd>=pd.Timestamp(a))&(dd<=pd.Timestamp(b))
    return m
_Base=E.BT
class BB(_Base):
    def __init__(s,t): super().__init__(t); s.bear=bearmask(s.idx)
    def run(s,en,ex,warm):
        pos=_Base.run(s,en,ex,warm); pos[s.bear]=0; return pos   # want-state machine untouched; after bear pos=want at first real bar
    def equity(s,pos,cost=0.,lo=None,hi=None):
        msk=~s.bear
        if lo is not None: msk&=s.idx>=pd.Timestamp(lo)
        if hi is not None: msk&=s.idx<pd.Timestamp(hi)
        ii=np.where(msk)[0]; p=pos[ii].copy()
        contig=np.r_[False,np.diff(ii)==1]          # first bar after a removed bear block: no gap return, entry at its open
        prevp=np.r_[0,p[:-1]]; prevp[~contig]=0
        gap=np.r_[0,s.O[ii[1:]]/s.C[ii[1:]-1]-1]; gap[~contig]=0; intr=s.C[ii]/s.O[ii]-1
        nxt_break=np.r_[~contig[1:],False]          # forced exit at close of last bar before bear
        r=(1+prevp*gap)*(1+p*intr)*(1-cost*np.abs(p-prevp))*(1-cost*p*nxt_break)-1
        return pd.Series(np.cumprod(1+r),s.idx[ii]),p
E.BT=BB
if __name__=='__main__':
    with Pool(8) as P: R=dict(P.map(E.one,E.T20))
    pd.to_pickle(R,'results_nobear.pkl')
