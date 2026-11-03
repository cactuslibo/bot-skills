# 独立复算：不 import r5/r6/r7，只读原始 CSV
import numpy as np,pandas as pd
EFFR={2014:0.09,2015:0.13,2016:0.40,2017:1.00,2018:1.83,2019:2.16,2020:0.38,2021:0.08,2022:1.68,2023:5.02,2024:5.14,2025:4.20,2026:3.80}
def ld(f):
    x=pd.read_csv('/workspace/data/'+f); x['time']=pd.to_datetime(x.time.str[:19]); return x.set_index('time')
q=ld('QQQ_1h.csv'); q=q[q.index>='2015-01-02']; q['day']=q.index.normalize()
g=q.groupby('day'); D=pd.DataFrame(dict(o=g.open.first(),c=g.close.last(),nb=g.size()))
D['px']=np.where(D.nb==7,g.open.last(),D.c)          # 15:30 bar 开盘
lo6=q[q.index.time<=pd.Timestamp('14:30').time()].groupby('day').low.min()
vx=pd.read_csv('/workspace/qqq_bottom/data/full/VIX.csv',parse_dates=['time']).set_index('time').close
v3=pd.read_csv('/workspace/qqq_bottom/data/full/VIX3M.csv',parse_dates=['time']).set_index('time').close
D['ratio']=(vx/v3).reindex(D.index).ffill(limit=3)
def rsi2(c):
    d=c.diff().fillna(0); u=d.clip(lower=0).ewm(alpha=.5,adjust=False).mean(); n=(-d.clip(upper=0)).ewm(alpha=.5,adjust=False).mean(); return 100-100/(1+u/n.clip(lower=1e-12)),u,n
D['r2'],U,Dn=rsi2(D.c)
dp=D.px-D.c.shift(1); up=U.shift(1)*.5+.5*dp.clip(lower=0); dn=Dn.shift(1)*.5+.5*(-dp).clip(lower=0); D['r2px']=100-100/(1+up/dn.clip(lower=1e-12))
D['sma5']=D.c.rolling(5).mean()
VH=ld('VIX_1h.csv'); V3H=ld('VIX3M_1h.csv'); AD=ld('ADV_DECL_1h.csv')
def at(df,col,t='14:30'):
    s=df[df.index.time==pd.Timestamp(t).time()][col]; s.index=s.index.normalize(); return s
VHr=VH[VH.index.time>=pd.Timestamp('09:30').time()]
D['rtr']=(at(VHr,'close')/at(V3H,'close')).reindex(D.index)
D['vix']=at(VHr,'close').reindex(D.index)
D['vhi']=VHr[VHr.index.time<=pd.Timestamp('14:30').time()].high.groupby(VHr[VHr.index.time<=pd.Timestamp('14:30').time()].index.normalize()).max().reindex(D.index)
D['br']=(at(AD,'decl')/(at(AD,'decl')+at(AD,'advn'))).reindex(D.index)
D['full']=D.nb==7
# 日级回测：持有状态 day-level，收益 = 隔夜 + 日内
def bt(panic=None,lo='2022-01-01',hi='2026-10-30'):
    c=D.c.values;o=D.o.values;n=len(D); wo=np.zeros(n); wi=np.zeros(n); inpos=False; trig=[]
    for d in range(6,n):
        if inpos:
            if d>=e and c[d]>D.sma5.values[d]: inpos=False; xs.append(d+1)
            continue
        if panic and D.full.values[d] and D.r2px.values[d]<panic[2] and D.br.values[d]>=panic[1] and D.rtr.values[d]>=1 and D.vix.values[d]<=D.vhi.values[d]*(1-panic[0]):
            inpos=True; e=d+1; trig.append(D.index[d]); es.append(('moc',d+1)); continue
        if D.r2.values[d]<15 and D.ratio.values[d]<1: inpos=True;e=d+1; es.append(('open',d+1))
    return trig
xs=[];es=[]
def run(panic=None,lo='2022-01-01',hi='2026-10-30'):
    global xs,es; xs=[];es=[]; trig=bt(panic)
    if len(xs)<len(es): xs.append(len(D))
    c=D.c.values;o=D.o.values;n=len(D); r=np.zeros(n); pc=np.r_[c[0],c[:-1]]
    tr=[]
    for (m,e),x in zip(es,xs):
        # 持有：若 moc，e-1 收盘买（含隔夜），否则 e 开盘买；x 开盘卖
        p=1.0
        if m=='moc': r[e-1]-=5e-4; 
        else: r[e]-=5e-4
        for d in range(e,min(x,n)):
            if d>e or m=='moc': r[d]+=o[d]/pc[d]-1
            r[d]+=c[d]/o[d]-1 if True else 0
        if x<n: r[x]+=o[x]/pc[x]-1-5e-4
        seg=r[(e-1 if m=='moc' else e):min(x,n-1)+1]; tr.append((D.index[e],np.prod(1+seg)-1))
    idx=D.index; mk=(idx>=lo)&(idx<hi); rf=np.array([EFFR[t.year]/100/252 for t in idx])
    x=r[mk]; eq=np.cumprod(1+x); ex=(r+0)[mk]  # 不计息
    # 计息日收益：空仓日+rf（近似：持仓日不计息）
    held=np.zeros(n)
    for (m,e),xx in zip(es,xs): held[e:min(xx,n)]=1
    ri=r+(1-held)*rf; exs=(ri-rf)[mk]
    t=[w for d0,w in tr if lo<=str(d0.date())<hi]
    return dict(cagr=eq[-1]**(252/len(x))-1,mdd=(eq/np.maximum.accumulate(eq)-1).min(),exS=exs.mean()/exs.std()*np.sqrt(252),n=len(t),win=np.mean([w>0 for w in t]),hold=held[mk].mean()),trig
p2,_=run(); print('P2',{k:round(v,4) for k,v in p2.items()})
g1,trig=run((0.03,0.6,5)); print('G1',{k:round(v,4) for k,v in g1.items()})
print('G1 恐慌触发日(全期):',[str(t.date()) for t in trig])
for y in (0.03,0.06,0.10):
  for z in (0.6,0.7,0.8):
    for rp in (5,10,20):
      _,tg=run((y,z,rp)); tt=[t for t in tg if t<pd.Timestamp('2022-01-01')]; print(y,z,rp,'train触发',len(tt),'oos',len(tg)-len(tt))
