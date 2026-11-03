# 事先登记的非财务标签：EDGAR 全文检索 2015–2024 10-K 中，“他人”文件同时出现公司名与 "sole source"/"single source" 的去重申报人数
# ratio = 共现人数 / 提及公司名的去重申报人数（剔除本公司 CIK）。登记规则（看结果前写定）：
# B = 共现人数>=5 且 ratio >= 全样本P75；S = ratio <= 全样本P25；其余不打标签
import requests,time,json,re,os,pandas as pd,urllib.parse as up
H={"User-Agent":"research YOUR_EMAIL@example.com"}
P=pd.read_csv("panel.csv"); F=P.dropna(subset=["ticker"]).drop_duplicates("cik")[["cik","name","ticker","sic"]]
def short(n):
  n=re.sub(r"[,\.]| /DE/| /DEL/","",n,flags=re.I)
  n=re.sub(r"\b(INC|CORP|CORPORATION|CO|LTD|LIMITED|HOLDINGS|INCORPORATED|NV|SA|PLC|THE|GROUP|TECHNOLOGIES|TECHNOLOGY|INTERNATIONAL)\b","",n,flags=re.I)
  return " ".join(n.split()).title()
def q(s):
  u="https://efts.sec.gov/LATEST/search-index?q="+up.quote(s)+"&forms=10-K&dateRange=custom&startdt=2015-01-01&enddt=2024-12-31"
  for _ in range(3):
    r=requests.get(u,headers=H); time.sleep(0.15)
    if r.status_code==200: return r.json()
    time.sleep(2)
  return None
cache=json.load(open("labels_cache.json")) if os.path.exists("labels_cache.json") else {}
rows=[]
for _,r in F.iterrows():
  nm={"ASML":"ASML","TSM":"Taiwan Semiconductor","A":"Agilent","FLEX":"Flex Ltd","P":"Pure Storage","ON":"ON Semiconductor","KE":"Kimball Electronics","BIO":"Bio-Rad"}.get(r.ticker,short(r["name"]))
  if nm not in cache:
    a=q(f'"{nm}" "sole source"'); b=q(f'"{nm}" "single source"'); c=q(f'"{nm}"')
    def ents(d): return {x["key"] for x in d.get("aggregations",{}).get("entity_filter",{}).get("buckets",[])} if d else set()
    cache[nm]=[list(ents(a)|ents(b)),list(ents(c))]; json.dump(cache,open("labels_cache.json","w"))
  co,al=cache[nm]; me=f"{int(r.cik):010d}"
  co=[e for e in co if me not in e]; al=[e for e in al if me not in e]
  rows.append(dict(ticker=r.ticker,name=r["name"],q=nm,sic=r.sic,co=len(co),men=len(al),ratio=len(co)/len(al) if al else float("nan")))
L=pd.DataFrame(rows); p75,p25=L.ratio.quantile(.75),L.ratio.quantile(.25)
L["lab"]=L.apply(lambda x:1 if x.co>=5 and x.ratio>=p75 else (0 if x.ratio<=p25 else None),axis=1)
L.to_csv("labels_v2.csv",index=False); print("P75",p75,"P25",p25); print(L.lab.value_counts(dropna=False))
print(L.sort_values("ratio",ascending=False).to_string())
