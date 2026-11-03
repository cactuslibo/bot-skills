import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
plt.rcParams['font.family']='Noto Sans CJK SC'; plt.rcParams['axes.unicode_minus']=False
d=pd.read_csv('CRCL_daily.csv',parse_dates=['date']); d['vm']=d.volume.rolling(20).mean().shift(1)
ix={k:i for i,k in enumerate(d.date.dt.strftime('%Y-%m-%d'))}
fig,(ax,av)=plt.subplots(2,1,figsize=(18,10),dpi=110,sharex=True,gridspec_kw={'height_ratios':[4,1],'hspace':0.03})
x=np.arange(len(d)); up=d.close>=d.open; col=np.where(up,'#26a69a','#ef5350')
ax.vlines(x,d.low,d.high,color=col,lw=0.8)
ax.bar(x,(d.close-d.open).abs().clip(lower=0.05),bottom=np.minimum(d.open,d.close),color=col,width=0.7)
av.bar(x,d.volume/1e6,color=col,width=0.7); av.plot(x,d.vm/1e6,color='#555',lw=1,label='20日均量')
av.set_ylabel('成交量(百万)'); av.legend(loc='upper right',fontsize=9)
phases=[('2025-06-05','2025-06-23','#7cb342','上涨\nMU'),
 ('2025-06-23','2025-11-07','#e53935','派发\nDistribution'),
 ('2025-11-07','2026-02-05','#8e24aa','下跌\nMarkdown'),
 ('2026-02-05','2026-03-23','#1e88e5','吸筹A\nPhase A'),
 ('2026-03-23','2026-10-30','#ffb300','吸筹B(待确认)\nPhase B?')]
for a,b,c,n in phases:
    ax.axvspan(ix[a]-0.5,ix[b]+0.5,color=c,alpha=0.10)
    ax.text((ix[a]+ix[b])/2,318,n,ha='center',va='top',fontsize=(10 if 'MU' in n else 12),color=c,weight='bold')
for y,a,b,c,t in [(262.97,'2025-06-23','2025-11-07','#e53935','派发阻力 263'),(108.0,'2025-06-23','2025-11-07','#e53935','派发支撑 108'),
                  (136.6,'2026-02-05','2026-10-30','#1e88e5','吸筹区间阻力 136.6 (AR)'),(49.9,'2026-02-05','2026-10-30','#1e88e5','吸筹区间支撑 49.9 (SC)')]:
    ax.hlines(y,ix[a],ix[b],colors=c,linestyles='--',lw=1.3); ax.text(ix[a]+1,y-9 if y<120 else y+3,t,ha='left',fontsize=9,color=c)
ev=[('2025-06-23',298.99,'BC 298.99\n买入高潮',(-14,285),'h'),('2025-06-27',175.6,'AR 175.6',(-2,150),'l'),
 ('2025-07-18',262.97,'ST/UT 263\n量1.11x',(32,290),'h'),('2025-09-05',108.02,'SOW前低 108\n量0.99x',(64,85),'l'),
 ('2025-10-10',159.47,'LPSY 159.5\n长上影收低',(85,190),'h'),('2025-11-13',81.38,'SOW 破位\n量4.95x',(118,45),'l'),
 ('2025-11-20',64.92,'PS 64.9\n量1.25x',(128,25),'l'),('2026-02-05',49.9,'SC 49.9\n连续量1.4-1.9x',(160,15),'l'),
 ('2026-02-25',83.35,'跳空放量\n5.41x',(165,125),'h'),('2026-03-17',136.6,'AR 136.6',(200,175),'h'),
 ('2026-05-12',140.0,'UT(B) 140\n量1.90x',(240,175),'h'),('2026-08-03',57.84,'ST 57.84\n量1.30x',(282,25),'l'),
 ('2026-09-03',103.28,'区间内反弹\n103.3 量1.72x',(305,150),'h'),('2026-10-30',71.0,'最新 72.54\n放量1.65x',(340,25),'l')]
for dt,p,t,(tx,ty),k in ev:
    i=ix[dt] if dt in ix else None
    ax.annotate(t,xy=(i,p),xytext=(tx,ty),fontsize=9,ha='center',arrowprops=dict(arrowstyle='->',color='k',lw=0.8),
                bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='gray',alpha=0.9))
ax.set_ylim(0,325); ax.set_ylabel('价格 (USD)'); ax.grid(alpha=0.2); av.grid(alpha=0.2)
ax.set_title('Circle (CRCL) 日线 威科夫结构标注  2025-06-05 ~ 2026-10-30（TradingView 数据）',fontsize=15)
ticks=x[::21]; av.set_xticks(ticks); av.set_xticklabels(d.date.dt.strftime('%Y-%m').iloc[ticks],fontsize=9)
ax.set_xlim(-2,len(d)+1)
plt.savefig('CRCL_wyckoff.png')
