import requests,json,time,os,re,pandas as pd,numpy as np,urllib.parse as up
H={"User-Agent":"research YOUR_EMAIL@example.com"}
R=pd.read_csv('stage12.csv'); C=json.load(open('fts_cache.json')) if os.path.exists('fts_cache.json') else {}
def fts(q,ciks=None):
  key=q+'|'+str(ciks)
  if key in C: return C[key]
  url='https://efts.sec.gov/LATEST/search-index?q='+up.quote(q)+'&forms=10-K&dateRange=custom&startdt=2024-01-01&enddt=2026-10-31'
  if ciks: url+='&ciks=%010d'%ciks
  for i in range(3):
    x=requests.get(url,headers=H); time.sleep(0.15)
    if x.status_code==200: break
    time.sleep(2)
  h=x.json().get('hits',{}).get('hits',[]) if x.status_code==200 else None
  C[key]=None if h is None else [dict(n=a['_source']['display_names'][0],cik=a['_source']['ciks'][0],date=a['_source']['file_date'],id=a['_id']) for a in h]
  json.dump(C,open('fts_cache.json','w')); return C[key]
SUF=r'(,?\s+(INC|CORP|CORPORATION|CO|LTD|PLC|N\.?V|S\.?A|AG|SE|HOLDINGS?|GROUP|LIMITED|COMPANY|INCORPORATED|TECHNOLOGIES|THE)\.?)+$'
def short(n):
  n=re.sub(r'\s*/.*$','',str(n)).upper(); n=re.sub(SUF,'',n).strip(' ,.')
  return n.title()
out=[]
for _,r in R[R.s2=='通过'].iterrows():
  sub=json.load(open(f'edgar/sub{int(r.cik)}.json')); nm=short(sub['name'])
  o=dict(ticker=r.ticker,search_name=nm)
  # (c) 产能售罄/长约：公司自身 10-K
  cap=[]
  for q in ['"sold out"','"take-or-pay"','"long-term supply agreement"','"capacity reservation"','"fully booked"']:
    h=fts(q,int(r.cik)); 
    if h: cap.append(q.strip('"'))
  o['cap_terms']=';'.join(cap)
  # (d) 客户披露 sole/single source 
  others=set()
  if len(nm)>=4:
    for q in [f'"sole source" "{nm}"',f'"single source" "{nm}"',f'"sole supplier" "{nm}"']:
      for a in fts(q) or []:
        if int(a['cik'])!=int(r.cik): others.add(a['n'].split('  (')[0])
  o['ss_n_filers']=len(others); o['ss_filers']='; '.join(sorted(others)[:8])
  out.append(o); print(o['ticker'],nm,cap,len(others),flush=True)
pd.DataFrame(out).to_csv('stage3_text.csv',index=False)
