"""第 11 次验证集查看（已先在 OOS_LOG.md 登记）：验证集终点修正为 2026-10-28 后重算 P2、H2；同时给出旧区间结果以分离"终点变化"和"数据变化"的影响。"""
import json, numpy as np, pandas as pd
from r8 import M8, build
from r5 import full_report
from config import VAL
OLD=('2022-01-01','2026-10-30')
m=M8('QQQ'); H2=dict(rp=30,z=0.6,y=0.006); out={}
for name,(fam,p) in {'P2':('P2',None),'H2':('H2_breadth_rev',H2)}.items():
    w=build(m,fam,p)
    for lab,iv in [('new_end_2026-10-28',VAL),('old_end_2026-10-29',OLD)]:
        s=full_report(m,*w,*iv); out[f'{name}|{lab}']=s; print(name,lab,{k:round(v,4) for k,v in s.items()})
# 第 1 轮 p2.py 口径（日线文件）
import engine
q=engine.load_daily(); O,C=q.open.values,q.close.values; r2=engine.rsi(q.close,2).values; s5=q.close.rolling(5).mean().values
pos,tr=engine.run(O,C,q.index,(r2<15)&(q.ratio.values<1),lambda i,ei,ef:C[i]>s5[i]); r=engine.returns(O,C,q.index,pos)
for lab,(lo,hi) in [('R1_daily_new_end',('2022-01-01','2026-10-29')),('R1_daily_old_end',('2022-01-01','2026-10-30'))]:
    s=engine.metrics(r,q.index,tr,pos,252,lo,hi); out[f'P2_daily|{lab}']={k:float(v) for k,v in s.items()}; print('P2_daily',lab,{k:round(float(v),4) for k,v in s.items()})
json.dump(out,open('recalc_val_end.json','w'),indent=1)
