import pandas as pd,numpy as np
exec(open("test3.py").read().split("rows=[]; ex={}")[0])
exec(open("labels_bis.py").read())
F=feats(2008,2025,[2009,2019,2023]); F=F[F.sic.isin(["3674","3559","3672"])|F.ticker.isin(B)]
F=F[~F.ticker.isin(EXCL)]
F["nar"]=F.ticker.map(lambda t:1 if t in B else (0 if t in S_narrow else np.nan))
F["wide"]=F.ticker.map(lambda t:1 if t in B else 0)
out=[]
for gk in ["SIC3","pooled"]:
  G=pct(F,"GM_trough",gk)
  for m in ["GM_trough_pct","GM_trough","GM","OM_floor","GM_ret","UP_dGM","CLR"]:
    for lab in ["nar","wide"]:
      if m!="GM_trough_pct" and gk=="SIC3": continue
      s=stats(G,m,lab)
      if s: out.append(dict(group=gk,metric=m,label=lab,**s))
R=pd.DataFrame(out); R.to_csv("results_bis.csv",index=False); print(R.round(2).to_string())
print(F.sort_values("GM_trough",ascending=False)[["ticker","sic","wide","nar","GM","GM_trough"]].round(3).head(15).to_string())
print("n",len(F))
