import pandas as pd,numpy as np
exec(open("test2.py").read().split("W1=feats")[0])
P0=P.copy()
print("universe tickers",P.ticker.nunique(),"labels in panel B",sorted(set(P.ticker)&B),"S",sorted(set(P.ticker)&S))
def run(gfun,tag):
  P["grp"]=gfun(P)
  W1=feats(P[(P.year>=2008)&(P.year<=2016)]); W2=feats(P[(P.year>=2017)&(P.year<=2025)])
  a1=auc(W1,"GM_trough_pct")[0]; a2=auc(W2,"GM_trough_pct")[0]
  y=W2.dropna(subset=["lab"]); pr=y[y.GM_trough_pct>=0.4545]
  print(tag,"AUC",round(a1,3),round(a2,3),"OOS prec",round((pr.lab==1).mean(),2),"rec",round((y[y.lab==1].GM_trough_pct>=0.4545).mean(),2))
  return W1,W2
W1,W2=run(lambda d:d.sic.astype(str).str[:3],"SIC3")
run(lambda d:d.sic.astype(str).str[:2],"SIC2")
run(lambda d:d.sic.astype(str),"SIC4")
run(lambda d:pd.Series("all",index=d.index),"pooled")
P["grp"]=P.sic.astype(str).str[:3]
for n,W in [("W1",W1),("W2",W2)]:
  x=W[W.lab.notna()][["ticker","grp","lab","GM_trough","GM_trough_pct"]].sort_values("GM_trough_pct"); print(n);print(x.round(3).to_string())
  print(n,"group sizes",W.groupby("grp").size().to_dict())
# bootstrap CI W2 & W1
rng=np.random.default_rng(0)
for n,W in [("W1",W1),("W2",W2)]:
  x=W.dropna(subset=["lab","GM_trough_pct"]);b=x[x.lab==1].GM_trough_pct.values;s=x[x.lab==0].GM_trough_pct.values
  bs=[]
  for _ in range(5000):
    bb=rng.choice(b,len(b));ss=rng.choice(s,len(s));bs.append(np.mean((bb[:,None]>ss[None])+0.5*(bb[:,None]==ss[None])))
  a=np.mean((b[:,None]>s[None])+0.5*(b[:,None]==s[None])); q=len(b);r=len(s)
  Q1=a/(2-a);Q2=2*a*a/(1+a);se=np.sqrt((a*(1-a)+(q-1)*(Q1-a*a)+(r-1)*(Q2-a*a))/(q*r))
  print(n,"nB",q,"nS",r,"AUC",round(a,3),"boot95",np.percentile(bs,[2.5,97.5]).round(3),"HanleyMcNeil SE",round(se,3))
# years per firm
for n,lo,hi in [("W1",2008,2016),("W2",2017,2025)]:
  c=P[(P.year>=lo)&(P.year<=hi)].groupby("ticker").gm.count(); print(n,"firms with <8 GM years among features:",(c<8).sum(),"of",len(c))
