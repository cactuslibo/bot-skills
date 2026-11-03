import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family']='Noto Sans CJK JP'; plt.rcParams['axes.unicode_minus']=False
P=[(0,100),(4,88),(6,80,'PS 初步支撑',1),(7,84),(10,66,'SC 卖出高潮',-1),(14,82,'AR 自动反弹',1),(18,68.5,'ST 二次测试',-1),
(22,78),(25,70),(28,81.5,'UA 上冲行为',1),(31,71),(34,69,'ST(B) B阶段二测',-1),(37,77),(40,72),(43,63,'Spring 弹簧',-1),
(45,74),(48,69,'Test 缩量回测',-1),(52,86,'SOS 强势信号',1),(55,78.5,'LPS 最后支撑点',-1),(58,88),(61,83,'BU 回踩确认',-1),(66,96),(69,92),(74,110)]
x=[p[0] for p in P]; y=[p[1] for p in P]
fig,(ax,av)=plt.subplots(2,1,figsize=(18,10),dpi=100,sharex=True,gridspec_kw={'height_ratios':[4,1],'hspace':0.05})
ph=[(0,15,'#f4a6a6','A阶段 止跌\nPhase A: Stopping'),(15,40.5,'#f9d89c','B阶段 构筑区间\nPhase B: Building Cause'),
(40.5,49.5,'#a8d8ea','C阶段 测试（Spring）\nPhase C: Test'),(49.5,62.5,'#b5e7a0','D阶段 突破\nPhase D: Markup Start'),(62.5,75,'#c9b6e4','E阶段 上涨\nPhase E: Markup')]
for a,b,c,t in ph:
  for A in(ax,av): A.axvspan(a,b,color=c,alpha=0.3,lw=0)
  ax.text((a+b)/2,113,t,ha='center',va='top',fontsize=12,fontweight='bold')
ax.axhline(67,ls='--',c='green',lw=1.5); ax.axhline(82,ls='--',c='red',lw=1.5)
ax.text(74.7,65.3,'支撑线 Support（SC/ST）',color='green',fontsize=11,ha='right'); ax.text(74.7,80.6,'阻力线 Resistance（AR）',color='red',fontsize=11,ha='right')
ax.plot(x,y,c='#1f3b73',lw=2.5)
for p in P:
  if len(p)>2:
    ax.plot(p[0],p[1],'o',ms=9,c='orange',mec='k',zorder=5)
    ax.annotate(p[2],(p[0],p[1]),xytext=(0,18*p[3]),textcoords='offset points',ha='center',va='bottom' if p[3]>0 else 'top',fontsize=11,
      bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='gray',alpha=0.9))
ax.set_ylim(58,115); ax.set_ylabel('价格 Price（示意）',fontsize=12); ax.set_yticks([])
ax.set_title('威科夫吸筹结构示意图（Wyckoff Accumulation Schematic #1）',fontsize=20,fontweight='bold')
V={6:55,10:100,14:65,18:35,22:32,25:28,28:30,31:22,34:20,37:18,40:16,43:45,48:10,52:80,55:22,58:40,61:25,66:50,69:30,74:55}
av.bar(list(V),list(V.values()),width=1.2,color=['#d9534f' if k in(10,52) else '#5b7db1' for k in V])
for k,t in {10:'巨量',14:'较大',18:'缩量',31:'逐渐缩量',43:'中量',48:'很小',52:'放量',55:'缩量'}.items():
  av.text(k,V[k]+3,t,ha='center',fontsize=10)
av.set_ylim(0,120); av.set_yticks([]); av.set_ylabel('成交量\nVolume',fontsize=12); av.set_xticks([]); av.set_xlim(0,75); av.set_xlabel('时间 Time（示意）',fontsize=12)
plt.savefig('wyckoff_accumulation_schematic.png',bbox_inches='tight',dpi=124)
