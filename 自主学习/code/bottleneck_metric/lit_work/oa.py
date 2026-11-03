import json,urllib.request,urllib.parse,subprocess,os,re,time
C=json.load(open("cands.json")); I=json.load(open("included.json"))
FORMAL={"Loe20":"10.1093/qje/qjz041","Bon20":"10.1016/j.jmoneco.2021.05.004","Rav20b":"10.1093/restud/rdad002","Gof13":"10.1016/j.jfineco.2021.05.054","Gof20":"10.1093/rfs/hhaa034","Car16":"10.1093/qje/qjaa044","Irv13":"10.2308/accr-51246","Run20":"10.1111/twec.13414","Pre17":"10.1016/j.econlet.2017.12.038","Ell20":"10.1257/aer.20210220","Dic12":"10.1111/j.1468-5957.2012.02283.x","Loe12":"10.1257/aer.102.6.2437","Alv00":"10.3386/w34110"}
ALT={"Bon20":["10.3386/w27002"],"Rav20b":["10.2139/ssrn.3324849"],"Gof20":["10.2139/ssrn.2981447"],"Car16":["10.2139/ssrn.2883800"],"Loe20":["10.3386/w23687"],"Dic12":["10.2139/ssrn.1012856"],"Irv13":["10.2139/ssrn.2347095"],"Hui18":["10.2139/ssrn.3210767"],"Dra08":["10.2139/ssrn.1287386"],"Hea14":["10.2139/ssrn.1865878"],"Agr23":["10.2139/ssrn.4166155"]}
json.dump(FORMAL,open("formal_doi.json","w"),indent=0)
H={"User-Agent":"Mozilla/5.0 (lit-check; mailto:YOUR_EMAIL@example.com)"}
def J(u):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    except Exception as e: return {}
def tryget(k,url):
    f=f"/workspace/bottleneck_metric/lit_pdfs/{k}.pdf"
    subprocess.run(["curl","-sL","-m","90","-A","Mozilla/5.0","-o",f+".tmp",url])
    ok=os.path.exists(f+".tmp") and open(f+".tmp","rb").read(5)==b"%PDF-" and subprocess.run(["pdfinfo",f+".tmp"],capture_output=True).returncode==0
    if ok: os.rename(f+".tmp",f)
    elif os.path.exists(f+".tmp"): os.remove(f+".tmp")
    return ok
log={}
for k in I:
    if os.path.exists(f"/workspace/bottleneck_metric/lit_pdfs/{k}.pdf"): log[k]="undermind"; continue
    dois=[d for d in [FORMAL.get(k),C[k]["doi"]]+ALT.get(k,[]) if d]
    urls=[]
    for d in dict.fromkeys(dois):
        u=J(f"https://api.unpaywall.org/v2/{d}?email=YOUR_EMAIL@example.com")
        for loc in (u.get("oa_locations") or []):
            if loc.get("url_for_pdf"): urls.append(loc["url_for_pdf"])
        o=J(f"https://api.openalex.org/works/doi:{d}?mailto=YOUR_EMAIL@example.com")
        for loc in (o.get("locations") or []):
            if loc.get("pdf_url"): urls.append(loc["pdf_url"])
    got=None
    for url in dict.fromkeys(urls):
        if tryget(k,url): got=url; break
    log[k]=got or ("FAIL; tried %d urls"%len(set(urls)))
    print(k,log[k],flush=True)
json.dump(log,open("oa_log.json","w"),indent=1)
