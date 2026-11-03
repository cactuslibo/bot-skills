import csv,os,re,urllib.parse,time,dvc_lib as L
from curl_cffi import requests as R
D='/workspace/multiscale_forces_papers/pdfs'
for i,_,doi,t in csv.reader(open('ms.tsv'),delimiter='\t'):
    if os.path.exists(f'{D}/{i}.pdf'): continue
    q=urllib.parse.quote(t[:150]); ax=set()
    for _ in range(3):
        s=L.js(f'https://api.semanticscholar.org/graph/v1/paper/search/match?query={q}&fields=title,externalIds,openAccessPdf')
        if s.get('data'): break
        time.sleep(3)
    for p in s.get('data') or []:
        if L.norm(p.get('title'))[:40]==L.norm(t)[:40]:
            a=(p.get('externalIds') or {}).get('ArXiv')
            if a: ax.add(a)
    o=L.js(f'https://api.openalex.org/works?search={q}&per-page=5&mailto={L.M}')
    for w in o.get('results') or []:
        if L.norm(w.get('title'))[:40]==L.norm(t)[:40]:
            for l in w.get('locations') or []:
                m=re.search(r'arxiv\.org/(?:abs|pdf)/([\w./-]+?)(?:v\d+)?$',l.get('landing_page_url') or '')
                if m: ax.add(m.group(1))
    done=False
    for a in ax:
        y=R.get(f'https://arxiv.org/pdf/{a}',impersonate='chrome',timeout=60)
        open('/tmp/a.pdf','wb').write(y.content)
        if L.ok('/tmp/a.pdf',t): os.rename('/tmp/a.pdf',f'{D}/{i}.pdf'); print(i,'OK arXiv',a,flush=True); done=True;break
    if not done: print(i,'MISS',ax,flush=True)
