import json,urllib.request,urllib.parse,re,time,difflib
exec(open('grades_r3.py').read()); info=json.load(open('info_r3.json'))
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'litcheck (mailto:YOUR_EMAIL@example.com)'}),timeout=40))
norm=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
out={}
for k in G:
    i=info[k]; r={'key':k,'um_title':i['title'],'um_doi':i['doi']}
    try:
        if i['doi'] and not i['doi'].upper().startswith('10.3386'):
            m=get('https://api.crossref.org/works/'+urllib.parse.quote(i['doi']))['message']
            r.update(mode='doi',cr_title=(m.get('title') or [''])[0],cr_journal=(m.get('container-title') or [''])[0],cr_year=(m.get('issued',{}).get('date-parts') or [[None]])[0][0],cr_doi=m['DOI'],cr_authors=[a.get('family') for a in m.get('author',[])][:6])
        else:
            q=urllib.parse.quote(i['title']+' '+i['authors'].split(',')[0])
            items=get('https://api.crossref.org/works?rows=3&query.bibliographic='+q)['message']['items']
            best=max(items,key=lambda m:difflib.SequenceMatcher(None,norm(i['title']),norm((m.get('title') or [''])[0])).ratio())
            r.update(mode='search',cr_title=(best.get('title') or [''])[0],cr_journal=(best.get('container-title') or [''])[0],cr_year=(best.get('issued',{}).get('date-parts') or [[None]])[0][0],cr_doi=best['DOI'],cr_authors=[a.get('family') for a in best.get('author',[])][:6])
        r['sim']=round(difflib.SequenceMatcher(None,norm(i['title']),norm(r['cr_title'])).ratio(),2)
    except Exception as e: r['error']=str(e)[:100]
    out[k]=r; time.sleep(0.15)
json.dump(out,open('crossref_r3.json','w'),ensure_ascii=False,indent=1)
for k,r in out.items(): print(k,r.get('mode'),r.get('sim'),r.get('cr_doi'),r.get('cr_year'),(r.get('cr_journal') or '')[:30],'|',(r.get('cr_title') or '')[:60],r.get('error',''))
