import json,os,pandas as pd,numpy as np
d=pd.read_csv('../tradingview_universe.csv'); d=d[d.source=='screener_mcap>10B']
T={v['ticker'].upper():v['cik_str'] for v in json.load(open('tickers.json')).values()}
REV=["Revenues","RevenueFromContractWithCustomerExcludingAssessedTax","SalesRevenueNet","SalesRevenueGoodsNet","RevenueFromContractWithCustomerIncludingAssessedTax"]
COGS=["CostOfRevenue","CostOfGoodsAndServicesSold","CostOfGoodsSold","CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"]
CL=["ContractWithCustomerLiabilityCurrent","ContractWithCustomerLiability","CustomerAdvancesCurrent","CustomerAdvancesAndDeposits","DeferredRevenueCurrent"]
def ann(g,t,inst=False):
  out={}
  for u in g.get(t,{}).get("units",{}).get("USD",[]):
    if u.get("form") not in ("10-K","10-K/A","20-F","20-F/A","40-F"): continue
    if not inst:
      if "start" not in u: continue
      dd=(pd.Timestamp(u["end"])-pd.Timestamp(u["start"])).days
      if dd<350 or dd>380: continue
    y=int(u["end"][:4]); f=u.get("filed","")
    if y not in out or f>out[y][1]: out[y]=(u["val"],f)
  return {k:v[0] for k,v in out.items()}
def merge(g,tags,inst=False):
  m={};src={}
  for t in tags:
    for k,v in ann(g,t,inst).items():
      if k not in m: m[k]=v; src[k]=t
  return m,src
rows=[];meta=[]
for _,r in d.iterrows():
  t=str(r.ticker).upper(); k=T.get(t.replace('.','-')) or T.get(t.replace('.',''))
  m=dict(ticker=r.ticker,name=r['name'],tv_sector=r.sector,cik=k,sic=None,sic_desc=None,data='ok')
  if not k or not os.path.exists(f'edgar/cf{k}.json'): m['data']='无SEC XBRL'; meta.append(m); continue
  if os.path.exists(f'edgar/sub{k}.json'):
    s=json.load(open(f'edgar/sub{k}.json')); m['sic']=s.get('sic'); m['sic_desc']=s.get('sicDescription')
  ff=json.load(open(f'edgar/cf{k}.json')).get('facts',{}); g=dict(ff.get('ifrs-full',{})); g.update(ff.get('us-gaap',{}))
  if 'Revenue' in g: g.setdefault('Revenues',g['Revenue'])
  if 'CostOfSales' in g: g.setdefault('CostOfRevenue',g['CostOfSales'])
  for kk in list(g):
    u=g[kk].get('units',{})
    if 'USD' not in u and u: g[kk]={'units':{'USD':list(u.values())[0]}}
  m['ifrs']='ifrs-full' in ff
  rev,_=merge(g,REV); gp,_=merge(g,["GrossProfit"]); cogs,_=merge(g,COGS); oi,_=merge(g,["OperatingIncomeLoss","ProfitLossFromOperatingActivities"])
  cl,cls=merge(g,CL,True); rpo,_=merge(g,["RevenueRemainingPerformanceObligation"],True)
  for y in sorted(rev):
    if y<2007 or rev[y]<=0: continue
    gpy=gp.get(y, rev[y]-cogs[y] if y in cogs else np.nan)
    rows.append(dict(ticker=r.ticker,year=y,rev=rev[y],gp=gpy,oi=oi.get(y,np.nan),cl=cl.get(y,np.nan),cl_tag=cls.get(y),rpo=rpo.get(y,np.nan)))
  meta.append(m)
P=pd.DataFrame(rows); M=pd.DataFrame(meta)
P['gm']=P.gp/P.rev; P['om']=P.oi/P.rev
P.loc[(P.gm<=-1)|(P.gm>1),'gm']=np.nan
P.to_csv('panel_tv.csv',index=False); M.to_csv('meta.csv',index=False)
DOWN={2009,2019,2023}
FIN=lambda s: s is not None and str(s)[:2] in ('60','61','62','63','64','65','67')
out=[]
for _,m in M.iterrows():
  o=m.to_dict(); g=P[P.ticker==m.ticker].sort_values('year')
  gg=g.dropna(subset=['gm']); o['n_gm_years']=len(gg)
  sic=str(int(m.sic)) if pd.notna(m.sic) and str(m.sic).strip() not in ('','None') else None
  o['sic2']=sic[:2] if sic else None
  if m.data!='ok': o['s1']='不适用(无数据)'
  elif FIN(sic) or len(gg)==0: o['s1']='不适用(无毛利率/金融地产)'
  elif len(gg)<8: o['s1']='不足8年'
  elif not DOWN & set(gg.year): o['s1']='无下行年'
  else:
    o['s1']='待评'; i=gg.gm.idxmin(); o['gm_trough']=gg.gm.min(); o['trough_year']=int(gg.loc[i,'year'])
    o['gm_mean']=gg.gm.mean(); o['yr_lo']=int(gg.year.min()); o['yr_hi']=int(gg.year.max())
    # 第二段特征
    gg=gg.copy(); gg['up']=gg.rev.pct_change()>0; gg['dgm']=gg.gm.diff(); gg['dom']=gg.om.diff()
    u=gg[gg.up]; o['n_up']=len(u); o['up_dgm_mean']=u.dgm.mean(); o['up_dom_mean']=u.dom.mean()
    o['up_share_gm_rise']=(u.dgm>0).mean() if len(u) else np.nan
    o['gm_last']=gg.gm.iloc[-1]; o['om_last']=gg.om.iloc[-1]
  # 第三段数据
  gl=g.dropna(subset=['rev'])
  if len(gl):
    last=gl.iloc[-1]; o['last_year']=int(last.year); o['rev_last']=last.rev
    c=g.dropna(subset=['cl']); 
    if len(c): o['cl_year']=int(c.iloc[-1].year); o['cl_tag']=c.iloc[-1].cl_tag; o['cl_rev']=c.iloc[-1].cl/ g.set_index('year').rev.get(c.iloc[-1].year,np.nan)
    rp=g.dropna(subset=['rpo'])
    if len(rp)>=2 and rp.iloc[-1].year-rp.iloc[-2].year==1:
      a,b=rp.iloc[-2],rp.iloc[-1]; o['rpo_year']=int(b.year); o['rpo']=b.rpo; o['rpo_yoy']=b.rpo/a.rpo-1 if a.rpo>0 else np.nan
      o['book_to_bill']=(b.rev+b.rpo-a.rpo)/b.rev if pd.notna(b.rev) else np.nan
  out.append(o)
R=pd.DataFrame(out)
e=R.s1=='待评'; R['peer_n']=R[e].groupby('sic2').ticker.transform('count')
R.loc[e,'gm_trough_pct']=R[e].groupby('sic2').gm_trough.rank(pct=True)
R.loc[e&(R.peer_n<5),'s1']='同业不足5家'
e=R.s1=='待评'; R.loc[e,'s1']=np.where(R.loc[e,'gm_trough_pct']>=0.5,'通过','未通过')
p=R.s1=='通过'
R['s2']=np.where(p,np.where((R.up_dgm_mean>0)&(R.up_dom_mean>R.up_dgm_mean),'通过','未通过'),'—')
R.to_csv('stage12.csv',index=False)
print(R.s1.value_counts()); print(R.s2.value_counts())
