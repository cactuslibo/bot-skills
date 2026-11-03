import csv,os,re,urllib.parse,time,html,dvc_lib as L
from curl_cffi import requests as R
D='/workspace/multiscale_forces_papers/pdfs'
for i,_,doi,t in csv.reader(open('ms.tsv'),delimiter='\t'):
    if os.path.exists(f'{D}/{i}.pdf'): continue
    tq=re.sub(r'[^\w\s-]',' ',t).strip(' .')
    x=R.get('https://arxiv.org/search/?searchtype=title&size=25&query='+urllib.parse.quote_plus(tq[:200]),impersonate='chrome',timeout=30)
    hits=[]
    for b in x.text.split('<li class="arxiv-result">')[1:]:
        a=re.search(r'arxiv.org/abs/([^"\s<]+)',b); tt=re.search(r'<p class="title is-5 mathjax">(.*?)</p>',b,re.S)
        if a and tt and L.norm(html.unescape(re.sub('<[^>]+>','',tt.group(1)))).rstrip()==L.norm(t): hits.append(a.group(1))
    done=False
    for a in hits:
        y=R.get(f'https://arxiv.org/pdf/{a}',impersonate='chrome',timeout=60); open('/tmp/a.pdf','wb').write(y.content)
        if L.ok('/tmp/a.pdf',t): os.rename('/tmp/a.pdf',f'{D}/{i}.pdf'); print(i,'OK arXiv',a,flush=True); done=True;break
    if not done: print(i,'MISS',hits,flush=True)
    time.sleep(3)
