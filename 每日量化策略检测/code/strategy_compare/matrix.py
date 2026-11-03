import pandas as pd, numpy as np
import framework as F
F.register_daily()
from framework import MK
def loadq():
    q=pd.read_csv('/workspace/ndx_escape/QQQ.csv',index_col=0,parse_dates=True); q.columns=[c.lower() for c in q.columns]
    d=q[['open','high','low','close','volume']].dropna(subset=['close'])
    m={k:v.reindex(d.index.union(v.index)).ffill().reindex(d.index) for k,v in MK.items()}
    m['vxn']=m['vxn'].combine_first(m['vix']); m['rf']=(m['irx']/100/252).fillna(0); return d,m
T=['QQQ']+open('/workspace/etf19_data/tickers.txt').read().split()
S=[('v1','v1'),('v2','v2'),('MyRSI','MyRSI'),('园园1x','园园1x'),('园园AI(1x/原版3x)','园园AI_3x'),('P2','P2')]
rows=[]
for t in T:
    px,m=loadq() if t=='QQQ' else F.load(t); r={'标的':t,'日期':str(px.index[-1].date())}
    for lab,k in S:
        if k=='园园AI_3x' and t!='QQQ': r[lab]='N/A（仅QQQ）'; continue
        w=F.STRATEGIES[k](px,m)[0]
        if isinstance(w,dict):
            wq,wt=w['legs'][0][0],w['legs'][1][0]; tot=wq+wt; note=f"（QQQ {wq.iloc[-1]:g}/TQQQ {wt.iloc[-1]:g}）"
        else: tot=w; note=''
        a,b=tot.iloc[-1],tot.iloc[-2]
        if pd.isna(a): r[lab]='无法计算（数据缺）'; continue
        st='买入' if a>b+1e-9 else ('卖出' if a<b-1e-9 else ('持仓' if a>0 else '空仓'))
        r[lab]=f"{a:g} {st}{note}"
    rows.append(r)
df=pd.DataFrame(rows); df.to_csv('current_matrix.csv',index=False,encoding='utf-8-sig')
print(df.to_markdown(index=False))
for lab,_ in S:
    c=df[lab].str.extract(r'(持仓|空仓|卖出|买入)')[0].value_counts().to_dict(); print(lab,c)
