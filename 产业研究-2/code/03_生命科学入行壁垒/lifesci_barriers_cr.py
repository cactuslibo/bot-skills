import json,urllib.request,urllib.parse
from ids import *
res={}
for k,d in dois.items():
  try:
    r=json.load(urllib.request.urlopen("https://api.crossref.org/works/"+urllib.parse.quote(d)+"?mailto=YOUR_EMAIL@example.com",timeout=20))["message"]
    y=(r.get("issued",{}).get("date-parts") or [[None]])[0][0]
    res[k]={"ok":1,"title":(r.get("title") or [""])[0][:90],"year":y,"au":(r.get("author") or [{}])[0].get("family")}
  except Exception as e: res[k]={"ok":0,"err":str(e)[:40]}
  try:
    u=json.load(urllib.request.urlopen(f"https://api.unpaywall.org/v2/{urllib.parse.quote(d)}?email=YOUR_EMAIL@example.com",timeout=20))
    res[k]["oa"]=(u.get("best_oa_location") or {}).get("url_for_pdf")
  except Exception: res[k]["oa"]=None
  print(ID[k],k,res[k])
json.dump(res,open("crossref.json","w"),ensure_ascii=False,indent=1)
