import subprocess,json,sys
from ids2 import *
for f in sys.argv[1:]:
  t=open(f).read(); j=json.loads(t[t.index('{'):t.rindex('}')+1])
  for r in j["results"]:
    k=r["cite_key"]
    if r.get("status")=="available":
        out=f"pdfs/{ID2[k]}.pdf"; subprocess.run(["curl","-sL","-m","90","-o",out,r["url"]])
        print(k,ID2[k],open(out,'rb').read(5))
    else: print(k,r.get("status"))
