import csv,json,os,re,subprocess,sys,urllib.parse
from concurrent.futures import ThreadPoolExecutor
D='/workspace/drug_value_chain/pdfs'
BAD=re.compile(r'sci-hub|scihub|libgen|library\.lol|annas-archive|z-lib|booksc|sci\.hub',re.I)
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
import os
M=os.environ.get('UNPAYWALL_EMAIL','you@example.com')
def get(u,t=25): return subprocess.run(['curl','-sL','-m',str(t),'-A',UA,u],capture_output=True).stdout
def js(u):
    try: return json.loads(get(u))
    except: return {}
def norm(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())
def cands(doi,title):
    c=[]
    if doi.startswith('http'):
        pid=doi.rstrip('/').split('/')[-1]
        s=js(f'https://api.semanticscholar.org/graph/v1/paper/{pid}?fields=openAccessPdf,externalIds,title')
        doi=(s.get('externalIds') or {}).get('DOI') or ''
        if (s.get('openAccessPdf') or {}).get('url'): c.append((s['openAccessPdf']['url'],'S2'))
    if doi:
        d=js(f'https://api.unpaywall.org/v2/{doi}?email={M}')
        for l in d.get('oa_locations') or []:
            for k in ('url_for_pdf','url'):
                if l.get(k): c.append((l[k],'UPW:'+str(l.get('version'))))
        o=js(f'https://api.openalex.org/works/doi:{doi}?mailto={M}')
        for l in o.get('locations') or []:
            for k in ('pdf_url','landing_page_url'):
                if l.get(k): c.append((l[k],'OA:'+str(l.get('version'))))
        s=js(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds')
        if (s.get('openAccessPdf') or {}).get('url'): c.append((s['openAccessPdf']['url'],'S2'))
        ax=(s.get('externalIds') or {}).get('ArXiv')
        if ax: c.append((f'https://arxiv.org/pdf/{ax}','arXiv'))
        e=js(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{doi}%22&format=json&resultType=core')
        for r in (e.get('resultList') or {}).get('result',[]):
            p=r.get('pmcid')
            if p:
                c+= [(f"https://europepmc.org/articles/{p}?pdf=render",'EPMC'),(f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={p}&blobtype=pdf",'EPMC'),(f"https://www.ncbi.nlm.nih.gov/pmc/articles/{p}/pdf/",'PMC')]
    q=urllib.parse.quote(title[:150])
    o=js(f'https://api.openalex.org/works?search={q}&per-page=5&mailto={M}')
    for w in o.get('results') or []:
        if norm(w.get('title'))==norm(title):
            for l in w.get('locations') or []:
                if l.get('pdf_url'): c.append((l['pdf_url'],'OA-title:'+str(l.get('version'))))
    k=os.environ.get('CORE')
    seen=set();out=[]
    for u,s in c:
        if u not in seen and not BAD.search(u): seen.add(u);out.append((u,s))
    return out,doi
def ok(fn,title):
    if not os.path.exists(fn) or os.path.getsize(fn)<30000 or open(fn,'rb').read(4)!=b'%PDF': return False
    t=norm(subprocess.run(['pdftotext','-l','3',fn,'-'],capture_output=True).stdout.decode('utf8','ignore'))
    w=[norm(x) for x in title.split() if len(x)>3]
    nt=norm(title); return nt[:45] in t or (sum(x in t for x in w)/max(1,len(w))>=0.9 and nt[:20] in t)
def pdf_from_html(u):
    h=get(u).decode('utf8','ignore')
    m=re.search(r'citation_pdf_url"\s+content="([^"]+)',h) or re.search(r'content="([^"]+)"\s+name="citation_pdf_url',h)
    return m.group(1) if m else None
def run(row):
    i,pr,doi,title=row
    fn=f'{D}/{i}.pdf'
    if os.path.exists(fn): return (i,'EXISTS','','',doi)
    cs,doi2=cands(doi,title)
    for u,s in cs:
        for uu in [u]+([pdf_from_html(u)] if 1 else []):
            if not uu or BAD.search(uu): continue
            subprocess.run(['curl','-sL','-m','60','-A',UA,'-o',fn+'.tmp',uu])
            if ok(fn+'.tmp',title): os.rename(fn+'.tmp',fn); return (i,'OK',uu,s,doi2)
            if os.path.exists(fn+'.tmp'): os.remove(fn+'.tmp')
    return (i,'MISSING','','',doi2)
