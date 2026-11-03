import json, numpy as np, pandas as pd
from engine import *
h=load_hourly(); O,C,idx=h.open.values,h.close.values,h.index; BPY=252*7
ratio=h.ratio_prev.values
# 日线 RSI2 前一日值（防前视）映射到小时
d=load_daily(); dr2=rsi(d.close,2).shift(1); h['dr2_prev']=h.day.map(dr2); dr2p=h.dr2_prev.values
cache={}
def feat(k,*a):
    if (k,a) not in cache:
        if k=='rsi': cache[(k,a)]=rsi(h.close,a[0]).values
        if k=='sma': cache[(k,a)]=h.close.rolling(a[0]).mean().values
        if k=='ddhi': cache[(k,a)]=(h.close/h.high.rolling(a[0]).max()-1).values
    return cache[(k,a)]
SPACE=dict(fam=['rsi','dd','hyb'],rn=[2,3,4,6,8,14],rth=[5,10,15,20,25,30],ddn=[14,35,70,140],ddth=[-0.02,-0.03,-0.04,-0.06,-0.08],
  rmax=[0.9,0.95,1.0,1.05,9],sma=[5,7,14,21,35],hold=[7,14,35,70,999],stop=[0.03,0.05,0.08,9],dth=[10,15,25,50,101])
def sample(rng): return {k:v[rng.integers(len(v))] if not isinstance(v[0],str) else v[rng.integers(len(v))] for k,v in SPACE.items()}
def build(p):
    f=p['fam']; filt=(ratio<p['rmax'])
    if f=='rsi': ent=(feat('rsi',p['rn'])<p['rth'])&filt
    elif f=='dd': ent=(feat('ddhi',p['ddn'])<p['ddth'])&filt
    else: ent=(dr2p<p['dth'])&(feat('rsi',p['rn'])<p['rth'])&filt   # 日线超卖背景 + 小时择时入场
    s=feat('sma',p['sma'])
    ex=lambda i,ei,ef:(C[i]>s[i] and i>ei) or (i-ei)>=p['hold'] or C[i]<ef*(1-p['stop'])
    pos,tr=run(O,C,idx,np.nan_to_num(ent).astype(bool),ex)
    return returns(O,C,idx,pos,bpy=BPY),tr,pos
def reward(m,years):
    if m['n']<8*years: return -9
    return m['sharpe']+1.0*(m['win']-0.6)+0.5*m['cagr']-max(0,-m['mdd']-0.15)*5-0.0*m['n']
TR=('2015-01-01','2020-01-01'); VA=('2020-01-01','2022-01-01'); TE=('2022-01-01','2026-10-30')
if __name__=='__main__':
    rng=np.random.default_rng(0); log=open('iter_log.jsonl','w'); res=[]
    for it in range(600):
        p=sample(rng); r,tr,pos=build(p); mt=metrics(r,idx,tr,pos,BPY,*TR); mv=metrics(r,idx,tr,pos,BPY,*VA)
        rec=dict(iter=it,params={k:(float(v) if not isinstance(v,str) else v) for k,v in p.items()},train={k:float(v) for k,v in mt.items()},val={k:float(v) for k,v in mv.items()},R_train=reward(mt,5),R_val=reward(mv,2))
        log.write(json.dumps(rec)+'\n'); res.append(rec)
    # 选择：train 前 30 -> 用 val 奖励挑；再取 min(R_train,R_val) 作稳健性排序
    top=sorted(res,key=lambda x:-x['R_train'])[:30]
    best=sorted(top,key=lambda x:-min(x['R_train'],x['R_val']))
    json.dump(best[:5],open('selected.json','w'),indent=1)
    for b in best[:5]: print(b['params'],round(b['R_train'],2),round(b['R_val'],2),{k:round(v,3) for k,v in b['val'].items()})
