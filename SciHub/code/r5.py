import json,sys,os,time,urllib.parse,re
import dvc_lib as L
sys.argv=[sys.argv[0]]+sys.argv[1:]
import importlib
md,D,res=sys.argv[1:4]
exec(open('r4.py').read().split('def g(u)')[0].split('md,D,out=')[0])
md,D=sys.argv[1],sys.argv[2]
rows=[]
for ln in open(md):
    c=[x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c)<3 or c[0] in('#','ID') or set(c[0])<=set('-'): continue
    if re.fullmatch(r'\d+',c[0]): c=c[1:]
    rows.append((c[0],re.sub(r'（.*?）','',c[1]).strip()))
src=open('r4.py').read(); ns={}
ns={'R':__import__('curl_cffi.requests',fromlist=['x']),'L':L,'re':re,'os':os}; exec(src[src.index('def g(u)'):src.index('def run(r)')],ns)
R=json.load(open(res)); miss={r['id'] for r in R if r['st']=='MISS'}
for i,t in rows:
    if i not in miss: continue
    fn=f'{D}/{i}.pdf'; us=[]
    s=L.js('https://api.semanticscholar.org/graph/v1/paper/search?query='+urllib.parse.quote(t[:200])+'&limit=5&fields=title,openAccessPdf,externalIds'); time.sleep(1.2)
    for p in s.get('data') or []:
        if L.norm(p.get('title'))==L.norm(t):
            if (p.get('openAccessPdf') or {}).get('url'): us.append(p['openAccessPdf']['url'])
            ax=(p.get('externalIds') or {}).get('ArXiv')
            if ax: us.append('https://arxiv.org/pdf/'+ax)
    h=L.get('https://www.nber.org/api/v1/search?q='+urllib.parse.quote(t)).decode('utf8','ignore')
    for m in re.findall(r'/papers/(w\d+)',h)[:2]: us.append(f'https://www.nber.org/system/files/working_papers/{m}/{m}.pdf')
    got=None
    for u in us:
        got=ns['tryurl'](u,fn,t)
        if got: break
    print(i,'OK' if got else 'MISS',got or '',us[:3],flush=True)
