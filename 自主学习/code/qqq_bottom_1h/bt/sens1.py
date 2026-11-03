"""Sensitivity of ambiguous-rule interpretations (counted as extra trials)."""
from models import *
PER={'FULL':('2015-01-02','2026-10-30'),'OOS':('2022-01-01','2026-10-30')}
def go(lab,d,a='2015-01-02'):
    R=Sim(q).run(**d); f=stats(q,R,a,'2026-10-30'); o=stats(q,R,'2022-01-01','2026-10-30')
    print(f"{lab:45s} n={f['trades']} SR={f['sharpe']:.2f} OOS={o['sharpe']:.2f} MDD={f['MDD']:.3f} gross={f['avg_gross_bp']:.1f}bp")
go('M2 Stdev=dev(Close-VWAP) [主口径]',M2())
go('M2 Stdev=stdev(Close,20)',M2(sdmode='price'))
d=M2(); go('M2 收盘>=VWAP或bar7 -> 次日开盘出场(不用MOC)',dict(entry=d['entry'],exitf=lambda i,st: c[i]>=vwap[i] or last[i]))
for w in (7,14,35): go(f'M4 spike窗口={w}根',M4(win=w),'2020-01-02')
d=M4(); go('M4 无窗口(自上次>1.02后首次<0.99)',d,'2020-01-02') if False else None
d=M5(); go('M5 bar7 -> 次日开盘出场',dict(entry=d['entry'],exitf=lambda i,st: last[i]))
def M7inc(k=7,it=0.15):
    mn=rng.rolling(k).min().values; s2=SMA(200); rg=rng.values
    return dict(entry=lambda i: rg[i]<=mn[i] and ibs[i]<it and c[i]>s2[i], exitf=lambda i,st: c[i]>h[st['sig']]+atr14[st['sig']] or i-st['ei']+1>=4)
go('M7 NR7 含当根(range<=lowest(range,7))',M7inc())
for wk in (0.5,0.7): go(f'M9 下影线≥{wk}×K线全长',M9(wick=wk))
def M9b(k=5,pct=0.005):
    mn=L.shift(1).rolling(k).min().values; lw=(np.minimum(o,c)-l)/c
    return dict(entry=lambda i: bar[i]==6 and l[i]<mn[i] and c[i]>o[i] and lw[i]>=pct*0+pct, exitf=lambda i,st: bar[i]==1 and i>st['ei'])
for p in (0.005,0.007): go(f'M9 下影线≥{p*100:.1f}%价格',M9b(pct=p))
go('M6 Pine lime(含rangeHigh)',M6(lime=True))
