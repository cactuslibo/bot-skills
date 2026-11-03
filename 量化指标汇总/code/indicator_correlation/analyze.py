import pandas as pd,numpy as np,dcor,warnings,matplotlib; matplotlib.use('Agg'); warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt; from matplotlib import font_manager
from scipy.cluster.hierarchy import linkage,fcluster,dendrogram; from scipy.spatial.distance import squareform; from scipy.stats import kendalltau
import indicators as I
fs=[f.name for f in font_manager.fontManager.ttflist if any(k in f.name for k in ['Noto Sans CJK','WenQuanYi','Noto Sans SC'])]
if fs: plt.rcParams['font.sans-serif']=[fs[0]]; plt.rcParams['axes.unicode_minus']=False
d=pd.read_pickle('raw.pkl'); TK=['SPY','QQQ','IWM','DIA','AAPL','MSFT','JPM','XOM','JNJ','PG']
spy=d['SPY']['Close']; vix=d['^VIX']['Close']; irx=pd.read_pickle('irx.pkl').squeeze()
ma=spy.rolling(200).mean(); slope=ma.diff(20)
reg=pd.Series('震荡',spy.index); reg[(spy>ma)&(slope>0)]='牛'; reg[(spy<ma)&(slope<0)]='熊'; reg[ma.isna()]=np.nan
reg.to_csv('regime_SPY200.csv')
ALL={t:I.compute(d[t].dropna(),spy,vix,irx) for t in TK}
cats=list(ALL['SPY'].keys()); WARM=260; SPLIT='2019-01-01'; rng=np.random.default_rng(0)
from scipy.stats import rankdata
def bb_ci_median(Xs,B=200,L=20):
    # 10 标的共同日期上做移动块自助（各标的用同一组块，保留截面相关），每次重抽样后重新排秩，
    # 计算各标的 Spearman 再取中位数，得到“10 标的中位数 ρ”的 95% 区间
    idx0=Xs[0].index
    for X in Xs[1:]: idx0=idx0.intersection(X.index)
    V=[X.loc[idx0].values for X in Xs]; n=len(idx0); out=[]
    for _ in range(B):
        st=rng.integers(0,n-L,n//L+1); idx=np.concatenate([np.arange(s,s+L) for s in st])[:n]
        rs=[]
        for v in V:
            R=rankdata(v[idx],axis=0)
            with np.errstate(all='ignore'): rs.append(np.corrcoef(R.T))
        out.append(np.nanmedian(rs,0))
    out=np.array(out); return np.nanpercentile(out,2.5,0),np.nanpercentile(out,97.5,0)
summary=[]
for cat in cats:
    cols=ALL['SPY'][cat].columns; rho=[];dc=[];XL=[];sub={'牛':[],'熊':[],'震荡':[],'IS':[],'OOS':[]}
    for t in TK:
        X=ALL[t][cat].iloc[WARM:].dropna(axis=1,how='all').reindex(columns=cols).dropna()
        rho.append(X.corr('spearman').values); XL.append(X)
        Xs=X.iloc[::3]  # 距离相关：每 3 日取一点以控制计算量
        m=np.eye(len(cols))
        for i in range(len(cols)):
            for j in range(i+1,len(cols)): m[i,j]=m[j,i]=dcor.distance_correlation(Xs.iloc[:,i].values,Xs.iloc[:,j].values,method='avl')
        dc.append(m)
        rg=reg.reindex(X.index)
        for s in ['牛','熊','震荡']: sub[s].append(X[rg==s].corr('spearman').values)
        sub['IS'].append(X[:SPLIT].corr('spearman').values); sub['OOS'].append(X[SPLIT:].corr('spearman').values)
    rho=np.array(rho); med=np.nanmedian(rho,0); q25,q75=np.nanpercentile(rho,25,0),np.nanpercentile(rho,75,0)
    dcm=np.nanmedian(dc,0); S={k:np.nanmedian(v,0) for k,v in sub.items()}
    Xspy=ALL['SPY'][cat].iloc[WARM:].dropna(); lo,hi=bb_ci_median(XL)
    pd.DataFrame(med,cols,cols).round(4).to_csv(f'spearman_median_{cat}.csv')
    pd.DataFrame(dcm,cols,cols).round(4).to_csv(f'dcor_median_{cat}.csv')
    # 聚类
    A=np.nan_to_num(np.abs(med)); D=1-A; np.fill_diagonal(D,0); Z=linkage(squareform(D,checks=False),'average')
    cl=fcluster(Z,0.3,'distance')  # 簇内平均 |ρ|≥0.7
    reps={}
    for k in np.unique(cl):
        mem=[i for i in range(len(cols)) if cl[i]==k]
        rep=max(mem,key=lambda i:A[i,mem].mean()) if len(mem)>1 else mem[0]
        for i in mem: reps[cols[i]]=(k,cols[rep])
    pd.DataFrame([(c_,*reps[c_]) for c_ in cols],columns=['指标','簇号','代表指标']).to_csv(f'clusters_{cat}.csv',index=False)
    # 代表指标 VIF
    rc=sorted(set(v[1] for v in reps.values()))
    if len(rc)>1:
        Rr=Xspy[rc].corr('spearman').fillna(0).values.copy(); np.fill_diagonal(Rr,1); vif=np.diag(np.linalg.pinv(Rr))
        pd.Series(vif,rc,name='VIF_SPY_rank_(Beta/Corr在SPY上为常数,置0)').round(2).to_csv(f'vif_reps_{cat}.csv')
        ev=np.linalg.eigvalsh(np.nan_to_num(med,nan=0)+np.diag(np.isnan(np.diag(med))*1.0))[::-1]; pd.Series(ev/ev.sum()).round(4).to_csv(f'pca_explained_{cat}.csv')
    rows=[]
    for i in range(len(cols)):
        for j in range(i+1,len(cols)):
            a,b=cols[i],cols[j]; kt=np.nan
            if abs(med[i,j])>=0.7: kt=kendalltau(Xspy[a].values[::2],Xspy[b].values[::2])[0]
            # 方向一致率：相对 252 日滚动中位数的符号（仅用历史，避免前视）
            sa=np.sign(Xspy[a]-Xspy[a].rolling(252).median()); sb=np.sign(Xspy[b]-Xspy[b].rolling(252).median()); mk=sa.notna()&sb.notna()&(sa!=0)&(sb!=0)
            agree=(sa[mk]==sb[mk]).mean()
            rows.append(dict(类别=cat,A=a,B=b,spearman_med=med[i,j],spearman_q25=q25[i,j],spearman_q75=q75[i,j],spearman_min=np.nanmin(rho[:,i,j]),spearman_max=np.nanmax(rho[:,i,j]),
              bootCI10_lo=lo[i,j],bootCI10_hi=hi[i,j],kendall_SPY=kt,dcor_med=dcm[i,j],牛=S['牛'][i,j],熊=S['熊'][i,j],震荡=S['震荡'][i,j],
              IS_2011_2018=S['IS'][i,j],OOS_2019_2026=S['OOS'][i,j],方向一致率_SPY=agree,同簇=reps[a][0]==reps[b][0]))
    P=pd.DataFrame(rows); P['abs']=P.spearman_med.abs()
    P['等级']=np.select([P['abs']>=0.9,P['abs']>=0.7],['冗余(≥0.9)','强相关(0.7–0.9)'],'')
    P['稳定']=P[['牛','熊','震荡','IS_2011_2018','OOS_2019_2026']].abs().min(axis=1)>=0.7
    P['非线性提示']=(P.dcor_med-P['abs'])>=0.2
    P.sort_values('abs',ascending=False).drop(columns='abs').round(4).to_csv(f'pairs_{cat}.csv',index=False); summary.append(P)
    # 热力图（按聚类顺序）
    order=dendrogram(Z,no_plot=True)['leaves']; n=len(cols)
    fig,ax=plt.subplots(1,2,figsize=(max(10,n*0.55)*2,max(8,n*0.5)))
    for k_,(M_,tt) in enumerate([(med,'Spearman ρ（10 标的中位数）'),(dcm,'距离相关（10 标的中位数）')]):
        im=ax[k_].imshow(M_[np.ix_(order,order)],cmap='RdBu_r' if k_==0 else 'viridis',vmin=-1 if k_==0 else 0,vmax=1)
        ax[k_].set_xticks(range(n)); ax[k_].set_yticks(range(n)); lab=[cols[i] for i in order]
        ax[k_].set_xticklabels(lab,rotation=90,fontsize=7); ax[k_].set_yticklabels(lab,fontsize=7); ax[k_].set_title(f'{cat}：{tt}'); plt.colorbar(im,ax=ax[k_],fraction=.04)
    plt.tight_layout(); plt.savefig(f'heatmap_{cat}.png',dpi=110); plt.close()
    print(cat,'done',flush=True)
pd.concat(summary).drop(columns='abs').round(4).to_csv('pairs_all.csv',index=False)

# ---------- 跨类别全局聚类 ----------
G=[]
for t in TK:
    X=pd.concat([ALL[t][c].add_prefix(c[:2]+':') for c in cats],axis=1).iloc[WARM:]
    G.append(X)
gcols=G[0].columns
gr=[]
for X in G:
    X=X.reindex(columns=gcols); X=X.loc[:,X.std()>0]; X=X.dropna(); gr.append(X.corr('spearman').reindex(index=gcols,columns=gcols).values)
gmed=np.nanmedian(gr,0); pd.DataFrame(gmed,gcols,gcols).round(4).to_csv('global_spearman_median.csv')
A=np.nan_to_num(np.abs(gmed)); D=1-A; np.fill_diagonal(D,0); Z=linkage(squareform(D,checks=False),'average'); cl=fcluster(Z,0.3,'distance')
rows=[]
for k in np.unique(cl):
    mem=[i for i in range(len(gcols)) if cl[i]==k]; rep_=max(mem,key=lambda i:A[i,mem].mean())
    for i in mem: rows.append((gcols[i],k,gcols[rep_],len(mem),len(set(gcols[m].split(':')[0] for m in mem))))
pd.DataFrame(rows,columns=['指标','簇号','代表指标','簇大小','跨类别数']).sort_values(['簇号','指标']).to_csv('global_clusters.csv',index=False)
cp=[]
for i in range(len(gcols)):
    for j in range(i+1,len(gcols)):
        if gcols[i].split(':')[0]!=gcols[j].split(':')[0] and abs(gmed[i,j])>=0.7: cp.append((gcols[i],gcols[j],gmed[i,j]))
pd.DataFrame(cp,columns=['A','B','spearman_med']).assign(a=lambda x:x.spearman_med.abs()).sort_values('a',ascending=False).drop(columns='a').round(4).to_csv('global_crosscat_pairs.csv',index=False)
order=dendrogram(Z,no_plot=True)['leaves']; n=len(gcols)
fig,ax=plt.subplots(figsize=(30,28)); im=ax.imshow(gmed[np.ix_(order,order)],cmap='RdBu_r',vmin=-1,vmax=1)
ax.set_xticks(range(n)); ax.set_yticks(range(n)); lab=[gcols[i] for i in order]; ax.set_xticklabels(lab,rotation=90,fontsize=6); ax.set_yticklabels(lab,fontsize=6)
ax.set_title('全局（跨类别）Spearman ρ（10 标的中位数）'); plt.colorbar(im,fraction=.03); plt.tight_layout(); plt.savefig('heatmap_global.png',dpi=90); plt.close()
print('global done', n, len(np.unique(cl)))
