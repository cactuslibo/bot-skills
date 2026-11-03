import re,sys,json
exec(open('/workspace/lifesci_barriers/ids.py').read()); exec(open('/workspace/lifesci_barriers/ids2.py').read())
inc=set(keys)|set(keys2)
seen=set(inc)
import glob,os
if os.path.exists('seen.json'): seen|=set(json.load(open('seen.json')))
for f in sys.argv[1:]:
    t=open(f).read()
    for b in re.split(r'\n(?=\[[A-Za-z]+\d{2}[a-z]{0,3}\] )',t):
        m=re.match(r'\s*\[([A-Za-z]+\d{2}[a-z]{0,3})\] (.*)',b)
        if m:
            k=m.group(1); l=b.split('\n')
            print(f[:7],'INC' if k in inc else ('SEEN' if k in seen else 'NEW'),k,m.group(2)[:105],'|',l[1][:30] if len(l)>1 else '')
