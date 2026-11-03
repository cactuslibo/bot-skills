import requests,json,time,os,pandas as pd,numpy as np
H={"User-Agent":"research YOUR_EMAIL@example.com"}
U=pd.read_csv("universe.csv")
U=pd.concat([U,pd.DataFrame([dict(cik=937966,name="ASML",sic=3559,ticker="ASML"),dict(cik=1046179,name="TSMC",sic=3674,ticker="TSM")])],ignore_index=True).drop_duplicates("cik")
REV=["Revenues","RevenueFromContractWithCustomerExcludingAssessedTax","SalesRevenueNet","SalesRevenueGoodsNet"]
GP=["GrossProfit"]; OI=["OperatingIncomeLoss"]; COGS=["CostOfRevenue","CostOfGoodsAndServicesSold","CostOfGoodsSold"]
CL=["ContractWithCustomerLiabilityCurrent","ContractWithCustomerLiability"]; DR=["DeferredRevenueCurrent","DeferredRevenue","CustomerAdvancesCurrent"]
def annual(g,tags,inst=False):
  out={}
  for t in tags:
    for u in g.get(t,{}).get("units",{}).get("USD",[]):
      if u.get("form") not in ("10-K","10-K/A","20-F","20-F/A"): continue
      fy=int(u["end"][:4]) + (1 if int(u["end"][5:7])>=7 and False else 0)
      if not inst:
        if "start" not in u: continue
        days=(pd.Timestamp(u["end"])-pd.Timestamp(u["start"])).days
        if days<350 or days>380: continue
      y=int(u["end"][:4]); f=u.get("filed","")
      if y not in out or f>out[y][1]: out[y]=(u["val"],f)  # 同一年保留最新申报（重述）值
  return {k:v[0] for k,v in out.items()}
rows=[]
for _,r in U.iterrows():
  p=f"edgar/cf{r.cik}.json"
  if not os.path.exists(p):
    x=requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{r.cik:010d}.json",headers=H); time.sleep(0.12)
    if x.status_code!=200: continue
    open(p,"w").write(x.text)
  ff=json.load(open(p)).get("facts",{}); g=dict(ff.get("ifrs-full",{})); g.update(ff.get("us-gaap",{}))
  if "Revenue" in g: g.setdefault("Revenues",g["Revenue"])
  for k in list(g):
    u=g[k].get("units",{})
    if "USD" not in u and u: g[k]={"units":{"USD":list(u.values())[0]}}  # 20-F 报告币种（EUR/TWD）——比率不受币种影响
  def merge(tags,inst=False):
    m={}
    for t in tags:
      for k,v in annual(g,[t],inst).items(): m.setdefault(k,v)
    return m
  rev,gp,oi,cogs,cl,dr=merge(REV),merge(GP),merge(OI),merge(COGS),merge(CL,True),merge(DR,True)
  for y in sorted(rev):
    gpy=gp.get(y, rev[y]-cogs[y] if y in cogs else np.nan)
    rows.append(dict(cik=r.cik,name=r["name"],ticker=r.ticker,sic=r.sic,year=y,rev=rev[y],gp=gpy,oi=oi.get(y,np.nan),cl=cl.get(y,np.nan),dr=dr.get(y,np.nan)))
P=pd.DataFrame(rows); P.to_csv("panel.csv",index=False); print(P.shape, P.year.min(), P.year.max())
