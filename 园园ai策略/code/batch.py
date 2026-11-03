import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from siji_1x import run
T="XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY ARKK ARKG ARKW ARKQ ARKF ARKX PRNT IZRL ARKB".split()
rows=[]
for t in T:
    r={"ticker":t,"group":"XL" if t.startswith("XL") else "ARK"}
    for lab,kw in [("fix",{}),("vol",{"hi_mode":"vol"}),("fixC",{"cost":.0005}),("volC",{"hi_mode":"vol","cost":.0005})]:
        m=run(f"/workspace/data/etf/{t}.csv",**kw)
        if lab=="fix":
            r.update(start=m["start"],end=m["end"],years=round((m["_eq"].index[-1]-m["_eq"].index[0]).days/365.25,1),
                     bh_cagr=m["bh_cagr"],bh_mdd=m["bh_mdd"],bh_sharpe=m["bh_sharpe"],state_1028=m["last"]["state"],
                     pending=m["last"]["pending"])
        if lab=="vol": r["state_1028_vol"]=m["last"]["state"]
        r.update({f"{lab}_cagr":m["strat_cagr"],f"{lab}_mdd":m["strat_mdd"],f"{lab}_sharpe":m["strat_sharpe"],f"{lab}_trades":m["trades"]})
    rows.append(r)
d=pd.DataFrame(rows)
for lab in ["fix","vol","fixC","volC"]:
    d[f"{lab}_beat_cagr"]=d[f"{lab}_cagr"]>d.bh_cagr; d[f"{lab}_smaller_mdd"]=d[f"{lab}_mdd"]>d.bh_mdd
d["note"]=np.where(d.years<3,"样本不足","")
d.round(4).to_csv("etf_summary.csv",index=False)
pd.set_option("display.width",250)
show=d[["ticker","start","years","bh_cagr","fix_cagr","vol_cagr","fixC_cagr","bh_mdd","fix_mdd","vol_mdd","bh_sharpe","fix_sharpe","vol_sharpe","fix_trades","vol_trades","state_1028","state_1028_vol","pending"]]
print(show.round(3).to_string())
ok=d[d.note==""]
for g,x in [("全部",ok),("XL",ok[ok.group=="XL"]),("ARK",ok[ok.group=="ARK"])]:
    print(g,len(x),{l:(int(x[f"{l}_beat_cagr"].sum()),int(x[f"{l}_smaller_mdd"].sum()),int((x[f"{l}_sharpe"]>x.bh_sharpe).sum()),round((x[f"{l}_cagr"]-x.bh_cagr).median()*100,2),round((x[f"{l}_mdd"]-x.bh_mdd).median()*100,1)) for l in ["fix","vol","fixC","volC"]})
fig,ax=plt.subplots(2,1,figsize=(13,8),sharex=True); x=np.arange(len(d)); w=.4
for i,(l,n) in enumerate([("fix","fixed 20%"),("vol","vol-scaled")]):
    ax[0].bar(x+(i-.5)*w,(d[f"{l}_cagr"]-d.bh_cagr)*100,w,label=n)
    ax[1].bar(x+(i-.5)*w,(d[f"{l}_mdd"]-d.bh_mdd)*100,w,label=n)
ax[0].set_ylabel("Strategy CAGR - B&H CAGR (pp)"); ax[1].set_ylabel("MaxDD improvement (pp, +=better)")
for a in ax: a.axhline(0,c="k",lw=.8); a.legend(); a.grid(alpha=.3)
ax[1].set_xticks(x); ax[1].set_xticklabels([t+("*" if n else "") for t,n in zip(d.ticker,d.note)],rotation=45)
ax[0].set_title("Siji 1x vs Buy&Hold (* = ARKB, insufficient sample)"); plt.tight_layout(); plt.savefig("etf_compare.png",dpi=120)
