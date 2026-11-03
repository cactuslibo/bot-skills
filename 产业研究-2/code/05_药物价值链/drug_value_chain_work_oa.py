import json,urllib.request,urllib.parse,time,os
from dl import fetch
M=json.load(open('meta.json'))
EXCL={'Haq26b','Bar13b'}
res={}
def get(u):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
    except Exception as e: return None
for k,m in M.items():
    if k in EXCL or os.path.exists(f'/workspace/drug_value_chain/pdfs/{k}.pdf'): continue
    d=m['doi']; cands=[]
    if d:
        u=get('https://api.unpaywall.org/v2/'+urllib.parse.quote(d)+'?email=YOUR_EMAIL@example.com')
        if u:
            for loc in (u.get('oa_locations') or []):
                if loc.get('url_for_pdf'): cands.append(loc['url_for_pdf'])
        o=get('https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(d))
        if o:
            for loc in (o.get('locations') or []):
                if loc.get('pdf_url'): cands.append(loc['pdf_url'])
            pmcid=(o.get('ids') or {}).get('pmcid')
            if pmcid:
                pid=pmcid.rstrip('/').split('/')[-1]
                cands.append(f'https://europepmc.org/backend/ptpmcrender.fcgi?accid={pid}&blobtype=pdf')
                cands.append(f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pid}/pdf/')
        if d.startswith('10.1101/'): cands.append(f'https://www.medrxiv.org/content/{d}v1.full.pdf'); cands.append(f'https://www.biorxiv.org/content/{d}v1.full.pdf')
    seen=[];ok=False
    for c in cands:
        if c in seen: continue
        seen.append(c)
        if fetch(k,c): ok=c;break
    res[k]={'ok':ok,'tried':seen}
    print(k,bool(ok),len(seen),flush=True)
    time.sleep(0.1)
json.dump(res,open('oa_results.json','w'),indent=1)
