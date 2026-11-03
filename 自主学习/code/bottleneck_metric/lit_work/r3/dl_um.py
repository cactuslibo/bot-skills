import json,re,subprocess,sys,os
src,D=sys.argv[1],sys.argv[2]
t=open(src).read(); t=t[t.index('{'):t.rindex('}')+1]
for r in json.loads(t)["results"]:
    if r.get("status")!="available": print(r["cite_key"],"unavailable"); continue
    f=os.path.join(D,r["cite_key"]+".pdf")
    subprocess.run(["curl","-sL","-m","120","-o",f,r["url"]])
    ok=open(f,'rb').read(5)==b'%PDF-' and subprocess.run(["pdfinfo",f],capture_output=True).returncode==0
    if not ok: os.remove(f)
    print(r["cite_key"],"OK" if ok else "BAD")
