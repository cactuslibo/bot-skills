import json,re,urllib.request,urllib.parse,time,difflib
exec(open('grades_r3.py').read())
t=open('R5_info.txt').read()+open('G_info.txt').read()
R={}
for b in re.split(r'\n(?=\[[A-Za-z]+\d{2}[a-z]{0,3}\] )',t):
    m=re.match(r'\[([A-Za-z]+\d{2}[a-z]{0,3})\] (.*?) \((\d{4}|Unknown Year)\)\n(.*?)\n',b)
    if not m: continue
    k=m.group(1); d=re.search(r'DOI: (\S+)',b); a=re.search(r'\nBy (.*?)( - \d+ citations|\n)',b)
    pdf=re.search(r'\nPDF (\S)',b)
    R[k]={"title":m.group(2),"year":m.group(3),"venue":m.group(4).strip(),"doi":d.group(1) if d else None,"authors":a.group(1) if a else "","pdf":pdf.group(1) if pdf else "?"}
json.dump(R,open('info_r3.json','w'),ensure_ascii=False,indent=1)
UA={"User-Agent":"lit-verify/1.0 (mailto:YOUR_EMAIL@example.com)"}
def get(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except urllib.error.HTTPError as e:
            if e.code==404: return {"_err":404}
            time.sleep(2)
        except Exception: time.sleep(2)
    return {"_err":"fail"}
n=lambda s:re.sub(r'[^a-z0-9 ]','',(s or '').lower())
sim=lambda a,b:difflib.SequenceMatcher(None,n(a),n(b)).ratio()
out={}
for k in G3:
    r=R[k]; fa=r["authors"].split(",")[0].split()[-1] if r["authors"] else ""
    rec={"um":r}
    if r["doi"] and not r["doi"].lower().startswith("10.2139"):
        w=get("https://api.crossref.org/works/"+urllib.parse.quote(r["doi"]))
        if "message" in w:
            m=w["message"]; rec["by_doi"]={"doi":m["DOI"],"title":(m.get("title") or [""])[0],"year":(m.get("issued",{}).get("date-parts",[[None]])[0][0]),"venue":(m.get("container-title") or [""])[0],"authors":[a.get("family") for a in m.get("author",[])],"sim":round(sim(r["title"],(m.get("title") or [""])[0]),2)}
        else: rec["by_doi"]=w
    q=get("https://api.crossref.org/works?rows=3&query.bibliographic="+urllib.parse.quote(r["title"])+"&query.author="+urllib.parse.quote(fa))
    c=[]
    for m in q.get("message",{}).get("items",[]):
        c.append({"doi":m["DOI"],"title":(m.get("title") or [""])[0],"year":(m.get("issued",{}).get("date-parts",[[None]])[0][0]),"venue":(m.get("container-title") or [""])[0],"type":m.get("type"),"authors":[a.get("family") for a in m.get("author",[])][:4],"sim":round(sim(r["title"],(m.get("title") or [""])[0]),2)})
    rec["by_title"]=c; out[k]=rec
    best=rec.get("by_doi") if isinstance(rec.get("by_doi"),dict) and rec["by_doi"].get("doi") else None
    print(k,"| UM:",r["doi"],r["year"],"|",("DOI-ok %s %s %s sim=%s"%(best["doi"],best["year"],best["venue"][:30],best["sim"])) if best else "no-doi-rec","|| T:",[(x["doi"],x["year"],x["venue"][:25],x["type"],x["sim"]) for x in c[:2]])
    time.sleep(0.3)
json.dump(out,open('crossref_r3.json','w'),ensure_ascii=False,indent=1)
