import json,urllib.request,urllib.parse,concurrent.futures as cf,difflib
m=json.load(open('meta.json'))
def chk(v):
    if not v['doi']: return v['key'],'NO_DOI',None,None
    try:
        r=json.load(urllib.request.urlopen(urllib.request.Request('https://api.crossref.org/works/'+urllib.parse.quote(v['doi']),headers={'User-Agent':'lit-check (mailto:none@example.com)'}),timeout=30))['message']
        t=(r.get('title') or [''])[0]; y=(r.get('issued',{}).get('date-parts') or [[None]])[0][0]
        s=difflib.SequenceMatcher(None,t.lower(),v['title'].lower()).ratio()
        fa=(r.get('author') or [{}])[0].get('family','')
        return v['key'],'OK' if s>0.8 else f'TITLE_MISMATCH({s:.2f}):{t[:60]}',y,fa
    except Exception as e: return v['key'],'CR_ERR '+str(e)[:40],None,None
with cf.ThreadPoolExecutor(1) as ex:
    import time
    for k,st,y,fa in ex.map(lambda v:(time.sleep(0.4),chk(v))[1] if v.get("crossref","").startswith("CR_ERR") or "crossref" not in v else (v["key"],v["crossref"],v["cr_year"],v["cr_first"]),m.values()):
        m[k]['crossref']=st; m[k]['cr_year']=y; m[k]['cr_first']=fa
json.dump(m,open('meta.json','w'),ensure_ascii=False,indent=0)
for v in m.values():
    if v['crossref']!='OK' or (v['cr_year'] and str(v['cr_year'])!=v['year']): print(v['key'],v['year'],v['cr_year'],v['crossref'])
