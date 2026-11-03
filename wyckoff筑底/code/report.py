import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family']='Noto Sans CJK JP'; plt.rcParams['axes.unicode_minus']=False
import scan_schematic2 as S
F=S.files(); R=pd.read_csv('scan_schematic2.csv').set_index('ticker')
ORDER=['SMMT','SNAP','HMY','CRCL','DOCU','CHYM','MORN','GDDY','TRI','TYL','CEG','VRSK']
SPR={'CHYM','MORN','GDDY','TRI','TYL','CEG','VRSK'}
COL={'A':'#f4a6a6','B':'#f9d89c','C':'#a8d8ea','D':'#b5e7a0','E':'#c9b6e4'}
NM={'A':'A阶段 止跌','B':'B阶段 构筑区间','C':'C阶段 测试','D':'D阶段 突破','E':'E阶段 上涨'}
def f2(x): return f'{x:.2f}'
def analyze(t):
  p,raw=F[t]; D=S.load(p,raw); D=D[D.date<='2026-10-30'].reset_index(drop=True)
  r=R.loc[t]; sc=D.index[D.date==r.sc_date][0]; ar=D.index[D.date==r.ar_date][0]; cl=D.index[D.date==r.c_low_date][0]
  D['vm']=D.volume.rolling(20).mean().shift(1)
  s0=max(0,sc-70); d=D.iloc[s0:].reset_index(drop=True); o=s0; sc-=o; ar-=o; cl-=o; N=len(d)
  # PS: highest-volume down bar in 10..60 bars before SC that is a local low
  w=d.iloc[max(0,sc-60):max(1,sc-8)]; ps=int((w.volume/w.vm).idxmax()) if len(w) else None
  # ST: lowest low between AR+3 and AR+35 (before C)
  w=d.iloc[ar+3:min(cl-15,ar+25)]; st=int(w.low.idxmin()) if len(w)>2 else None
  # UA: highest high between ST and C if > AR
  ua=None
  if st is not None:
    w=d.iloc[st:cl]; j=int(w.high.idxmax())
    if d.high[j]>r.ar_price: ua=j
  rng_hi=max(r.ar_price, d.high[ua] if ua is not None else 0)
  sos=lps=None
  w=d.iloc[cl:]; b=w[w.close>r.ar_price]
  if len(b) and r.breakout: sos=int(b.index[0]); w2=d.iloc[sos+1:]
  if sos is not None and len(w2)>3:
    pk=int(d.iloc[sos:min(N,sos+25)].high.idxmax()); w3=d.iloc[pk+1:]
    if len(w3)>2: lps=int(w3.low.idxmin())
  last=d.close.iloc[-1]; spring=r.c_low_price<r.sc_price
  if sos is not None:
    stage='E' if last>r.ar_price*1.15 and (N-sos)>40 else 'D'
  else:
    stage='D' if last>r.c_low_price*1.12 else 'C'
  return dict(t=t,d=d,r=r,sc=sc,ar=ar,cl=cl,ps=ps,st=st,ua=ua,sos=sos,lps=lps,stage=stage,last=last,spring=spring,src=p)
def conf(a):
  r=a['r']; dep=(1-r.c_low_price/r.sc_price)*100
  s=2
  if a['t'] in SPR: s-=1
  if r.low_vol_pullback: s+=1
  if a['sos'] is not None: s+=1
  if a['stage']=='C': s-=1
  if a['t'] in SPR and dep>3.5: s-=1
  return ['低','低','中','中','较高','高'][max(0,min(5,s))]
def page(a,pdf):
  d,r,t=a['d'],a['r'],a['t']; N=len(d); x=np.arange(N); dt=lambda i:d.date[i].strftime('%Y-%m-%d')
  fig=plt.figure(figsize=(16.5,11.7)); ax=fig.add_axes([0.05,0.30,0.93,0.62]); av=fig.add_axes([0.05,0.17,0.93,0.13],sharex=ax)
  up=d.close>=d.open; col=np.where(up,'#26a69a','#ef5350')
  ax.vlines(x,d.low,d.high,color=col,lw=0.8); rg=d.high.max()-d.low.min()
  ax.bar(x,(d.close-d.open).abs().clip(lower=rg*0.002),bottom=np.minimum(d.open,d.close),color=col,width=0.7)
  av.bar(x,d.volume/1e6,color=col,width=0.7)
  st=a['st'] or a['ar']+5; cS=max(st+1,a['cl']-8); cE=min(N-1,a['cl']+12)
  b=[(-0.5,'A',a['ps'] if a['ps'] is not None else a['sc']-5),(None,'B',st),(None,'C',cS),(None,'D',cE)]
  segs=[('A',(a['ps'] if a['ps'] is not None else a['sc']-5)-0.5,st+0.5),('B',st+0.5,cS-0.5),('C',cS-0.5,cE+0.5)]
  if a['stage']=='C': segs[-1]=('C',cS-0.5,N+0.5)
  else:
    eS=None
    if a['stage']=='E':
      w=d.iloc[a['sos']:]; eS=int(w.index[(w.close>r.ar_price*1.15).values][0])
      segs+= [('D',cE+0.5,eS-0.5),('E',eS-0.5,N+0.5)]
    else: segs+=[('D',cE+0.5,N+0.5)]
  ylo,yhi=d.low.min(),d.high.max(); H=yhi-ylo; top=yhi+H*0.22
  ax.axvspan(-0.5,segs[0][1],color='#cccccc',alpha=0.45,lw=0)
  if segs[0][1]>15: ax.text(segs[0][1]/2,top-H*0.01,'前期下跌',ha='center',va='top',fontsize=11,color='#555',fontweight='bold')
  for k,a0,b0 in segs:
    for A in(ax,av): A.axvspan(a0,b0,color=COL[k],alpha=0.3,lw=0)
    ax.text((a0+b0)/2,top-H*0.01,NM[k].replace(' ','\n'),ha='center',va='top',fontsize=11,fontweight='bold')
  ax.hlines(r.ar_price,a['ar'],N+3,ls='--',colors='red',lw=1.5); ax.hlines(r.sc_price,a['sc'],N+3,ls='--',colors='green',lw=1.5)
  ax.text(a['ar']+25,r.ar_price-H*0.012,f'阻力线（AR {f2(r.ar_price)}）',color='red',fontsize=10,ha='left',va='top')
  ax.text(N-2,r.sc_price-H*0.012,f'支撑线（SC {f2(r.sc_price)}）',color='green',fontsize=10,ha='right',va='top')
  ctag='Spring 弹簧' if a['spring'] else 'C阶段低点\n（更高低点，Schematic #2）'
  E=[]
  if a['ps'] is not None: E.append((a['ps'],'low','PS 初步支撑',-1))
  E+=[(a['sc'],'low','SC 卖出高潮',-1),(a['ar'],'high','AR 自动反弹',1)]
  if a['st'] is not None: E.append((a['st'],'low','ST 二次测试',-1))
  if a['ua'] is not None: E.append((a['ua'],'high','UA 上冲行为',1))
  E.append((a['cl'],'low',ctag,-1))
  if a['sos'] is not None: E.append((a['sos'],'high','SOS 强势信号',1))
  if a['lps'] is not None and a['lps']<N-3: E.append((a['lps'],'low','LPS 最后支撑点',-1))
  E.sort(); lastx={1:-99,-1:-99}; lvl={1:0,-1:0}
  for i,k,tx,s in E:
    p=d[k][i]; lvl[s]=lvl[s]+1 if i-lastx[s]<14 else 0; lastx[s]=i
    ax.plot(i,p,'o',ms=9,c='orange',mec='k',zorder=5)
    ax.annotate(f'{tx}\n{dt(i)} {f2(p)}',(i,p),xytext=(0,s*(14+lvl[s]*34)),textcoords='offset points',ha='center',va='bottom' if s>0 else 'top',fontsize=9.5,
      arrowprops=dict(arrowstyle='-',color='gray',lw=0.6),bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='gray',alpha=0.92),zorder=7)
  stg={'C':'C阶段（测试后，未突破）','D':'D阶段' if (a['sos'] is not None and r.breakout) else 'D阶段早期（未突破AR）','E':'E阶段 上涨'}[a['stage']]
  a['stg']=stg
  ax.plot(N-1,a['last'],'*',ms=18,c='blue',mec='k',zorder=8)
  ax.annotate(f'当前位置：{stg}\n2026-10-30 收 {f2(a["last"])}',(N-1,a['last']),xytext=(-260,70 if a['last']<ylo+H*0.75 else -90),textcoords='offset points',fontsize=11,color='blue',
    arrowprops=dict(arrowstyle='->',color='blue'),bbox=dict(boxstyle='round,pad=0.3',fc='#e8f0ff',ec='blue'),zorder=9)
  ax.set_ylim(ylo-H*0.22,top); ax.set_xlim(-1,N+4); ax.grid(alpha=0.15); ax.set_ylabel('价格 Price（USD）',fontsize=11)
  av.set_ylabel('成交量(百万)',fontsize=10); av.set_ylim(0,d.volume.max()/1e6*1.15); plt.setp(ax.get_xticklabels(),visible=False)
  tk=[i for i in range(N) if (i>3 and d.date[i].month!=d.date[i-1].month)]; av.set_xticks(tk); av.set_xticklabels(d.date.dt.strftime('%Y-%m').iloc[tk],fontsize=9)
  fig.suptitle(f'{t} 日线 · 威科夫吸筹结构标注',fontsize=20,fontweight='bold',y=0.975)
  dep=(1-r.c_low_price/r.sc_price)*100; cf=conf(a); a['conf']=cf
  L=[]
  L.append(f'事件：'+('PS '+dt(a['ps'])+' '+f2(d.low[a['ps']])+'；' if a['ps'] is not None else '')+f'SC {r.sc_date} {f2(r.sc_price)}；AR {r.ar_date} {f2(r.ar_price)}；'+(f'ST {dt(a["st"])} {f2(d.low[a["st"]])}；' if a['st'] is not None else '')+(f'UA {dt(a["ua"])} {f2(d.high[a["ua"]])}；' if a['ua'] is not None else '')+f'C低点 {r.c_low_date} {f2(r.c_low_price)}'+(f'（低于SC {dep:.1f}%）' if a['spring'] else f'（高于SC {-dep:.1f}%）'))
  if a['sos'] is not None: L.append(f'突破：SOS {dt(a["sos"])} 收 {f2(d.close[a["sos"]])}（量比 {d.volume[a["sos"]]/d.vm[a["sos"]]:.1f}x）'+(f'；LPS {dt(a["lps"])} {f2(d.low[a["lps"]])}' if a['lps'] is not None else '')+f'；现价 {f2(a["last"])}，当前 {stg}。')
  else: L.append(f'未突破：现价 {f2(a["last"])}，距 AR 阻力 {f2(r.ar_price)} 还差 {(r.ar_price/a["last"]-1)*100:.1f}%，当前 {stg}；需放量站上 AR 才确认 SOS。')
  if t in SPR: q=f'形态评估：Spring 例外规则入选，C低点比SC低 {dep:.1f}%，'+('跌破幅度偏深，接近“新低延续”而非标准弹簧，' if dep>3.5 else '属浅跌破后收回，基本符合弹簧特征，')+('回撤缩量。' if r.low_vol_pullback else '但回撤未见明显缩量，形态不算标准。')
  else: q=f'形态评估：'+('C低点跌破SC后收回，按 Spring 处理；' if a['spring'] else 'C低点高于SC，为 Schematic #2 更高低点；')+('回撤缩量，量价配合较好。' if r.low_vol_pullback else '回撤未明显缩量。')
  L.append(q+f' 置信度：{cf}。')
  inv=r.c_low_price if a['sos'] is None else (d.low[a['lps']] if a['lps'] is not None else r.ar_price)
  L.append(f'失效条件：收盘跌破 {f2(inv)}'+('（C阶段低点）则吸筹结构作废；' if a['sos'] is None else ('（LPS）且跌回 AR '+f2(r.ar_price)+' 以下则突破失败；')) + f'跌破 SC {f2(r.sc_price)} 则彻底作废。')
  if 'raw' in a['src'] or 'data_1b' in a['src'] or 'CRCL_daily' in a['src']: L.append('数据来源：TradingView 导出日线（截至 2026-10-30）。仅供研究参考，不构成投资建议。')
  fig.text(0.05,0.135,'\n'.join(L),fontsize=11.5,va='top',linespacing=1.7,wrap=True)
  pdf.savefig(fig); plt.close(fig)
A={t:analyze(t) for t in ORDER}
with PdfPages('wyckoff_scan_report.pdf') as pdf:
  fig=plt.figure(figsize=(16.5,11.7)); ax=fig.add_axes([0.02,0.02,0.96,0.96]); ax.imshow(plt.imread('wyckoff_accumulation_schematic.png')); ax.axis('off'); pdf.savefig(fig); plt.close(fig)
  figs=[]
  for t in ORDER: page(A[t],None) if False else None
  # render stock pages to temp list first to get stage/conf for table
  import io
  from matplotlib.backends.backend_pdf import PdfPages as PP
  class Buf: 
    def __init__(s): s.f=[]
    def savefig(s,f): s.f.append(f)
  bufs=[]
  for t in ORDER:
    b=Buf(); plt.close=lambda f=None:None; page(A[t],b); bufs.append(b.f[0])
  fig=plt.figure(figsize=(16.5,11.7)); fig.suptitle('威科夫吸筹扫描汇总（12 只，数据截至 2026-10-30）',fontsize=20,fontweight='bold',y=0.94)
  ax=fig.add_axes([0.08,0.2,0.84,0.68]); ax.axis('off')
  rows=[[t,A[t]['stg'],'是' if A[t]['sos'] is not None else '否',f2(A[t]['last']),A[t]['conf']] for t in ORDER]
  tb=ax.table(cellText=rows,colLabels=['代码','当前阶段','是否已突破AR','现价(USD)','置信度'],loc='upper center',cellLoc='center')
  tb.auto_set_font_size(False); tb.set_fontsize(13); tb.scale(1,2.3)
  for (i,j),c in tb.get_celld().items():
    if i==0: c.set_facecolor('#dde6f5'); c.set_text_props(fontweight='bold')
  fig.text(0.08,0.12,'注：本次扫描只覆盖了 2524 只中的 1081 只；内容仅供研究参考，不构成投资建议。\nCHYM、MORN、GDDY、TRI、TYL、CEG、VRSK 为 Spring 例外规则入选（C 低点比 SC 低 2%~5%）。',fontsize=13,linespacing=1.8)
  pdf.savefig(fig)
  for f in bufs: pdf.savefig(f)
print(*[(t,A[t]['stg'],A[t]['conf']) for t in ORDER],sep='\n')
