import json,urllib.request,subprocess,os,time
exec(open('grades.py').read())
X=json.load(open('crossref_r2.json')); R=json.load(open('info_new.json'))
D="/workspace/bottleneck_metric/lit_pdfs"
H={"User-Agent":"Mozilla/5.0 (lit-check; mailto:YOUR_EMAIL@example.com)"}
def J(u):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    except Exception: return {}
def have(k): return any(x.startswith(k+".") or x.startswith(k+"_") for x in os.listdir(D))
def tryget(k,url):
    f=f"{D}/{k}.pdf"
    subprocess.run(["curl","-sL","-m","90","-A","Mozilla/5.0","-o",f+".tmp",url])
    ok=os.path.exists(f+".tmp") and open(f+".tmp","rb").read(5)==b"%PDF-" and subprocess.run(["pdfinfo",f+".tmp"],capture_output=True).returncode==0
    if ok: os.rename(f+".tmp",f)
    elif os.path.exists(f+".tmp"): os.remove(f+".tmp")
    return ok
log={}
for k in G:
    if have(k): log[k]="have"; continue
    dois=[d for d in [X[k].get("cr_doi"),R[k].get("doi")] if d]
    urls=[]
    for d in dict.fromkeys(x.lower() for x in dois):
        u=J(f"https://api.unpaywall.org/v2/{d}?email=YOUR_EMAIL@example.com")
        for loc in (u.get("oa_locations") or []):
            if loc.get("url_for_pdf"): urls.append(loc["url_for_pdf"])
        o=J(f"https://api.openalex.org/works/doi:{d}?mailto=YOUR_EMAIL@example.com")
        for loc in (o.get("locations") or []):
            if loc.get("pdf_url"): urls.append(loc["pdf_url"])
    got=None
    for url in list(dict.fromkeys(urls))[:6]:
        if tryget(k,url): got=url; break
    log[k]=got or ("FAIL; tried %d urls"%len(set(urls)))
    print(k,log[k],flush=True)
json.dump(log,open("oa_log_r2.json","w"),indent=1)
print("DONE")
