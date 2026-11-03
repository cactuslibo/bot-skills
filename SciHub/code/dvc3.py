import json,re,os,csv,subprocess
from curl_cffi import requests as R
from dvc_lib import js,ok,BAD,M,D
rows={r[0]:r for r in csv.reader(open('dvc.tsv'),delimiter='\t')}
def g(u):
    try: return R.get(u,impersonate="chrome",timeout=40,allow_redirects=True)
    except Exception: return None
for i,s,_,_,doi in json.load(open('res_dvc.json')):
    if os.path.exists(f'{D}/{i}.pdf') or not doi: continue
    t=rows[i][3]; o=js(f'https://api.openalex.org/works/doi:{doi}?mailto={M}')
    us=[]
    for l in o.get('locations') or []:
        if l.get('is_oa'): us+= [x for x in (l.get('pdf_url'),l.get('landing_page_url')) if x]
    done=False
    for u in us:
        if BAD.search(u) or done: continue
        x=g(u)
        if not x: continue
        cand=[u] if x.content[:4]==b'%PDF' else []
        h=x.text if not cand else ''
        cand+=re.findall(r'citation_pdf_url"\s+content="([^"]+)',h)+[ (x.url.split('/handle')[0] if 0 else '') ]
        cand+=[re.sub(r'^/',x.url.split('/',3)[0]+'//'+x.url.split('/')[2]+'/',m) for m in re.findall(r'href="([^"]*(?:bitstream|/download)[^"]*\.pdf[^"]*)"',h)]
        for cu in cand:
            if not cu or BAD.search(cu): continue
            y=x if cu==u else g(cu)
            if y and y.content[:4]==b'%PDF':
                open('/tmp/c.pdf','wb').write(y.content)
                if ok('/tmp/c.pdf',t): os.rename('/tmp/c.pdf',f'{D}/{i}.pdf'); print(i,'OK',l.get('version'),cu,flush=True); done=True;break
    if not done: print(i,'MISS',flush=True)
