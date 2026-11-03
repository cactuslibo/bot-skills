import json,urllib.request,urllib.parse,subprocess,os
P={"Mor65":"10.1143/PTP.33.423","Zwa61":"10.1103/PhysRev.124.983","Zwa60":"10.1063/1.1731409","Eva79":"10.1080/00018737900101365","Mar99":"10.1063/1.478705","Asa54":"10.1063/1.1740347","Asa58":"10.1002/pol.1958.1203312618","Der41":"10.1016/0079-6816(93)90013-L","Ver47":"10.1021/j150453a001","Dzy61":"10.1080/00018736100101281","Wei79":"10.1016/0378-4371(79)90223-1","Wil71":"10.1103/PhysRevB.4.3174","Wil74":"10.1016/0370-1573(74)90023-4","Bra09":"10.1126/science.1172046","Hym14":"10.1146/annurev-cellbio-100913-013325","Vic95":"10.1103/PhysRevLett.75.1226","Hoh77":"10.1103/RevModPhys.49.435","She08":"10.1063/1.2992060"}
H={"User-Agent":"Mozilla/5.0 (mailto:bot@example.com)"}
res={}
for k,d in P.items():
  urls=[]
  try:
    j=json.load(urllib.request.urlopen(f"https://api.unpaywall.org/v2/{urllib.parse.quote(d)}?email=bot@example.com",timeout=30))
    urls+=[l.get("url_for_pdf") for l in j.get("oa_locations",[]) if l.get("url_for_pdf")]
  except Exception as e: pass
  try:
    j=json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.openalex.org/works/doi:{d}",headers=H),timeout=30))
    urls+=[l.get("pdf_url") for l in j.get("locations",[]) if l.get("pdf_url") and l.get("is_oa")]
  except Exception: pass
  ok=None
  for u in dict.fromkeys(urls):
    f=f"pdfs/{k}.pdf"
    subprocess.run(["curl","-sL","-m","60","-A",H["User-Agent"],"-o",f,u])
    if os.path.exists(f) and open(f,"rb").read(5)==b"%PDF-" and subprocess.run(["pdfinfo",f],capture_output=True).returncode==0:
      ok=u;break
    if os.path.exists(f): os.remove(f)
  res[k]=dict(doi=d,urls=urls,ok=ok); print(k,ok,len(urls),flush=True)
json.dump(res,open("oa_round2.json","w"),indent=1)
