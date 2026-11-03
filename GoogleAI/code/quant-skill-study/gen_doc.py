import pandas as pd, glob, sys
sys.path.insert(0,'.'); from gen_doc_data import D
C='/workspace/indicator_correlation/'
cl=pd.concat([pd.read_csv(f).assign(类=f.split('clusters_')[1][:-4]) for f in glob.glob(C+'clusters_*.csv')])
cl['size']=cl.groupby(['类','簇号'])['指标'].transform('count')
cl=cl.set_index('指标')
pr=pd.concat([pd.read_csv(f) for f in glob.glob(C+'pairs_*.csv') if 'pairs_all' not in f])
red=pr[pr['等级'].astype(str).str.startswith('冗余')]
miss=[k for d in D for k in d[7] if k not in cl.index]; print('missing',miss)
res=pd.read_csv('ndx_top_study/results.csv',index_col=0)
def ev(keys):
    if not keys: return '无回测，仅有相关性分析——且本项未进入相关性计算（缺数据或不适合），无簇信息。'
    parts=[]
    for k in keys:
        r=cl.loc[k]; rep=r['代表指标']; tag='本身即簇代表' if rep==k else f'代表为 {rep}'
        s=f'`{k}`：{r["类"]}类第 {r["簇号"]} 簇（{r["size"]} 条序列，{tag}，符号 {r["与代表符号"]}）'
        rr=red[(red.A==k)|(red.B==k)].reindex(columns=['A','B','spearman_med']).sort_values('spearman_med',key=abs,ascending=False)
        if len(rr):
            ps=[(b if a==k else a)+f'(ρ={x:.2f})' for a,b,x in rr.head(3).values]
            s+=f'；冗余对(|ρ|≥0.9) {len(rr)} 个：'+'、'.join(ps)
        parts.append(s)
    return '无回测，仅有相关性分析。'+'；'.join(parts)+'。'
L=[]
cur=None; cats={'动量/震荡':'一','趋势':'二','波动率':'三','成交量/量价':'四','市场宽度/情绪':'五','微观结构/流动性':'六','其他':'七'}
for cat,i,n,f,p,t,u,k in D:
    if cat!=cur:
        cur=cat; L.append(f'\n### 2.{cats[cat]} {cat}（{sum(1 for d in D if d[0]==cat)} 项）\n')
    L.append(f'**{cats[cat]}-{i}. {n}**\n- 公式/定义：{f}\n- 常用参数：{p}\n- 常用阈值：{t}\n- 适用用途：{u}\n- 回测证据：{ev(k)}\n')
open('_body.md','w').write('\n'.join(L))
open('_res.md','w').write(res.to_markdown())
