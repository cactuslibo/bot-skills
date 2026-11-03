from engine import *
q=load_daily(); O,C=q.open.values,q.close.values; r2=rsi(q.close,2).values; s5=q.close.rolling(5).mean().values
ent=(r2<15)&(q.ratio.values<1)
pos,tr=run(O,C,q.index,ent,lambda i,ei,ef:C[i]>s5[i])
r=returns(O,C,q.index,pos)
import json
for lo,hi in [('2015-01-01','2020-01-01'),('2020-01-01','2022-01-01'),('2022-01-01','2026-10-30'),('2015-01-01','2026-10-30')]:
    print(lo,hi,{k:round(v,4) for k,v in metrics(r,q.index,tr,pos,252,lo,hi).items()})
