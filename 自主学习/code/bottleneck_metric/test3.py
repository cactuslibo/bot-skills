import pandas as pd,numpy as np
rng=np.random.default_rng(0)
P=pd.read_csv("panel.csv"); P=P[(P.rev>0)&P.ticker.notna()].copy()
P["gm"]=P.gp/P.rev; P["om"]=P.oi/P.rev; P["clr"]=P.cl/P.rev
EXP_B={"KLAC","LRCX","AMAT","TER","FORM","OLED","NVDA","AVGO","ASML","TSM"}
EXP_S={"JBL","FLEX","SANM","PLXS","BHE","KTCC","KE","TTMI","AMKR","MU","PENG","DQ","ARRY","SEDG","NTGR","CRSR","LOGI"}
L=pd.read_csv("labels_v2.csv").set_index("ticker").lab
DOWN={"W1":(2008,2016,[2009]),"W2":(2017,2025,[2019,2023]),"ALL":(2008,2025,[2009,2019,2023])}
def feats(lo,hi,down):
  w=P[(P.year>=lo)&(P.year<=hi)]; out=[]
  for t,g in w.groupby("ticker"):
    g=g.dropna(subset=["gm"])
    if len(g)<8 or not set(down)&set(g.year): continue   # 必改3：≥8年且覆盖下行年
    up=g.rev.pct_change()>0.10
    out.append(dict(ticker=t,sic=str(g.sic.iloc[0]),GM=g.gm.mean(),GM_trough=g.gm.min(),OM_floor=g.om.min(),
      GM_ret=g.gm.min()/g.gm.max(),UP_dGM=g.gm.diff()[up].mean(),CLR=g.clr.mean()))
  return pd.DataFrame(out)
GROUPS={"SIC4(N>=10)":lambda F:F.sic,"SIC3":lambda F:F.sic.str[:3],"SIC2":lambda F:F.sic.str[:2],"pooled":lambda F:pd.Series("all",index=F.index)}
def pct(F,m,gk):
  F=F.copy(); F["g"]=GROUPS[gk](F); n=F.groupby("g").ticker.transform("count")
  F[m+"_pct"]=F.groupby("g")[m].rank(pct=True)
  if gk.startswith("SIC4"): F.loc[n<10,m+"_pct"]=np.nan   # 必改2：同业<10 家不评分
  return F
def stats(x,m,lab):
  x=x.dropna(subset=[m,lab]); b=x[x[lab]==1][m].values; s=x[x[lab]==0][m].values
  if len(b)<2 or len(s)<2: return None
  A=lambda b,s:np.mean((b[:,None]>s[None])+0.5*(b[:,None]==s[None]))
  a=A(b,s); bs=[A(rng.choice(b,len(b)),rng.choice(s,len(s))) for _ in range(2000)]
  q1=a/(2-a);q2=2*a*a/(1+a);se=np.sqrt(max(a*(1-a)+(len(b)-1)*(q1-a*a)+(len(s)-1)*(q2-a*a),0)/(len(b)*len(s)))
  o=dict(nB=len(b),nS=len(s),AUC=a,boot_lo=np.percentile(bs,2.5),boot_hi=np.percentile(bs,97.5),HM_lo=max(0,a-1.96*se),HM_hi=min(1,a+1.96*se))
  if m.endswith("_pct"):
    for th in (0.5,0.75):   # 必改4：固定阈值
      tp=(b>=th).sum(); fp=(s>=th).sum()
      o[f"rec@{th}"]=tp/len(b); o[f"FDR@{th}"]=fp/(tp+fp) if tp+fp else np.nan
  return o
rows=[]; ex={}
for wn,(lo,hi,dn) in DOWN.items():
  F=feats(lo,hi,dn); F["exp"]=F.ticker.map(lambda t:1 if t in EXP_B else (0 if t in EXP_S else np.nan)); F["edgar"]=F.ticker.map(L)
  ex[wn]=F
  for gk in GROUPS:
    G=pct(F,"GM_trough",gk); G=pct(G,"GM_ret",gk); G=pct(G,"OM_floor",gk)
    for m in ["GM_trough_pct","GM_ret_pct","OM_floor_pct"]+(["GM_trough","GM","OM_floor","UP_dGM","CLR"] if gk=="pooled" else []):
      for lab in ["exp","edgar"]:
        s=stats(G,m,lab)
        if s: rows.append(dict(window=wn,group=gk,metric=m,label=lab,**s))
    if gk=="SIC3":
      for g in ["737","382"]:
        z=G[G.sic.str[:3]==g]; rows.append(dict(window=wn,group=gk,metric=f"{g}组被判≥P75占比",label="-",AUC=(z.GM_trough_pct>=0.75).mean(),nB=len(z)))
R=pd.DataFrame(rows); R.to_csv("results_v3.csv",index=False)
pd.set_option("display.width",250); print(R.round(2).to_string())
for wn in ex: print(wn,"n firms",len(ex[wn]),"SIC4 sizes>=10:",{k:v for k,v in ex[wn].sic.value_counts().items() if v>=10})
print(ex["ALL"][ex["ALL"].exp.notna()][["ticker","sic","exp","GM_trough","GM_ret"]].round(3).sort_values("GM_trough").to_string())
