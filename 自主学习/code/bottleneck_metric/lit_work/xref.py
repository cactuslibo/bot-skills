import json,urllib.request,urllib.parse,time,re
C=json.load(open("cands.json")); I=json.load(open("included.json"))
UA={"User-Agent":"lit-check/1.0 (mailto:YOUR_EMAIL@example.com)"}
def get(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
        except Exception as e: err=str(e); time.sleep(2)
    return {"error":err}
out={}
for k in I:
    c=C[k]; r={"undermind":{"title":c["title"],"year":c["year"],"authors":c["authors"],"doi":c["doi"],"venue":c["venue"]}}
    if c["doi"]:
        j=get("https://api.crossref.org/works/"+urllib.parse.quote(c["doi"]))
        if "message" in j:
            m=j["message"]; r["doi_rec"]={"title":(m.get("title") or [""])[0],"year":(m.get("issued",{}).get("date-parts",[[None]])[0][0]),"authors":[a.get("family","") for a in m.get("author",[])],"container":(m.get("container-title") or [""])[0],"type":m.get("type"),"doi":m.get("DOI")}
        else: r["doi_rec"]=j
    q=urllib.parse.quote(c["title"]); a=c["authors"].split(",")[0].split()[-1] if c["authors"] else ""
    j=get(f"https://api.crossref.org/works?query.bibliographic={q}&query.author={urllib.parse.quote(a)}&rows=4&select=DOI,title,issued,author,container-title,type")
    r["title_query"]=[{"doi":m["DOI"],"title":(m.get("title") or [""])[0],"year":m.get("issued",{}).get("date-parts",[[None]])[0][0],"container":(m.get("container-title") or [""])[0],"type":m.get("type"),"authors":[x.get("family","") for x in m.get("author",[])][:4]} for m in j.get("message",{}).get("items",[])]
    out[k]=r; print(k,flush=True)
json.dump(out,open("crossref_raw.json","w"),ensure_ascii=False,indent=1)
