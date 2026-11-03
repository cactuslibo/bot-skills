import os
EMAIL=os.environ.get('UNPAYWALL_EMAIL','you@example.com')
import csv,json,os,re,subprocess,sys,urllib.parse,time
DEST={'tem':'/workspace/tem_analysis/pdfs','life':'/workspace/lifesci_barriers/pdfs','bn':'/workspace/bottleneck_metric/lit_pdfs'}
BAD=re.compile(r'sci-hub|scihub|libgen|library\.lol|annas-archive|z-lib|booksc',re.I)
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
def get(u,t=25):
    try: return subprocess.run(['curl','-sL','-m',str(t),'-A',UA,u],capture_output=True).stdout
    except: return b''
def js(u):
    try: return json.loads(get(u))
    except: return {}
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
def cands(doi,title):
    c=[]
    if doi!='-':
        d=js(f'https://api.unpaywall.org/v2/{doi}?email={EMAIL}')
        for l in d.get('oa_locations') or []:
            for k in ('url_for_pdf','url'):
                if l.get(k): c.append((l[k],'Unpaywall:'+(l.get('version') or '?')+':'+(l.get('host_type') or '')))
        o=js(f'https://api.openalex.org/works/doi:{doi}?mailto={EMAIL}')
        for l in o.get('locations') or []:
            if l.get('pdf_url'): c.append((l['pdf_url'],'OpenAlex:'+str(l.get('version'))))
        s=js(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds')
        if (s.get('openAccessPdf') or {}).get('url'): c.append((s['openAccessPdf']['url'],'S2'))
        ax=(s.get('externalIds') or {}).get('ArXiv')
        if ax: c.append((f'https://arxiv.org/pdf/{ax}','arXiv:preprint'))
        e=js(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{doi}%22&format=json&resultType=core')
        for r in (e.get('resultList') or {}).get('result',[]):
            if r.get('pmcid'): c.append((f"https://europepmc.org/articles/{r['pmcid']}?pdf=render",'EuropePMC:published'))
    # title searches
    q=urllib.parse.quote(title[:150])
    o=js(f'https://api.openalex.org/works?search={q}&per-page=5&mailto={EMAIL}')
    for w in o.get('results') or []:
        if norm(title)[:40] in norm(w.get('title') or ''):
            for l in w.get('locations') or []:
                if l.get('pdf_url'): c.append((l['pdf_url'],'OpenAlex-title:'+str(l.get('version'))))
    a=get('http://export.arxiv.org/api/query?search_query=ti:%22'+urllib.parse.quote(title[:120])+'%22&max_results=3').decode('utf8','ignore')
    for ent in re.findall(r'<entry>(.*?)</entry>',a,re.S):
        t=re.search(r'<title>(.*?)</title>',ent,re.S).group(1)
        if norm(title)[:40] in norm(t):
            i=re.search(r'<id>http://arxiv.org/abs/(.*?)</id>',ent).group(1); c.append((f'https://arxiv.org/pdf/{i}','arXiv-title:preprint'))
    seen=set();out=[]
    for u,s in c:
        if u not in seen and not BAD.search(u): seen.add(u);out.append((u,s))
    return out
def short(t): return '_'.join(re.sub(r'[^A-Za-z0-9 ]','',t).split()[:4])
res=[]
for b,i,doi,title in csv.reader(open('items.tsv'),delimiter='\t'):
    if len(sys.argv)>1 and b!=sys.argv[1]: continue
    dd=DEST[b]; os.makedirs(dd,exist_ok=True)
    ex=[f for f in os.listdir(dd) if f==i+'.pdf' or f.startswith(i+'_')]
    if ex and i!='Rid26': res.append((b,i,'EXISTS',ex[0]));print(b,i,'EXISTS',ex,flush=True);continue
    ok=None
    for u,s in cands(doi,title):
        fn=os.path.join(dd,f'{i}_{short(title)}.pdf')
        subprocess.run(['curl','-sL','-m','60','-A',UA,'-o',fn,u])
        if os.path.exists(fn) and os.path.getsize(fn)>30000 and open(fn,'rb').read(4)==b'%PDF': ok=(fn,u,s);break
        if os.path.exists(fn): os.remove(fn)
    print(b,i,'OK' if ok else 'MISSING',ok,flush=True); res.append((b,i,'OK' if ok else 'MISSING',ok))
json.dump(res,open(f'res_{sys.argv[1] if len(sys.argv)>1 else "all"}.json','w'))
