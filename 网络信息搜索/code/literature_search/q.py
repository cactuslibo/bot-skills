import json,sys,urllib.request,urllib.parse,difflib,concurrent.futures as cf
titles=[l.strip() for l in open(sys.argv[1]) if l.strip()]
def f(t):
    u="https://api.crossref.org/works?rows=3&query.bibliographic="+urllib.parse.quote(t)+"&mailto=YOUR_EMAIL@example.com"
    try:
        it=json.load(urllib.request.urlopen(u,timeout=40))["message"]["items"]
    except Exception as e:
        import time;time.sleep(3);it=json.load(urllib.request.urlopen(u,timeout=40))["message"]["items"]
    best=max(it,key=lambda x:difflib.SequenceMatcher(None,t.lower(),(x.get("title") or [""])[0].lower()).ratio())
    tt=(best.get("title") or [""])[0]
    au=[a.get("family","")for a in best.get("author",[])]
    y=(best.get("issued",{}).get("date-parts") or [[None]])[0][0]
    return {"q":t,"title":tt,"score":round(difflib.SequenceMatcher(None,t.lower(),tt.lower()).ratio(),2),"doi":best.get("DOI"),"year":y,"authors":au,"venue":(best.get("container-title") or [""])[0]}
with cf.ThreadPoolExecutor(2) as ex:
    for r in ex.map(f,titles): print(json.dumps(r,ensure_ascii=False))
