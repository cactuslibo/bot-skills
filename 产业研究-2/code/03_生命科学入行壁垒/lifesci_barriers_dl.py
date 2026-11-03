import json,re,subprocess,sys
from ids import *
for f in sys.argv[1:]:
    t=open(f).read()
    for m in re.finditer(r'"cite_key":"(\w+)","status":"available","url":"([^"]+)"',t):
        k,u=m.groups(); out=f"pdfs/{ID[k]}.pdf"
        subprocess.run(["curl","-sL","-m","60","-o",out,u]); print(k,ID[k])
