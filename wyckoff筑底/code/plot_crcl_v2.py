import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family']='Noto Sans CJK JP'; plt.rcParams['axes.unicode_minus']=False
D=pd.read_csv('CRCL_daily.csv',parse_dates=['date']); D['vm']=D.volume.rolling(20).mean().shift(1)
d=D[D.date>='2025-10-01'].reset_index(drop=True)
ix={k:i for i,k in enumerate(d.date.dt.strftime('%Y-%m-%d'))}; N=len(d)
fig,(ax,av)=plt.subplots(2,1,figsize=(18,10),dpi=100,sharex=True,gridspec_kw={'height_ratios':[4,1],'hspace':0.05})
x=np.arange(N); up=d.close>=d.open; col=np.where(up,'#26a69a','#ef5350')
ax.vlines(x,d.low,d.high,color=col,lw=0.8)
ax.bar(x,(d.close-d.open).abs().clip(lower=0.05),bottom=np.minimum(d.open,d.close),color=col,width=0.7)
av.bar(x,d.volume/1e6,color=col,width=0.7)
F=N+120
ph=[(-0.5,ix['2025-11-20']-0.5,'#cccccc','前期下跌\n（含上市炒作与派发）'),
 (ix['2025-11-20']-0.5,ix['2026-04-02']+0.5,'#f4a6a6','A阶段 止跌\nPhase A: Stopping'),
 (ix['2026-04-02']+0.5,N-0.5,'#f9d89c','B阶段 构筑区间\nPhase B: Building Cause'),
 (N-0.5,N+38,'#a8d8ea','C阶段 测试（Spring）\nPhase C: Test'),(N+38,N+82,'#b5e7a0','D阶段 突破\nPhase D: Markup Start'),(N+82,F,'#c9b6e4','E阶段 上涨\nPhase E: Markup')]
for a,b,c,t in ph:
  for A in(ax,av): A.axvspan(a,b,color=c,alpha=0.3 if c!='#cccccc' else 0.45,lw=0)
  ax.text((a+b)/2,212,t,ha='center',va='top',fontsize=12,fontweight='bold',color='#555' if c=='#cccccc' else 'k')
s0=ix['2026-02-05']
ax.hlines(136.65,s0,F,ls='--',color='red',lw=1.5); ax.hlines(49.9,s0,F,ls='--',color='green',lw=1.5)
ax.hlines(57.84,ix['2026-07-31'],F,ls=':',color='green',lw=1.2)
ax.text(ix['2026-02-09'],129,'阻力线 Resistance（AR 136.6）',color='red',fontsize=11,ha='left')
ax.text(ix['2026-03-05'],43,'支撑线 Support（SC 49.9 / ST(B) 57.8）',color='green',fontsize=11,ha='left')
E=[('2025-11-20','low','PS 初步支撑\n64.92',-1),('2026-02-05','low','SC 卖出高潮\n49.90',-1),('2026-03-17','high','AR 自动反弹\n136.65',1),
 ('2026-04-02','low','ST 二次测试\n84.27',-1),('2026-05-12','high','UA 上冲行为\n140.00',1),('2026-08-03','low','ST(B) B阶段二测\n57.84',-1)]
for dt,k,t,s in E:
  i=ix[dt]; p=d[k][i]; ax.plot(i,p,'o',ms=9,c='orange',mec='k',zorder=5)
  ax.annotate(t,(i,p),xytext=(0,14*s),textcoords='offset points',ha='center',va='bottom' if s>0 else 'top',fontsize=11,
    bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='gray',alpha=0.9))
for dt,k,t,s in [('2026-09-03','high','B阶段区间内反弹 103.28',1),('2026-02-25','low','2-25 放量启动',-1)]:
  i=ix[dt]; p=d[k][i]; ax.plot(i,p,'o',ms=6,c='#bbb',mec='gray',zorder=5)
  ax.annotate(t,(i,p),xytext=(0,10*s),textcoords='offset points',ha='center',va='bottom' if s>0 else 'top',fontsize=9,color='#555')
i=N-1; ax.plot(i,72.54,'*',ms=16,c='blue',mec='k',zorder=6)
ax.annotate('当前位置：B阶段（疑似）\n2026-10-30 收 72.54',(i,72.54),xytext=(-60,75),textcoords='offset points',fontsize=11,color='blue',
  arrowprops=dict(arrowstyle='->',color='blue'),bbox=dict(boxstyle='round,pad=0.3',fc='#e8f0ff',ec='blue'))
fx=[N-1,N+8,N+18,N+24,N+33,N+44,N+54,N+62,N+70,N+80,N+92,N+118]; fy=[72.54,62,46,64,55,85,110,145,126,152,138,178]
ax.plot(fx,fy,ls='--',c='gray',lw=2)
for j,t,s in [(2,'Spring 弹簧\n（跌破49.9~57.8后收回）',-1),(4,'Test 缩量回测',-1),(7,'SOS 强势信号\n（放量突破103/136.6）',1),(8,'LPS 最后支撑点',-1),(10,'BU 回踩确认',-1)]:
  ax.plot(fx[j],fy[j],'o',ms=8,mfc='white',mec='gray',zorder=5)
  ax.annotate(t,(fx[j],fy[j]),xytext=(0,12*s),textcoords='offset points',ha='center',va='bottom' if s>0 else 'top',fontsize=10,color='gray',
    bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='gray',ls='--',alpha=0.9))
ax.text(N+85,18,'待出现：C阶段 Spring → Test → D阶段 SOS → LPS\n（虚线路径为示意，非真实数据）',ha='center',fontsize=11,color='gray',
  bbox=dict(boxstyle='round',fc='white',ec='gray',ls='--'))
V={'2026-02-05':'巨量','2026-02-25':'放量','2026-04-02':'缩量','2026-05-11':'放量','2026-08-03':'中量','2026-09-03':'较大','2025-11-20':'较大'}
for dt,t in V.items(): av.text(ix[dt],d.volume[ix[dt]]/1e6+2,t,ha='center',fontsize=10,fontweight='bold')
q=d[(d.date>='2026-07-01')&(d.date<='2026-07-30')].volume.mean()/1e6; av.text(ix['2026-07-15'],q+12,'逐渐缩量',ha='center',fontsize=10,fontweight='bold')
av.text(N+60,55,'（未来量能：Spring 中量 → Test 很小 → SOS 放量 → LPS 缩量，示意）',ha='center',fontsize=10,color='gray')
ax.set_ylim(10,215); fig.subplots_adjust(left=0.05,right=0.98,top=0.93,bottom=0.05); ax.set_ylabel('价格 Price（USD）',fontsize=12); ax.grid(alpha=0.15)
av.set_ylabel('成交量(百万)\nVolume',fontsize=12); av.set_ylim(0,d.volume.max()/1e6*1.25)
t=[i for i in range(N) if i==0 or d.date[i].month!=d.date[i-1].month]
av.set_xticks(t); av.set_xticklabels(d.date.dt.strftime('%Y-%m').iloc[t],fontsize=10); ax.set_xlim(-1,F)
ax.set_title('CRCL 日线 · 威科夫吸筹结构标注（对照标准示意图）',fontsize=20,fontweight='bold')
ins=fig.add_axes([0.50,0.66,0.17,0.19]); ins.imshow(plt.imread('wyckoff_accumulation_schematic.png')); ins.axis('off')
ins.set_title('标准示意图（对照）',fontsize=10)
plt.savefig('CRCL_wyckoff_v2.png',dpi=100)
