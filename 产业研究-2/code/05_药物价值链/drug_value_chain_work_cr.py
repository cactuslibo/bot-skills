import json,urllib.request,urllib.parse,os,time,difflib,re
M=json.load(open('meta.json'))
out={}
for k,m in M.items():
    d=m['doi']
    if not d: out[k]={'status':'no_doi'};continue
    fn='/workspace/drug_value_chain/crossref/'+d.replace('/','_')+'.json'
    if not os.path.exists(fn):
        url='https://api.crossref.org/works/'+urllib.parse.quote(d)+'?mailto=YOUR_EMAIL@example.com'
        try:
            r=urllib.request.urlopen(url,timeout=30).read(); open(fn,'wb').write(r)
        except Exception as e:
            out[k]={'status':'err '+str(e)[:60]};continue
        time.sleep(0.15)
    j=json.load(open(fn))['message']
    ti=(j.get('title') or [''])[0]
    yr=None
    for f in ('published-print','published-online','issued'):
        if j.get(f,{}).get('date-parts') and j[f]['date-parts'][0][0]: yr=j[f]['date-parts'][0][0];break
    iss=j.get('issued',{}).get('date-parts',[[None]])[0][0]
    au=j.get('author',[]); fa=au[0].get('family','') if au else ''
    sim=difflib.SequenceMatcher(None,re.sub(r'\W','',ti.lower()),re.sub(r'\W','',m['title'].lower())).ratio()
    um_first=m['authors'].split(',')[0].split()[-1] if m['authors'] else ''
    out[k]={'status':'ok','cr_title':ti,'cr_year':iss,'um_year':m['year'],'cr_first':fa,'um_first':um_first,'sim':round(sim,2),'journal':(j.get('container-title') or [''])[0],'vol':j.get('volume'),'page':j.get('page') or j.get('article-number'),'n_auth':len(au),'type':j.get('type'),
      'authors':'; '.join((a.get('family','')+' '+a.get('given','')[:1]).strip() for a in au[:6])+(' 等' if len(au)>6 else '')}
json.dump(out,open('crossref_check.json','w'),ensure_ascii=False,indent=1)
for k,v in out.items():
    if v['status']!='ok': print(k,v);continue
    flag=[]
    if v['sim']<0.85: flag.append('TITLE')
    if str(v['cr_year'])!=v['um_year']: flag.append('YEAR')
    if v['um_first'].lower() not in v['cr_first'].lower() and v['cr_first'].lower() not in v['um_first'].lower(): flag.append('AUTH')
    if flag: print(k,flag,v['cr_year'],v['um_year'],v['cr_first'],v['um_first'],v['sim'],'|',v['cr_title'][:80])
