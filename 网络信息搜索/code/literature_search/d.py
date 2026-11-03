import json,sys,urllib.request,time
for d in open(sys.argv[1]).read().split():
    try:
        m=json.load(urllib.request.urlopen("https://api.crossref.org/works/"+d+"?mailto=YOUR_EMAIL@example.com",timeout=30))["message"]
        print(d,"|",(m.get("issued",{}).get("date-parts") or [[None]])[0][0],"|",(m.get("title") or [""])[0][:100],"|",[a.get("family") for a in m.get("author",[])][:4],"|",(m.get("container-title") or [""])[0][:30])
    except Exception as e: print(d,"ERR",e)
    time.sleep(0.3)
