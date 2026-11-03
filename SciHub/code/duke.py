import json,csv,os,subprocess,urllib.parse
from dvc_lib import js,ok,D
rows={r[0]:r for r in csv.reader(open('dvc.tsv'),delimiter='\t')}
B='https://dukespace.lib.duke.edu/server/api'
for i in 'Dim03 Dim16 Dim04 Dim07 Dim07b Dim91 Gra12e'.split():
    t=rows[i][3]; r=js(f'{B}/discover/search/objects?dsoType=ITEM&query='+urllib.parse.quote(t))
    objs=[o['_embedded']['indexableObject'] for o in r.get('_embedded',{}).get('searchResult',{}).get('_embedded',{}).get('objects',[])][:8]
    done=False
    for it in objs:
        bs=js(f"{B}/core/items/{it['uuid']}/bundles?embed=bitstreams")
        for bd in bs.get('_embedded',{}).get('bundles',[]):
            if bd['name']!='ORIGINAL': continue
            for b in bd['_embedded']['bitstreams']['_embedded']['bitstreams']:
                subprocess.run(['curl','-sL','-m','60','-o','/tmp/d.pdf',f"{B}/core/bitstreams/{b['uuid']}/content"])
                if ok('/tmp/d.pdf',t): os.rename('/tmp/d.pdf',f'{D}/{i}.pdf'); print(i,'OK',it.get('name'),b['name']); done=True;break
            if done:break
        if done:break
    if not done: print(i,'MISS',[o.get('name') for o in objs])
