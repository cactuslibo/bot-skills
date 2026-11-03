import yfinance as yf, pandas as pd, numpy as np
B=["ASML","TSM","NVDA","KLAC","LRCX","CDNS","SNPS","MCO","V","LONN.SW","TMO","SPGI"]
N=["2317.TW","JBL","FLEX","MU","WDC","CLS","SANM","STX"]
rows=[]
for t in B+N:
  try:
    tk=yf.Ticker(t); f=tk.income_stmt; b=tk.balance_sheet
    rev=f.loc["Total Revenue"]; gp=f.loc["Gross Profit"] if "Gross Profit" in f.index else None
    oi=f.loc["Operating Income"]
    gm=(gp/rev).dropna() if gp is not None else pd.Series(dtype=float)
    om=(oi/rev).dropna()
    ic=(b.loc["Invested Capital"] if "Invested Capital" in b.index else None)
    roic=(oi*0.79/ic).dropna() if ic is not None else pd.Series(dtype=float)
    ar=b.loc["Accounts Receivable"] if "Accounts Receivable" in b.index else None
    ap=b.loc["Accounts Payable"] if "Accounts Payable" in b.index else None
    cogs=f.loc["Cost Of Revenue"] if "Cost Of Revenue" in f.index else None
    dpo_dso=((ap/cogs*365)-(ar/rev*365)).dropna().mean() if ar is not None and ap is not None and cogs is not None else np.nan
    rows.append(dict(t=t,grp="B" if t in B else "N",GM=gm.mean(),GM_sd=gm.std(),OM=om.mean(),OM_min=om.min(),ROIC=roic.mean(),ROIC_min=roic.min(),DPO_DSO=dpo_dso,yrs=len(om)))
  except Exception as e: rows.append(dict(t=t,err=str(e)[:60]))
d=pd.DataFrame(rows); pd.set_option("display.width",200); print(d.round(3).to_string())
d.to_csv("data.csv",index=False)
g=d.groupby("grp")[["GM","GM_sd","OM","OM_min","ROIC","ROIC_min","DPO_DSO"]].median(); print(g.round(3))
from itertools import product
for c in ["GM","OM","OM_min","ROIC","ROIC_min","DPO_DSO"]:
  x=d.dropna(subset=[c]); bb=x[x.grp=="B"][c]; nn=x[x.grp=="N"][c]
  auc=np.mean([1.0*(i>j)+0.5*(i==j) for i,j in product(bb,nn)]); print(c,"AUC",round(auc,3))
c="GM_sd"; x=d.dropna(subset=[c]); bb=x[x.grp=="B"][c]; nn=x[x.grp=="N"][c]
print("GM_sd AUC(lower=B)",round(np.mean([1.0*(i<j) for i,j in product(bb,nn)]),3))
