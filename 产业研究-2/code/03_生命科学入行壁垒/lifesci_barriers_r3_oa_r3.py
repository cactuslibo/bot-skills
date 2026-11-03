import json,urllib.request,urllib.parse,subprocess,os
exec(open('grades_r3.py').read()); c=json.load(open('crossref_r3.json'))
FORMAL={"Kar07":"10.1111/j.1467-6451.2012.00473.x","Coo08":"10.1215/s12280-008-9040-y"}
log={}
def ok(f): return os.path.exists(f) and open(f,'rb').read(5)==b'%PDF-' and subprocess.run(["pdfinfo",f],capture_output=True).returncode==0
for k in G:
    f=f"dl/{k}.pdf"
    if os.path.exists(f): log[k]="undermind"; continue
    doi=FORMAL.get(k) or (c[k].get('cr_doi') if c[k].get('mode')=='doi' or c[k].get('sim',0)>=0.95 else None)
    urls=[]
    if doi:
        try:
            d=json.load(urllib.request.urlopen(f"https://api.unpaywall.org/v2/{doi}?email=YOUR_EMAIL@example.com",timeout=30))
            urls+=[l.get('url_for_pdf') for l in d.get('oa_locations') or [] if l.get('url_for_pdf')]
        except Exception as e: pass
        try:
            d=json.load(urllib.request.urlopen("https://api.openalex.org/works/doi:"+doi+"?mailto=YOUR_EMAIL@example.com",timeout=30))
            urls+=[l.get('pdf_url') for l in d.get('locations') or [] if l.get('pdf_url')]
        except Exception: pass
    got=None
    for u in dict.fromkeys(urls):
        subprocess.run(["curl","-sL","-m","60","-A","Mozilla/5.0","-o",f,u])
        if ok(f): got=u; break
        if os.path.exists(f): os.remove(f)
    log[k]=got or ("no_oa_url" if not urls else "oa_url_failed:"+";".join(urls[:2]))
    print(k,log[k][:100],flush=True)
json.dump(log,open('oa_log_r3.json','w'),indent=1)
