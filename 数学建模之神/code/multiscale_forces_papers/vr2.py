import json,urllib.request,urllib.parse,sys
dois=sys.argv[1:]
out={}
for d in dois:
  try:
    r=json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/"+urllib.parse.quote(d),headers={"User-Agent":"mailto:bot@example.com"}),timeout=30))["message"]
    a=[(x.get("family") or x.get("name","")) for x in r.get("author",[])]
    y=(r.get("published-print") or r.get("issued"))["date-parts"][0][0]
    out[d]=dict(t=(r.get("title") or [""])[0],a=a,y=y,v=(r.get("container-title") or [""])[0],vol=r.get("volume"),p=r.get("page"))
  except Exception as e: out[d]=str(e)
  print(d,out[d],flush=True)
json.dump(out,open("cr_round2.json","w"),ensure_ascii=False,indent=1)
