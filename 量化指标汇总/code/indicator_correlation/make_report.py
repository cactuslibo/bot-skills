import pandas as pd,numpy as np
cats=['动量震荡','趋势均线','波动率','成交量量价','微观结构流动性','其他']
P=pd.read_csv('pairs_all.csv'); L=[]
L.append("## 四、各类相关性结果\n\n热力图左半部分是 Spearman ρ，右半部分是距离相关，两者都是 10 个标的的中位数，行列按聚类顺序排列。\n\n### 4.0 总览\n")
L.append("| 类别 | 序列数 | 指标对数 | 冗余 ≥0.9 | 强相关 0.7–0.9 | 五个子样本都稳定 | 非线性提示 | 第一主成分占比 | 簇数 | 代表 VIF 最大值 | bootstrap 区间宽度中位数 |\n|---|---|---|---|---|---|---|---|---|---|---|")
stab={}
for c in cats:
    g=P[P.类别==c]; a=g.spearman_med.abs(); C=pd.read_csv(f'clusters_{c}.csv'); v=pd.read_csv(f'vif_reps_{c}.csv',index_col=0).iloc[:,0]
    pc=pd.read_csv(f'pca_explained_{c}.csv').iloc[0,1]
    L.append(f"|{c}|{len(C)}|{len(g)}|{(a>=.9).sum()}|{((a>=.7)&(a<.9)).sum()}|{g.稳定.sum()}|{g.非线性提示.sum()}|{pc:.1%}|{C.代表指标.nunique()}|{v.max():.2f}（{v.idxmax()}）|{(g.bootCI10_hi-g.bootCI10_lo).median():.3f}|")
    r=g[a>=.9][['牛','熊','震荡','IS_2011_2018','OOS_2019_2026']].abs()
    if len(r): m=r.min(); stab[c]=f"{m.min():.3f}（{m.idxmin()}）"
open('_stab.txt','w').write(repr(stab)); print(stab)
open('_tab.md','w').write('\n'.join(L)+'\n')
out=[]
for c,g in P.groupby('类别',sort=False):
    g=g[g.spearman_med.abs()>=0.9].copy(); g['a']=g.spearman_med.abs(); g=g.sort_values('a',ascending=False)
    out.append(f"\n**{c}**（|ρ|≥0.9 共 {len(g)} 对；完整列表见 `pairs_{c}.csv`）\n")
    if not len(g): out.append("无。\n"); continue
    out.append("| A | B | ρ中位数 | 10 标的最小值 | 10 标的 bootstrap 95% 区间 | 距离相关 | Kendall τ(SPY) | 熊市 ρ | 样本外 ρ | 五个子样本都稳定 |\n|---|---|---|---|---|---|---|---|---|---|")
    for _,r in g.head(15).iterrows():
        out.append(f"|{r.A}|{r.B}|{r.spearman_med:.3f}|{r.spearman_min:.3f}|[{r.bootCI10_lo:.3f}, {r.bootCI10_hi:.3f}]|{r.dcor_med:.3f}|{r.kendall_SPY:.3f}|{r.熊:.3f}|{r.OOS_2019_2026:.3f}|{'是' if r.稳定 else '否'}|")
open('_pairs.md','w').write('\n'.join(out)+'\n')
cl=[]
for c in cats:
    C=pd.read_csv(f'clusters_{c}.csv'); cl.append(f"\n**{c}**（{len(C)} 条序列 → {C.代表指标.nunique()} 簇）\n\n| 代表指标 | 簇成员 |\n|---|---|")
    for r,gg in C.groupby('代表指标'): cl.append(f"|{r}|{', '.join(gg.指标)}|")
open('_cl.md','w').write('\n'.join(cl)+'\n')
G=pd.read_csv('global_clusters.csv'); X=pd.read_csv('global_crosscat_pairs.csv')
gl=[f"全局共 {len(G)} 条序列，聚成 {G.簇号.nunique()} 簇，其中 {(G.groupby('簇号').size()==1).sum()} 簇只有一个成员。跨类别的 |ρ|≥0.7 指标对共 {len(X)} 对，其中 |ρ|≥0.9 的有 {(X.spearman_med.abs()>=0.9).sum()} 对（`global_crosscat_pairs.csv`）。\n\n**跨类别的多成员簇：**\n\n| 代表指标 | 簇大小 | 涉及类别数 | 成员 |\n|---|---|---|---|"]
for k,gg in G[G.跨类别数>1].groupby('簇号'):
    gl.append(f"|{gg.代表指标.iloc[0]}|{len(gg)}|{gg.跨类别数.iloc[0]}|{', '.join(gg.指标)}|")
gl.append("\n**跨类别 |ρ| 最高的 15 对：**\n\n| A | B | ρ中位数 |\n|---|---|---|")
for _,r in X.head(15).iterrows(): gl.append(f"|{r.A}|{r.B}|{r.spearman_med:.4f}|")
open('_gl.md','w').write('\n'.join(gl)+'\n')
