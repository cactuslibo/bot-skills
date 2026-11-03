import json,urllib.request,urllib.parse
from ids2 import *
res={}
def get(u):
  return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"lit-check (mailto:YOUR_EMAIL@example.com)"}),timeout=30))
# find Get14 DOI
q=get("https://api.crossref.org/works?query.bibliographic="+urllib.parse.quote("Taking the pulse of strategic outsourcing relationships Getz Lamberti Kaitin Clinical Therapeutics 2014")+"&rows=2")
for it in q["message"]["items"]: print("Get14 cand",it["DOI"],it.get("title"),it.get("container-title"))
q=get("https://api.crossref.org/works?query.bibliographic="+urllib.parse.quote("Mirowski Van Horn Contract Research Organization Commercialization of Scientific Research")+"&rows=1")
for k,d in dois2.items():
  try:
    r=get("https://api.crossref.org/works/"+urllib.parse.quote(d))["message"]
    y=(r.get("issued",{}).get("date-parts") or [[None]])[0][0]
    res[k]={"id":ID2[k],"doi":d,"ok":1,"title":(r.get("title") or [""])[0][:100],"year":y,"au":(r.get("author") or [{}])[0].get("family"),"journal":(r.get("container-title") or [""])[0]}
  except Exception as e: res[k]={"id":ID2[k],"doi":d,"ok":0,"err":str(e)[:60]}
  try:
    u=get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(d)}?email=YOUR_EMAIL@example.com")
    res[k]["oa"]=[l.get("url_for_pdf") for l in (u.get("oa_locations") or []) if l.get("url_for_pdf")]
  except Exception: res[k]["oa"]=[]
  print(ID2[k],k,res[k])
json.dump(res,open("crossref_round2.json","w"),ensure_ascii=False,indent=1)
