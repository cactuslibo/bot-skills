import json,os,subprocess,re,csv
from dvc_lib import *
rows={r[0]:r for r in csv.reader(open('dvc.tsv'),delimiter='\t')}
res=json.load(open('res_dvc.json'))
def pmcid(doi):
    o=js(f'https://api.openalex.org/works/doi:{doi}?mailto={M}')
    p=(o.get('ids') or {}).get('pmcid')
    if p: return p.rstrip('/').split('/')[-1].replace('PMC','')
    e=js(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{doi}%22&format=json')
    for r in (e.get('resultList') or {}).get('result',[]):
        if r.get('pmcid'): return r['pmcid'].replace('PMC','')
def try_url(i,u,title,tag):
    fn=f'{D}/{i}.pdf'
    subprocess.run(['curl','-sL','-m','90','-A',UA,'-o',fn+'.tmp',u])
    if ok(fn+'.tmp',title): os.rename(fn+'.tmp',fn); print(i,'OK',tag,u,flush=True); return True
    if os.path.exists(fn+'.tmp'): os.remove(fn+'.tmp')
for i,s,_,_,doi in res:
    if s!='MISSING' or not doi: continue
    t=rows[i][3]
    p=pmcid(doi); done=False
    if p:
        for v in (1,2,3,4):
            m=js(f'https://pmc-oa-opendata.s3.amazonaws.com/metadata/PMC{p}.{v}.json')
            if m:
                pu=m.get('pdf_url') or ''
                pu=pu.replace('s3://pmc-oa-opendata/','https://pmc-oa-opendata.s3.amazonaws.com/')
                if pu and try_url(i,pu,t,'PMC-S3 manuscript=%s'%m.get('is_manuscript')): done=True;break
    if done: continue
    m=re.search(r'10\.3386/w(\d+)',doi,re.I)
    if m: try_url(i,f'https://www.nber.org/system/files/working_papers/w{m.group(1)}/w{m.group(1)}.pdf',t,'NBER WP')
