import json,urllib.request,urllib.parse,re,time,difflib
exec(open('grades.py').read())
R=json.load(open('info_new.json'))
R["Jia23b"]={"key":"Jia23b","title":"The effect of customer and supplier concentrations on firm resilience during the COVID-19 pandemic: Resource dependence and power balancing","year":"2023","venue":"Journal of Operations Management","authors":"Shen-Yang Jiang, A. Yeung, Zhao-Jun Han, B. Huo","doi":"10.1002/joom.1236","pdf":"✓","abstract":""}
json.dump(R,open('info_new.json','w'),ensure_ascii=False,indent=1)
OVR={"Mue77":"10.2307/2553570","Fee04":"10.1016/j.jfineco.2003.10.002","Ahe12":"10.1111/jofi.12122","Her17b":"10.1111/jofi.12684"}
SEARCH={"Bro09b","Leh20","Das15","Bar20c","Tae12","Cow76","Cha15b","Fly19","Dor21","Hal18c","Loe18b","Mor17b","Bel22","Ili20","Cho19e","Sch84","Has21","Mue86b","Jin00","Oda85"}
UA={"User-Agent":"lit-verify/1.0 (mailto:YOUR_EMAIL@example.com)"}
def get(u):
    for i in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except urllib.error.HTTPError as e:
            if e.code==404: return {"_err":404}
            time.sleep(2)
        except Exception as e: time.sleep(2)
    return {"_err":"fail"}
def sim(a,b): 
    n=lambda s:re.sub(r'[^a-z0-9 ]','',(s or '').lower())
    return difflib.SequenceMatcher(None,n(a),n(b)).ratio()
out={}
for k in G:
    r=R[k]; t=r["title"]; fa=(r.get("authors","").split(",")[0].split()[-1] if r.get("authors") else "")
    rec={"undermind_doi":r.get("doi"),"title":t,"first_author":fa,"um_year":r["year"]}
    cands=[]
    if k in OVR: cands.append(OVR[k])
    d=r.get("doi")
    if d and k not in OVR: cands.append(d)
    best=None
    for dd in cands:
        j=get("https://api.crossref.org/works/"+urllib.parse.quote(dd))
        if "message" in j:
            m=j["message"]; best=m; rec["checked_doi"]=dd; break
        else: rec.setdefault("errors",[]).append(f"{dd}:{j.get('_err')}")
    if (best is None) or k in SEARCH or (best and "ssrn" in (best.get("DOI","").lower())):
        q=urllib.parse.urlencode({"query.bibliographic":t,"query.author":fa,"rows":5})
        j=get("https://api.crossref.org/works?"+q)
        for it in j.get("message",{}).get("items",[]):
            tt=(it.get("title") or [""])[0]
            if sim(tt,t)>0.85 and it.get("type")!="posted-content" and "ssrn" not in it.get("DOI",""):
                best=it; rec["checked_doi"]=it["DOI"]; rec["via"]="title-search"; break
    if best:
        rec["cr_doi"]=best.get("DOI"); rec["cr_title"]=(best.get("title") or [""])[0]
        rec["cr_container"]=(best.get("container-title") or [""])[0]
        dp=(best.get("issued") or {}).get("date-parts",[[None]])[0]; rec["cr_year"]=dp[0]
        au=best.get("author") or []; rec["cr_first_author"]=(au[0].get("family") if au else (best.get("editor") or [{}])[0].get("family"))
        rec["cr_authors"]=", ".join((a.get("given","")+" "+a.get("family","")).strip() for a in au[:6])
        rec["cr_volume"]=best.get("volume"); rec["cr_page"]=best.get("page"); rec["cr_type"]=best.get("type")
        rec["title_sim"]=round(sim(rec["cr_title"],t),2)
        rec["status"]="ok" if rec["title_sim"]>0.8 else "title_mismatch"
    else: rec["status"]="not_found"
    out[k]=rec; time.sleep(0.15)
json.dump(out,open("crossref_r2.json","w"),ensure_ascii=False,indent=1)
for k,r in out.items():
    print(k,r["status"],r.get("cr_doi"),r.get("cr_year"),r.get("um_year"),r.get("cr_first_author"),"|",(r.get("cr_container") or "")[:35],r.get("title_sim"),r.get("via",""))
