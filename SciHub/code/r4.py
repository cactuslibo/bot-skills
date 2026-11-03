import re,os,sys,json,subprocess,urllib.parse
import dvc_lib as L
from curl_cffi import requests as R
from concurrent.futures import ThreadPoolExecutor
md,D,out=sys.argv[1:4]
rows=[]
for ln in open(md):
    c=[x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c)<3 or c[0] in('#','ID') or set(c[0])<=set('-'): continue
    if re.fullmatch(r'\d+',c[0]): c=c[1:]
    i,t=c[0],re.sub(r'（.*?）','',c[1]).strip()
    doi=next((m.group(0).rstrip('.') for x in c[2:] for m in [re.search(r'10\.\d{4,}/\S+',x)] if m),'')
    rows.append((i,t,doi))
def g(u):
    try: return R.get(u,impersonate="chrome",timeout=40,allow_redirects=True)
    except Exception: return None
def tryurl(u,fn,t):
    if not u or L.BAD.search(u): return None
    x=g(u)
    if not x: return None
    cs=[u] if x.content[:4]==b'%PDF' else []
    if not cs:
        h=x.text; base=x.url.split('/')[0]+'//'+x.url.split('/')[2]
        cs=re.findall(r'citation_pdf_url"\s+content="([^"]+)',h)+re.findall(r'content="([^"]+)"\s+name="citation_pdf_url',h)
        cs+=[m if m.startswith('http') else base+'/'+m.lstrip('/') for m in re.findall(r'href="([^"]*(?:bitstream|download|\.pdf)[^"]*)"',h)][:8]
    for cu in cs:
        if L.BAD.search(cu): continue
        y=x if cu==u else g(cu)
        if y and y.content[:4]==b'%PDF':
            open(fn+'.tmp','wb').write(y.content)
            if L.ok(fn+'.tmp',t): os.rename(fn+'.tmp',fn); return cu
            os.remove(fn+'.tmp')
def run(r):
    i,t,doi=r; fn=f'{D}/{i}.pdf'
    if os.path.exists(fn): return dict(id=i,st='EXISTS')
    cs,_=L.cands(doi,t) if doi else L.cands('',t)
    # arXiv exact title
    a=L.get('http://export.arxiv.org/api/query?search_query=ti:%22'+urllib.parse.quote(t)+'%22&max_results=3').decode('utf8','ignore')
    for ti,idd in re.findall(r'<entry>.*?<id>http://arxiv.org/abs/(\S+?)</id>.*?<title>(.*?)</title>',a,re.S) and [(b,a_) for a_,b in re.findall(r'<id>http://arxiv.org/abs/(\S+?)</id>.*?<title>(.*?)</title>',a,re.S)]:
        if L.norm(ti)==L.norm(t): cs.append(('https://arxiv.org/pdf/'+idd,'arXiv'))
    if 'ssrn' in doi.lower(): pass
    for u,s in cs:
        v=tryurl(u,fn,t)
        if v: return dict(id=i,st='OK',src=s,url=v,doi=doi)
    return dict(id=i,st='MISS',doi=doi,cands=[u for u,_ in cs][:6])
os.makedirs(D,exist_ok=True)
res=list(ThreadPoolExecutor(8).map(run,rows))
json.dump(res,open(out,'w'),indent=1)
for r in res: print(r['id'],r['st'],r.get('src',''),r.get('url',''))
