import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fs=[f.name for f in fm.fontManager.ttflist if any(k in f.name for k in ['Noto Sans CJK','WenQuanYi','SimHei','Source Han'])]
if fs: plt.rcParams['font.sans-serif']=[fs[0]]
plt.rcParams['axes.unicode_minus']=False
L=['IP/研发设计','原材料\n(ABS/PP/PVC/色母)','模具/零部件','制造代工\n(加工费+利润)','物流+关税','品牌商\n(营销+管理+利润)','渠道零售','售后/退货']
V=[5,8,3,9,5,25,43,2]
fig,ax=plt.subplots(figsize=(12,6));b=0
for i,(l,v) in enumerate(zip(L,V)):
    ax.bar(i,v,bottom=b,color='C%d'%i);ax.text(i,b+v/2,f'{v}元',ha='center',va='center',fontsize=11,color='white',weight='bold');b+=v
ax.bar(len(L),100,color='gray');ax.text(len(L),50,'100元',ha='center',color='white',weight='bold')
ax.set_xticks(range(len(L)+1));ax.set_xticklabels(L+['终端零售价'],fontsize=9)
ax.set_title('一件100元塑料玩具的价格瀑布（美国商超口径，中国/越南制造；估算，C级）');ax.set_ylabel('元')
plt.tight_layout();plt.savefig('waterfall.png',dpi=150)
print(fs[:1])
