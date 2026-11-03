import requests,json,time,os,pandas as pd
H={"User-Agent":"research YOUR_EMAIL@example.com"}
d=pd.read_csv('../tradingview_universe.csv'); d=d[d.source=='screener_mcap>10B']
if not os.path.exists('tickers.json'):
  open('tickers.json','w').write(requests.get('https://www.sec.gov/files/company_tickers.json',headers=H).text)
T={v['ticker'].upper():v['cik_str'] for v in json.load(open('tickers.json')).values()}
for t in d.ticker:
  k=T.get(str(t).upper().replace('.','-')) or T.get(str(t).upper().replace('.',''))
  if not k: print('nocik',t); continue
  for kind,url in (('cf',f"https://data.sec.gov/api/xbrl/companyfacts/CIK{k:010d}.json"),('sub',f"https://data.sec.gov/submissions/CIK{k:010d}.json")):
    p=f"edgar/{kind}{k}.json"
    if os.path.exists(p): continue
    for i in range(3):
      x=requests.get(url,headers=H); time.sleep(0.13)
      if x.status_code==200: open(p,'w').write(x.text); break
      if x.status_code==404: break
      time.sleep(2)
