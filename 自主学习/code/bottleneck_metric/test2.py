import pandas as pd,numpy as np
from itertools import product
P=pd.read_csv("panel.csv"); P=P[P.rev>0]
P["gm"]=P.gp/P.rev; P["om"]=P.oi/P.rev; P["clr"]=P.cl/P.rev; P["drr"]=P.dr/P.rev
# 事前、非利润率标签（依据：细分份额/单一来源/替代难度的公开常识，待逐条核实）
B={"KLAC","LRCX","AMAT","TER","FORM","OLED","NVDA","AVGO","ASML"}
S={"JBL","FLEX","SANM","PLXS","BHE","KTCC","KE","TTMI","AMKR","MU","PENG","DQ","MAXNQ","ARRY","SEDG","NTGR","CRSR","LOGI","SMCI"}
P["lab"]=P.ticker.map(lambda t:1 if t in B else (0 if t in S else np.nan))
P["grp"]=P.sic.astype(str).str[:3]
def feats(w):
  out=[]
  for (c,t),g in w.groupby(["cik","ticker"],dropna=False):
    g=g.sort_values("year")
    if len(g)<5 or g.gm.isna().sum()>2: continue
    gr=g.rev.pct_change(); up=g[gr>0.10]; dg=g.gm.diff(); do=g.om.diff()
    out.append(dict(ticker=t,grp=g.grp.iloc[0],lab=g.lab.iloc[0],GM=g.gm.mean(),OM=g.om.mean(),OM_floor=g.om.min(),
      GM_ret=g.gm.min()/g.gm.max() if g.gm.max()>0 else np.nan,GM_trough=g.gm.min(),
      UP_dGM=dg[gr>0.10].mean(),UP_lev=(do-dg)[gr>0.10].mean(),CLR=g.clr.mean(),DRR=g.drr.mean()))
  F=pd.DataFrame(out)
  for m in ["OM_floor","GM_ret","GM_trough","GM","OM"]: F[m+"_pct"]=F.groupby("grp")[m].rank(pct=True)
  return F
def auc(F,m):
  x=F.dropna(subset=[m,"lab"]); b=x[x.lab==1][m]; s=x[x.lab==0][m]
  if len(b)<2 or len(s)<2: return np.nan,len(b),len(s)
  return np.mean([1.0*(i>j)+0.5*(i==j) for i,j in product(b,s)]),len(b),len(s)
W1=feats(P[(P.year>=2008)&(P.year<=2016)]); W2=feats(P[(P.year>=2017)&(P.year<=2025)])
ms=["GM","OM","OM_floor","GM_trough","GM_ret","OM_floor_pct","GM_ret_pct","GM_trough_pct","UP_dGM","UP_lev","CLR","DRR"]
res=[]
for m in ms:
  a1=auc(W1,m); a2=auc(W2,m)
  # 样本内校准阈值（W1 约登指数），样本外应用 W2
  x=W1.dropna(subset=[m,"lab"]); best=(None,-9)
  for th in x[m].unique():
    tpr=(x[x.lab==1][m]>=th).mean(); fpr=(x[x.lab==0][m]>=th).mean()
    if tpr-fpr>best[1]: best=(th,tpr-fpr)
  y=W2.dropna(subset=[m,"lab"]); th=best[0]
  if th is not None and len(y):
    pr=y[y[m]>=th]; prec=(pr.lab==1).mean() if len(pr) else np.nan; rec=(y[y.lab==1][m]>=th).mean()
  else: prec=rec=np.nan
  res.append(dict(metric=m,AUC_08_16=a1[0],nB1=a1[1],nS1=a1[2],AUC_17_25=a2[0],nB2=a2[1],nS2=a2[2],th_W1=th,OOS_prec=prec,OOS_rec=rec))
R=pd.DataFrame(res); pd.set_option("display.width",250); print(R.round(3).to_string())
R.to_csv("oos_results.csv",index=False)
cols=["ticker","lab","GM","OM_floor","GM_ret","GM_ret_pct","OM_floor_pct","UP_dGM","CLR"]
print(W1[W1.lab.notna()][cols].round(3).sort_values("GM_ret").to_string())
print(W2[W2.lab.notna()][cols].round(3).sort_values("GM_ret").to_string())
W1.to_csv("feat_2008_2016.csv",index=False); W2.to_csv("feat_2017_2025.csv",index=False)
# 软件/生命科学工具假阳性检查
for nm,W in [("W1",W1),("W2",W2)]:
  for g in ["737","382"]:
    z=W[W.grp==g]; print(nm,g,"n",len(z),"GM_ret>=0.85 占比",round((z.GM_ret>=0.85).mean(),2),"OM_floor>=0.2 占比",round((z.OM_floor>=0.2).mean(),2))
