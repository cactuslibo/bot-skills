import csv,json,urllib.request,sys,difflib
for f in ["branchA_papers.csv","branchB_papers.csv"]:
  for r in csv.DictReader(open(f)):
    try:
      m=json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/"+r["DOI"],headers={"User-Agent":"review (mailto:YOUR_EMAIL@example.com)"}),timeout=30))["message"]
      t=(m.get("title") or [""])[0]; y=(m.get("issued",{}).get("date-parts") or [[None]])[0][0]
      au=m.get("author",[{}]); fa=au[0].get("family","?") if au else "?"
      s=difflib.SequenceMatcher(None,t.lower(),r["title"].lower()).ratio()
      print(f[6],r["cite_key"],r["year"],y,fa,len(au),"|",(m.get("container-title") or [""])[0][:40],"| sim%.2f"%s, "" if s>.9 else "TITLE:"+t[:90])
    except Exception as e: print(f[6],r["cite_key"],"ERR",e)
