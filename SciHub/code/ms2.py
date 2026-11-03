import csv,json,os,re,urllib.parse
from curl_cffi import requests as R
import dvc_lib as L
D='/workspace/multiscale_forces_papers/pdfs'
def g(u):
    try: return R.get(u,impersonate="chrome",timeout=40)
    except Exception: return None
for i,_,doi,t in csv.reader(open('ms.tsv'),delimiter='\t'):
    if os.path.exists(f'{D}/{i}.pdf'): continue
    us=[]
    if doi:
        o=L.js(f'https://api.openalex.org/works/doi:{doi}?mailto={L.M}')
        us+=[(x,l.get('version')) for l in o.get('locations') or [] if l.get('is_oa') for x in (l.get('pdf_url'),l.get('landing_page_url')) if x]
    q=urllib.parse.quote('ti:"'+re.sub(r'[^\w\s-]',' ',t)[:120]+'"')
    a=L.get(f'http://export.arxiv.org/api/query?search_query={q}&max_results=5').decode()
    for e in re.findall(r'<entry>(.*?)</entry>',a,re.S):
        tt=re.search(r'<title>(.*?)</title>',e,re.S).group(1); 
        if L.norm(tt)==L.norm(t): us.append((re.search(r'<id>(.*?)</id>',e).group(1).replace('/abs/','/pdf/'),'arXiv'))
    done=False
    for u,v in us:
        if done or L.BAD.search(u): continue
        x=g(u)
        if not x: continue
        c=[u] if x.content[:4]==b'%PDF' else re.findall(r'citation_pdf_url"\s+content="([^"]+)',x.text)
        for cu in c:
            y=x if cu==u else g(cu)
            if y and y.content[:4]==b'%PDF':
                open('/tmp/m.pdf','wb').write(y.content)
                if L.ok('/tmp/m.pdf',t): os.rename('/tmp/m.pdf',f'{D}/{i}.pdf'); print(i,'OK',v,cu,flush=True); done=True; break
    if not done: print(i,'MISS',len(us),flush=True)
