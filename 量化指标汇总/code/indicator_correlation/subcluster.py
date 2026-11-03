# 第九节 46 成员大簇的子聚类：平均连接 vs Ward；并给所有簇表加“与代表符号”列
import pandas as pd,numpy as np
from scipy.cluster.hierarchy import linkage,fcluster
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score
G=pd.read_csv('global_clusters.csv'); M=pd.read_csv('global_spearman_median.csv',index_col=0)
big=G.groupby('簇号').size().idxmax(); mem=G[G.簇号==big].指标.tolist(); print(len(mem))
A=M.loc[mem,mem].abs().values; D=1-A; np.fill_diagonal(D,0); cd=squareform(D,checks=False)
Za=linkage(cd,'average'); Zw=linkage(np.sqrt(2*cd),'ward')  # Ward 用 √(2(1−|ρ|))，近似欧氏
rows=[]
for k in [3,4,5,6]:
    la=fcluster(Za,k,'maxclust'); lw=fcluster(Zw,k,'maxclust'); rows.append((k,adjusted_rand_score(la,lw)))
ari=pd.DataFrame(rows,columns=['簇数k','ARI(平均连接 vs Ward)']); ari.to_csv('bigcluster_ARI.csv',index=False); print(ari)
la=fcluster(Za,0.15,'distance'); K=len(set(la)); lw=fcluster(Zw,K,'maxclust')
out=pd.DataFrame({'指标':mem,'平均连接子簇(切0.15)':la,f'Ward子簇(k={K})':lw})
rep={}
for s in set(la):
    m=[i for i in range(len(mem)) if la[i]==s]; r=max(m,key=lambda i:A[i,m].mean()); 
    for i in m: rep[mem[i]]=mem[r]
out['子簇代表']=out.指标.map(rep); out['与子簇代表符号']=[('−' if M.loc[a,rep[a]]<0 else '+') for a in out.指标]
out['子簇内平均|ρ|']=[A[mem.index(a),[mem.index(b) for b in mem if rep[b]==rep[a]]].mean().round(3) for a in out.指标]
out.sort_values(['平均连接子簇(切0.15)','指标']).to_csv('bigcluster_subclusters.csv',index=False)
print(K, adjusted_rand_score(la,lw)); print(out.sort_values('平均连接子簇(切0.15)').to_string())
# 符号列
G['与代表符号']=[('−' if M.loc[a,r]<0 else '+') for a,r in zip(G.指标,G.代表指标)]; G.to_csv('global_clusters.csv',index=False)
for c in ['动量震荡','趋势均线','波动率','成交量量价','微观结构流动性','其他']:
    C=pd.read_csv(f'clusters_{c}.csv'); S=pd.read_csv(f'spearman_median_{c}.csv',index_col=0)
    C['与代表符号']=[('−' if S.loc[a,r]<0 else '+') for a,r in zip(C.指标,C.代表指标)]; C.to_csv(f'clusters_{c}.csv',index=False)
