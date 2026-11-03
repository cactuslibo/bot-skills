import json,re,sys,subprocess,glob,os
for f in sys.argv[1:]:
    t=open(f).read(); s=t[t.index('{'):t.rindex('}')+1]
    for r in json.loads(s)['results']:
        k=r['cite_key']; out=f'pdfs/{k}.pdf'
        if r.get('status')!='available' or not r.get('url'): print(k,'NOLINK',r.get('status')); continue
        subprocess.run(['curl','-sL','-m','120','-o',out,r['url']])
        ok=os.path.exists(out) and open(out,'rb').read(5)==b'%PDF-'
        pi=subprocess.run(['pdfinfo',out],capture_output=True,text=True)
        pg=re.search(r'Pages:\s+(\d+)',pi.stdout)
        print(k,'OK' if ok and pg else 'BAD',pg.group(1) if pg else '')
        if not (ok and pg) and os.path.exists(out): os.remove(out)
