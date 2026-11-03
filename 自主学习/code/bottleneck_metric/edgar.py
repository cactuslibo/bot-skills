import requests,json,time,os,pandas as pd
H={"User-Agent":"research YOUR_EMAIL@example.com"}
os.makedirs("edgar",exist_ok=True)
def get(u,f):
  p="edgar/"+f
  if os.path.exists(p): return json.load(open(p))
  r=requests.get(u,headers=H); time.sleep(0.12)
  if r.status_code!=200: return None
  open(p,"w").write(r.text); return r.json()
# universe: frames CY2019 revenue
fr=get("https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2019.json","fr1.json")["data"]
fr+=get("https://data.sec.gov/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2019.json","fr2.json")["data"]
d={}
for x in fr:
  if x["val"]>3e8: d[x["cik"]]=x["entityName"]
print(len(d))
SIC={"3674","3559","3672","3577","3572","3825","3827","3826","7372","3670","3679","3576"}
uni=[]
for c,n in d.items():
  s=get(f"https://data.sec.gov/submissions/CIK{c:010d}.json",f"sub{c}.json")
  if s and s.get("sic") in SIC: uni.append((c,n,s["sic"],(s.get("tickers") or [""])[0]))
pd.DataFrame(uni,columns=["cik","name","sic","ticker"]).to_csv("universe.csv",index=False); print(len(uni))
